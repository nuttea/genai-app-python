'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Bot, User, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import Image from 'next/image';

interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = role === 'user';

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500' : 'bg-purple-500'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
        <div
          className={`max-w-3xl rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-white border border-gray-200 shadow-sm'
          }`}
        >
          {/* Message */}
          <div
            className={`prose prose-sm max-w-none ${
              isUser
                ? 'prose-invert'
                : 'prose-slate prose-headings:text-gray-900 prose-p:text-gray-700'
            }`}
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw, rehypeSanitize]}
              components={{
                // Code blocks with syntax highlighting
                code({ className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || '');
                  const codeContent = String(children).replace(/\n$/, '');
                  const inline = props.inline || !className;

                  return !inline && match ? (
                    <div className="relative group">
                      <SyntaxHighlighter
                        style={vscDarkPlus as any}
                        language={match[1]}
                        PreTag="div"
                        className="!mt-2 !mb-2 !rounded-lg !text-sm"
                      >
                        {codeContent}
                      </SyntaxHighlighter>
                      <button
                        onClick={() => navigator.clipboard.writeText(codeContent)}
                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-700 hover:bg-gray-600 text-white px-2 py-1 rounded text-xs"
                      >
                        Copy
                      </button>
                    </div>
                  ) : (
                    <code
                      className={`${
                        isUser
                          ? 'bg-blue-600 text-blue-100'
                          : 'bg-gray-100 text-pink-600'
                      } px-1.5 py-0.5 rounded text-sm font-mono`}
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                // Images with Next.js Image component
                img({ src, alt }) {
                  if (!src) return null;
                  return (
                    <div className="my-4">
                      <Image
                        src={src}
                        alt={alt || 'Image'}
                        width={600}
                        height={400}
                        className="rounded-lg shadow-lg"
                        style={{ width: 'auto', height: 'auto', maxWidth: '100%' }}
                      />
                    </div>
                  );
                },
                // Links
                a({ href, children }) {
                  return (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`${
                        isUser
                          ? 'text-blue-100 hover:text-white underline'
                          : 'text-blue-600 hover:text-blue-800 underline'
                      }`}
                    >
                      {children}
                    </a>
                  );
                },
                // Tables
                table({ children }) {
                  return (
                    <div className="overflow-x-auto my-4">
                      <table className="min-w-full divide-y divide-gray-200">
                        {children}
                      </table>
                    </div>
                  );
                },
                // Blockquotes
                blockquote({ children }) {
                  return (
                    <blockquote
                      className={`border-l-4 pl-4 my-4 italic ${
                        isUser ? 'border-blue-300' : 'border-gray-300'
                      }`}
                    >
                      {children}
                    </blockquote>
                  );
                },
              }}
            >
              {content}
            </ReactMarkdown>
          </div>

          {/* Timestamp and Actions */}
          <div
            className={`flex items-center justify-between mt-2 pt-2 border-t ${
              isUser ? 'border-blue-400' : 'border-gray-200'
            }`}
          >
            {timestamp && (
              <span
                className={`text-xs ${isUser ? 'text-blue-100' : 'text-gray-500'}`}
              >
                {timestamp}
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className={`ml-auto ${
                isUser ? 'hover:bg-blue-600 text-blue-100' : 'hover:bg-gray-100'
              }`}
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 mr-1" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3 mr-1" />
                  Copy
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

