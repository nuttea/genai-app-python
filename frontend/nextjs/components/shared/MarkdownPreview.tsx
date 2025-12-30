'use client';

import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { cn } from '@/lib/utils';

interface MarkdownPreviewProps {
  content: string;
  className?: string;
}

export function MarkdownPreview({ content, className }: MarkdownPreviewProps) {
  return (
    <div
      className={cn(
        'prose prose-slate max-w-none',
        // Headings
        'prose-headings:text-foreground prose-headings:font-bold',
        'prose-h1:text-3xl prose-h1:mt-8 prose-h1:mb-4',
        'prose-h2:text-2xl prose-h2:mt-6 prose-h2:mb-3',
        'prose-h3:text-xl prose-h3:mt-5 prose-h3:mb-2',
        // Paragraphs & Text
        'prose-p:text-foreground prose-p:leading-7 prose-p:my-3',
        'prose-strong:text-foreground prose-strong:font-semibold',
        // Links
        'prose-a:text-purple-600 prose-a:no-underline hover:prose-a:underline',
        // Code
        'prose-code:text-purple-600 prose-code:bg-purple-50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm',
        'prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:my-4 prose-pre:p-4',
        // Quotes
        'prose-blockquote:border-l-purple-500 prose-blockquote:text-muted-foreground prose-blockquote:my-4',
        // Lists
        'prose-ul:text-foreground prose-ul:my-3 prose-ul:list-disc',
        'prose-ol:text-foreground prose-ol:my-3',
        'prose-li:text-foreground prose-li:my-1.5 prose-li:leading-relaxed',
        // Tables
        'prose-table:my-4',
        'prose-th:text-left prose-th:font-semibold',
        'prose-td:text-foreground',
        className
      )}
    >
      <ReactMarkdown
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={vscDarkPlus as any}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

