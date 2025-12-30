'use client';

import { useState, useRef, useEffect } from 'react';
import { datadogRum } from '@datadog/browser-rum';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { FileUpload } from '@/components/shared/FileUpload';
import { MarkdownPreview } from '@/components/shared/MarkdownPreview';
import { contentCreatorApi } from '@/lib/api/contentCreator';
import { useToast } from '@/hooks/useToast';
import {
  Send,
  Bot,
  User,
  FileText,
  Upload,
  Sparkles,
  Download,
  Copy,
  Check,
  X,
} from 'lucide-react';
import { copyToClipboard, downloadBlob } from '@/lib/utils';

// Message types
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  streaming?: boolean;
}

// Workflow states
type WorkflowStep =
  | 'welcome'
  | 'choose_content_type'
  | 'blog_planning'
  | 'blog_outline_review'
  | 'blog_writing'
  | 'blog_draft_review'
  | 'blog_editing'
  | 'video_writing'
  | 'video_review'
  | 'social_writing'
  | 'social_review'
  | 'export';

interface WorkflowState {
  step: WorkflowStep;
  contentType: 'blog' | 'video' | 'social' | null;
  uploadedFiles: Array<{ filename: string; text?: string }>;
  outline?: string;
  draft?: string;
  finalContent?: string;
}

/**
 * Get Datadog RUM session ID for ADK session tracking
 * Falls back to timestamp-based ID if Datadog RUM is not initialized
 */
function getDatadogSessionId(): string {
  try {
    const internalContext = datadogRum.getInternalContext();
    if (internalContext?.session_id) {
      return `dd_${internalContext.session_id}`;
    }
  } catch (error) {
    console.warn('Datadog RUM not initialized, using fallback session ID');
  }
  return `session_${Date.now()}`;
}

