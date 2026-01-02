'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { datadogRum } from '@datadog/browser-rum';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ChatMessage } from '@/components/shared/ChatMessage';
import { FileUpload } from '@/components/shared/FileUpload';
import { contentCreatorApi } from '@/lib/api/contentCreator';
import { API_CONFIG } from '@/lib/constants/config';
import { useToast } from '@/hooks/useToast';
import {
  Send,
  FileText,
  Upload,
  Sparkles,
  Loader2,
  Video,
  Share2,
} from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export default function InteractiveContentCreatorV2Page() {
  const { showToast } = useToast();
  const [sessionId, setSessionId] = useState<string>(() => {
    const rumSessionId = datadogRum.getInternalContext()?.session_id;
    return rumSessionId ? `dd_${rumSessionId}` : `session_${Date.now()}`;
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isMountedRef = useRef(true);
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Log session ID to Datadog on mount
  useEffect(() => {
    console.log('ADK Session ID linked to Datadog RUM:', sessionId);
  }, [sessionId]);

  // Quick action handlers - populate input with prompt
  const handleQuickAction = (action: string) => {
    let prompt = '';
    switch (action) {
      case 'blog':
        prompt =
          'I want to create a blog post about Datadog observability features. Please help me plan it.';
        break;
      case 'video':
        prompt =
          'I need a 60-second video script about Datadog APM for YouTube Shorts.';
        break;
      case 'social':
        prompt =
          'Help me create social media posts about Datadog RUM for LinkedIn and Twitter.';
        break;
    }

    if (prompt) {
      setInput(prompt);
    }
  };

  // File upload handler
  const handleFileSelect = async (files: File[]) => {
    try {
      const uploadPromises = files.map((file) =>
        contentCreatorApi.uploadFile(file)
      );
      const results = await Promise.all(uploadPromises);

      const fileIds = results
        .map((r) => r.file_id)
        .filter((id): id is string => !!id);
      setUploadedFiles((prev) => [...prev, ...fileIds]);

      showToast(`${files.length} file(s) uploaded successfully`, 'success');
      setShowFileUpload(false);
    } catch (error) {
      console.error('File upload error:', error);
      showToast('Failed to upload files', 'error');
    }
  };

  // Throttled update function to prevent excessive re-renders
  const throttledUpdate = useCallback(
    (messageId: string, newContent: string) => {
      if (!isMountedRef.current) return;

      // Clear any pending update
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }

      // Use requestAnimationFrame for smooth updates
      requestAnimationFrame(() => {
        if (!isMountedRef.current) return;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === messageId ? { ...msg, content: newContent } : msg
          )
        );
      });
    },
    []
  );

  // Call ADK agent with optimized streaming
  const callAgent = useCallback(
    async (userMessage: string) => {
      if (!userMessage.trim() || isLoading) return;

      // Add user message
      const userMsg: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: userMessage,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setInput('');
      setIsLoading(true);

      // Create AbortController for cleanup
      const abortController = new AbortController();

      try {
        // Create session
        await contentCreatorApi._createSession(
          'content_creator_agent',
          'user_nextjs',
          sessionId
        );

        // Call streaming API
        const response = await fetch(
          `${API_CONFIG.contentCreator.baseUrl}/run_sse`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              appName: 'content_creator_agent',
              userId: 'user_nextjs',
              sessionId,
              newMessage: {
                role: 'user',
                parts: [{ text: userMessage }],
              },
              streaming: true,
            }),
            signal: abortController.signal,
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let assistantMessageId: string | null = null;
        let lastText = ''; // Track last text to avoid duplicate updates
        let lastUpdateTime = 0;
        const UPDATE_THROTTLE_MS = 50; // Throttle updates to max 20/sec

        while (true) {
          const { done, value } = await reader!.read();
          if (done) {
            // Final update to ensure we have the complete text
            if (assistantMessageId && lastText) {
              throttledUpdate(assistantMessageId, lastText);
            }
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonString = line.slice(6).trim();
              if (jsonString) {
                try {
                  const data = JSON.parse(jsonString);
                  if (data.content?.parts) {
                    for (const part of data.content.parts) {
                      if (part.text) {
                        const fullText = part.text;

                        // Skip if text hasn't changed (avoid duplicate renders)
                        if (fullText === lastText) {
                          continue;
                        }
                        lastText = fullText;

                        const now = Date.now();
                        const timeSinceLastUpdate = now - lastUpdateTime;

                        if (!assistantMessageId) {
                          // Create new assistant message
                          assistantMessageId = `assistant-${Date.now()}`;
                          setMessages((prev) => [
                            ...prev,
                            {
                              id: assistantMessageId!,
                              role: 'assistant',
                              content: fullText,
                              createdAt: new Date().toISOString(),
                            },
                          ]);
                          lastUpdateTime = now;
                        } else if (timeSinceLastUpdate >= UPDATE_THROTTLE_MS) {
                          // Throttled update: only update if enough time has passed
                          throttledUpdate(assistantMessageId, fullText);
                          lastUpdateTime = now;
                        }
                        // If throttled, the final update after stream ends will catch it
                      }
                    }
                  }
                } catch (e) {
                  console.error('Error parsing SSE:', e);
                }
              }
            }
          }
        }
      } catch (error) {
        // Ignore abort errors (cleanup)
        if (error instanceof Error && error.name === 'AbortError') {
          return;
        }
        console.error('Error calling agent:', error);
        if (isMountedRef.current) {
          showToast(
            error instanceof Error ? error.message : 'Failed to get response',
            'error'
          );
        }
      } finally {
        if (isMountedRef.current) {
          setIsLoading(false);
        }
      }

      // Cleanup function
      return () => {
        abortController.abort();
      };
    },
    [isLoading, sessionId, throttledUpdate, showToast]
  );

  // Handle form submission
  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;
    callAgent(input);
  };

  // Handle Enter key (Shift+Enter for new line)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim()) {
        callAgent(input);
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <Header title="Interactive Content Creator (Vercel AI SDK)" />

        <main className="flex-1 overflow-hidden flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
            {/* Welcome Message */}
            {messages.length === 0 && (
              <div className="max-w-3xl mx-auto">
                <div className="bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl p-8 text-white shadow-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <Sparkles className="w-8 h-8" />
                    <h2 className="text-2xl font-bold">
                      Welcome to Datadog Content Creator!
                    </h2>
                  </div>
                  <p className="text-lg leading-relaxed mb-6">
                    I'm your AI assistant specializing in creating content about
                    Datadog observability products. I can help you create:
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                      <FileText className="w-6 h-6 mb-2" />
                      <h3 className="font-semibold mb-1">Blog posts</h3>
                      <p className="text-sm opacity-90">
                        Long-form technical articles
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                      <Video className="w-6 h-6 mb-2" />
                      <h3 className="font-semibold mb-1">Video scripts</h3>
                      <p className="text-sm opacity-90">
                        60-second shorts for YouTube/TikTok/Reels
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                      <Share2 className="w-6 h-6 mb-2" />
                      <h3 className="font-semibold mb-1">Social media posts</h3>
                      <p className="text-sm opacity-90">
                        Platform-specific content
                      </p>
                    </div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button
                    onClick={() => handleQuickAction('blog')}
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-start gap-2 hover:bg-blue-50 hover:border-blue-300"
                  >
                    <FileText className="w-6 h-6 text-blue-600" />
                    <div className="text-left">
                      <div className="font-semibold">Blog Post</div>
                      <div className="text-xs text-gray-500">
                        Create technical articles
                      </div>
                    </div>
                  </Button>

                  <Button
                    onClick={() => handleQuickAction('video')}
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-start gap-2 hover:bg-purple-50 hover:border-purple-300"
                  >
                    <Video className="w-6 h-6 text-purple-600" />
                    <div className="text-left">
                      <div className="font-semibold">Video Script</div>
                      <div className="text-xs text-gray-500">
                        60-second video content
                      </div>
                    </div>
                  </Button>

                  <Button
                    onClick={() => handleQuickAction('social')}
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-start gap-2 hover:bg-green-50 hover:border-green-300"
                  >
                    <Share2 className="w-6 h-6 text-green-600" />
                    <div className="text-left">
                      <div className="font-semibold">Social Media</div>
                      <div className="text-xs text-gray-500">
                        Multi-platform posts
                      </div>
                    </div>
                  </Button>
                </div>
              </div>
            )}

            {/* Chat Messages */}
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                role={message.role}
                content={message.content}
                timestamp={new Date().toLocaleTimeString()}
              />
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                </div>
                <div className="flex-1">
                  <div className="max-w-3xl bg-white border border-gray-200 rounded-2xl px-4 py-3">
                    <p className="text-gray-500">Agent is thinking...</p>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t bg-white px-4 py-4">
            <div className="max-w-4xl mx-auto">
              {/* Uploaded Files */}
              {uploadedFiles.length > 0 && (
                <div className="mb-3 flex flex-wrap gap-2">
                  {uploadedFiles.map((fileId, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm"
                    >
                      <FileText className="w-3 h-3" />
                      File {idx + 1}
                    </span>
                  ))}
                </div>
              )}

              {/* Quick Actions Bar */}
              <div className="flex gap-2 mb-3">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFileUpload(!showFileUpload)}
                >
                  <Upload className="w-4 h-4 mr-1" />
                  Upload Files
                </Button>
              </div>

              {/* File Upload */}
              {showFileUpload && (
                <div className="mb-3">
                  <FileUpload
                    onFilesSelected={handleFileSelect}
                    maxFiles={10}
                    maxSizeMB={500}
                  />
                </div>
              )}

              {/* Input Form */}
              <form onSubmit={onSubmit} className="flex gap-2">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message... (Shift+Enter for new line)"
                  className="flex-1 min-h-[60px] max-h-[200px] resize-none"
                  disabled={isLoading}
                />
                <Button type="submit" disabled={isLoading || !input.trim()}>
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </form>

              <p className="text-xs text-gray-500 mt-2">
                Press <kbd className="px-1 py-0.5 bg-gray-100 rounded">Enter</kbd>{' '}
                to send, <kbd className="px-1 py-0.5 bg-gray-100 rounded">Shift+Enter</kbd>{' '}
                for new line
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