export default function InteractiveContentCreatorPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [workflow, setWorkflow] = useState<WorkflowState>({
    step: 'welcome',
    contentType: null,
    uploadedFiles: [],
  });
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [sessionId, setSessionId] = useState<string>(getDatadogSessionId());

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize Datadog RUM session ID
  useEffect(() => {
    // Wait a bit for Datadog RUM to initialize, then get the session ID
    const timer = setTimeout(() => {
      const ddSessionId = getDatadogSessionId();
      setSessionId(ddSessionId);
      console.log('ADK Session ID linked to Datadog RUM:', ddSessionId);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  // Initialize with welcome message
  useEffect(() => {
    addMessage(
      'assistant',
      `👋 Welcome to Datadog Content Creator!

I'm your AI assistant specializing in creating content about Datadog observability products.

I can help you create:
📝 **Blog posts** - Long-form technical articles
🎥 **Video scripts** - 60-second shorts for YouTube/TikTok/Reels
📱 **Social media posts** - Platform-specific content for LinkedIn/Twitter/Instagram

**Optional:** If you have any files (videos, images, documents) you'd like me to analyze, upload them now. Otherwise, just tell me what type of content you'd like to create!

What would you like to work on today?`
    );
  }, []);

  const addMessage = (
    role: 'user' | 'assistant' | 'system',
    content: string,
    streaming = false
  ) => {
    const newMessage: Message = {
      id: `msg_${Date.now()}_${Math.random()}`,
      role,
      content,
      timestamp: new Date(),
      streaming,
    };
    setMessages((prev: Message[]) => [...prev, newMessage]);
    return newMessage.id;
  };

  const updateLastMessage = (content: string, append: boolean = false) => {
    setMessages((prev: Message[]) => {
      const updated = [...prev];
      if (updated.length > 0) {
        if (append) {
          updated[updated.length - 1].content += content;
        } else {
          // Replace content (for ADK which sends full message each time)
          updated[updated.length - 1].content = content;
        }
      }
      return updated;
    });
  };

  const finalizeLastMessage = () => {
    setMessages((prev: Message[]) => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1].streaming = false;
      }
      return updated;
    });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    addMessage('user', userMessage);

    // Call ADK agent with streaming
    await callAgent(userMessage);
  };

  const callAgent = async (userMessage: string) => {
    setIsStreaming(true);

    try {
      // Create a new message for streaming response
      const messageId = addMessage('assistant', '', true);

      // Prepare ADK request
      const appName = 'content_creator_agent';
      const userId = 'user_nextjs';

      // Create session if needed
      await contentCreatorApi._createSession(appName, userId, sessionId);

      // Call /run_sse with streaming
      const apiUrl = 'http://localhost:8002'; // TODO: Use env var
      const response = await fetch(`${apiUrl}/run_sse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          appName,
          userId,
          sessionId,
          newMessage: {
            role: 'user',
            parts: [{ text: userMessage }],
          },
          streaming: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Process SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let lastContent = ''; // Track last content to detect changes

      if (!reader) {
        throw new Error('No response body reader');
      }

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // SSE events are separated by double newlines
        const events = buffer.split('\n\n');
        // Keep the last potentially incomplete event in the buffer
        buffer = events.pop() || '';

        for (const event of events) {
          // Each event can have multiple lines
          const lines = event.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.slice(6).trim();

              // Skip empty data lines
              if (!jsonStr) continue;

              try {
                const data = JSON.parse(jsonStr);

                // ADK sends complete message content in each event
                // We need to replace (not append) the message content
                if (data.content?.parts) {
                  for (const part of data.content.parts) {
                    if (part.text && part.text !== lastContent) {
                      // Only update if content changed
                      updateLastMessage(part.text, false); // false = replace
                      lastContent = part.text;
                    }
                  }
                }
              } catch (err) {
                // Log the problematic JSON for debugging
                console.error('Error parsing SSE JSON:', err);
                console.error('Problematic JSON string:', jsonStr.substring(0, 200));
                // Continue processing other lines instead of breaking
              }
            }
          }
        }
      }

      finalizeLastMessage();
    } catch (error) {
      console.error('Error calling agent:', error);
      finalizeLastMessage();
      addMessage(
        'system',
        `⚠️ Error: ${error instanceof Error ? error.message : 'Failed to get response'}`
      );
      toast.error('Failed to get response from agent');
    } finally {
      setIsStreaming(false);
    }
  };

  const handleFilesSelected = async (files: File[]) => {
    try {
      toast.loading(`Uploading ${files.length} file(s)...`);

      const uploadPromises = files.map((file) => contentCreatorApi.uploadFile(file));
      const results = await Promise.all(uploadPromises);

      const fileInfos = results.map((r) => ({
        filename: r.file.filename,
        text: r.file.extracted_text || undefined,
      }));

      setWorkflow((prev: WorkflowState) => ({
        ...prev,
        uploadedFiles: [...prev.uploadedFiles, ...fileInfos],
      }));

      toast.success(`Uploaded ${fileInfos.length} file(s) successfully`);

      // Notify agent about uploaded files
      const fileList = fileInfos.map((f) => f.filename).join(', ');
      await callAgent(`I've uploaded these files: ${fileList}. Please analyze them.`);

      setShowFileUpload(false);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload files');
    }
  };

  const handleQuickAction = async (action: string, value?: string) => {
    switch (action) {
      case 'blog':
        await callAgent('I want to create a blog post');
        break;
      case 'video':
        await callAgent('I want to create a video script');
        break;
      case 'social':
        await callAgent('I want to create social media posts');
        break;
      case 'approve':
        await callAgent('Yes, I approve. Please proceed.');
        break;
      case 'reject':
        await callAgent('No, please revise it.');
        break;
      case 'upload_files':
        setShowFileUpload(true);
        break;
      default:
        if (value) {
          await callAgent(value);
        }
    }
  };

  const handleCopyContent = (content: string) => {
    copyToClipboard(content);
    toast.success('Content copied to clipboard');
  };

  const handleDownloadContent = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    downloadBlob(blob, filename);
    toast.success('Content downloaded');
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Interactive Content Creator" />

        <main className="flex-1 overflow-hidden flex flex-col">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <div className="max-w-4xl mx-auto space-y-4">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onCopy={handleCopyContent}
                  onDownload={handleDownloadContent}
                />
              ))}

              {isStreaming && (
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Bot className="w-5 h-5 animate-pulse" />
                  <span className="text-sm">Agent is thinking...</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Quick Actions Bar */}
          {!isStreaming && (
            <div className="border-t border-border bg-card p-3">
              <div className="max-w-4xl mx-auto flex flex-wrap gap-2">
                <Button size="sm" variant="outline" onClick={() => handleQuickAction('blog')}>
                  <FileText className="w-4 h-4 mr-1" />
                  Blog Post
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleQuickAction('video')}>
                  <Sparkles className="w-4 h-4 mr-1" />
                  Video Script
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleQuickAction('social')}>
                  <Sparkles className="w-4 h-4 mr-1" />
                  Social Media
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleQuickAction('upload_files')}
                >
                  <Upload className="w-4 h-4 mr-1" />
                  Upload Files
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleQuickAction('approve')}>
                  <Check className="w-4 h-4 mr-1" />
                  Approve
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleQuickAction('reject')}>
                  <X className="w-4 h-4 mr-1" />
                  Revise
                </Button>
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t border-border bg-background p-4">
            <div className="max-w-4xl mx-auto">
              {showFileUpload ? (
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold">Upload Files</h3>
                      <Button size="sm" variant="ghost" onClick={() => setShowFileUpload(false)}>
                        Cancel
                      </Button>
                    </div>
                    <FileUpload onFilesSelected={handleFilesSelected} maxFiles={5} />
                  </CardContent>
                </Card>
              ) : (
                <div className="flex space-x-2">
                  <Textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="Type your message... (Shift+Enter for new line)"
                    className="flex-1 min-h-[60px] resize-none"
                    disabled={isStreaming}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={isStreaming || !inputValue.trim()}
                    className="px-6"
                  >
                    <Send className="w-5 h-5" />
                  </Button>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

// Chat Message Component
interface ChatMessageProps {
  message: Message;
  onCopy?: (content: string) => void;
  onDownload?: (content: string, filename: string) => void;
}

function ChatMessage({ message, onCopy, onDownload }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`flex space-x-3 max-w-[85%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}
      >
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isUser
              ? 'bg-purple-600 text-white'
              : isSystem
                ? 'bg-yellow-100 text-yellow-600'
                : 'bg-blue-100 text-blue-600'
          }`}
        >
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </div>

        {/* Message Content */}
        <div className="flex-1">
          <div
            className={`rounded-lg p-4 ${
              isUser
                ? 'bg-purple-600 text-white'
                : isSystem
                  ? 'bg-yellow-50 border border-yellow-200 text-yellow-900'
                  : 'bg-card border border-border'
            }`}
          >
            {message.streaming ? (
              <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:mt-6 prose-headings:mb-3 prose-p:my-3 prose-ul:my-3 prose-li:my-1">
                {message.content}
                <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
              </div>
            ) : message.content.includes('```') || message.content.includes('#') ? (
              <div
                className={`prose prose-sm dark:prose-invert max-w-none ${
                  isUser ? 'prose-invert' : ''
                } prose-headings:mt-6 prose-headings:mb-3 prose-p:my-3 prose-ul:my-3 prose-ol:my-3 prose-li:my-1.5 prose-code:text-sm prose-pre:my-4`}
              >
                <MarkdownPreview content={message.content} />
              </div>
            ) : (
              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
            )}
          </div>

          {/* Actions */}
          {!isUser && !isSystem && !message.streaming && message.content.length > 100 && (
            <div className="flex space-x-2 mt-2">
              <Button size="sm" variant="ghost" onClick={() => onCopy?.(message.content)}>
                <Copy className="w-4 h-4 mr-1" />
                Copy
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onDownload?.(message.content, `content_${Date.now()}.md`)}
              >
                <Download className="w-4 h-4 mr-1" />
                Download
              </Button>
            </div>
          )}

          {/* Timestamp */}
          <p className="text-xs text-muted-foreground mt-1">
            {message.timestamp.toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
}
