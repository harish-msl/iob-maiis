'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { Bot, User, Copy, Check, FileText, ExternalLink } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '@/lib/types/chat';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils/cn';

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
  className?: string;
}

export function ChatMessage({ message, isStreaming, className }: ChatMessageProps) {
  const [copied, setCopied] = React.useState(false);
  const [expandedSources, setExpandedSources] = React.useState(false);

  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy message:', error);
    }
  };

  return (
    <div
      className={cn(
        'group flex gap-4 px-4 py-6 transition-colors hover:bg-muted/50',
        isUser && 'bg-muted/30',
        className
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg',
          isUser && 'bg-primary text-primary-foreground',
          isAssistant && 'bg-gradient-to-br from-purple-500 to-blue-500 text-white'
        )}
      >
        {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
      </div>

      {/* Message Content */}
      <div className="flex-1 space-y-3 overflow-hidden">
        {/* Header with role and timestamp */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          {message.timestamp && (
            <span className="text-xs text-muted-foreground">
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          )}
          {isStreaming && (
            <Badge variant="outline" className="ml-2 animate-pulse">
              <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-green-500" />
              Typing...
            </Badge>
          )}
        </div>

        {/* Message text with markdown */}
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const language = match ? match[1] : '';

                return !inline && language ? (
                  <div className="relative my-4">
                    <div className="absolute right-2 top-2 z-10">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          navigator.clipboard.writeText(String(children).trim());
                        }}
                        className="h-7 text-xs"
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={language}
                      PreTag="div"
                      customStyle={{
                        margin: 0,
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                      }}
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  </div>
                ) : (
                  <code
                    className={cn(
                      'rounded bg-muted px-1.5 py-0.5 font-mono text-sm',
                      className
                    )}
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
              a({ node, children, href, ...props }) {
                return (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary underline-offset-4 hover:underline"
                    {...props}
                  >
                    {children}
                    <ExternalLink className="ml-1 inline h-3 w-3" />
                  </a>
                );
              },
              table({ node, children, ...props }) {
                return (
                  <div className="my-4 overflow-x-auto">
                    <table className="min-w-full divide-y divide-border" {...props}>
                      {children}
                    </table>
                  </div>
                );
              },
              th({ node, children, ...props }) {
                return (
                  <th
                    className="bg-muted px-4 py-2 text-left text-sm font-semibold"
                    {...props}
                  >
                    {children}
                  </th>
                );
              },
              td({ node, children, ...props }) {
                return (
                  <td className="px-4 py-2 text-sm" {...props}>
                    {children}
                  </td>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.attachments.map((attachment, index) => (
              <Card
                key={index}
                className="flex items-center gap-2 px-3 py-2 text-sm"
              >
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">{attachment.filename}</span>
                <Badge variant="secondary" className="text-xs">
                  {(attachment.size / 1024).toFixed(1)} KB
                </Badge>
              </Card>
            ))}
          </div>
        )}

        {/* RAG Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 space-y-2">
            <button
              onClick={() => setExpandedSources(!expandedSources)}
              className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              <FileText className="h-4 w-4" />
              <span>
                {message.sources.length} source{message.sources.length > 1 ? 's' : ''}{' '}
                referenced
              </span>
              <svg
                className={cn(
                  'h-4 w-4 transition-transform',
                  expandedSources && 'rotate-180'
                )}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {expandedSources && (
              <div className="space-y-2">
                {message.sources.map((source, index) => (
                  <Card
                    key={index}
                    className="p-3 transition-colors hover:bg-muted/50"
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" className="text-xs">
                              Source {index + 1}
                            </Badge>
                            {source.score !== undefined && (
                              <Badge
                                variant="outline"
                                className={cn(
                                  'text-xs',
                                  source.score > 0.8 && 'border-green-500 text-green-500',
                                  source.score > 0.6 &&
                                    source.score <= 0.8 &&
                                    'border-yellow-500 text-yellow-500',
                                  source.score <= 0.6 && 'border-orange-500 text-orange-500'
                                )}
                              >
                                {(source.score * 100).toFixed(0)}% match
                              </Badge>
                            )}
                          </div>
                          {source.metadata?.filename && (
                            <p className="text-sm font-medium">
                              {source.metadata.filename}
                            </p>
                          )}
                        </div>
                      </div>

                      {source.content && (
                        <p className="text-sm text-muted-foreground line-clamp-3">
                          {source.content}
                        </p>
                      )}

                      {source.metadata && (
                        <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                          {source.metadata.page && (
                            <span>Page {source.metadata.page}</span>
                          )}
                          {source.metadata.chunk_index !== undefined && (
                            <span>Chunk {source.metadata.chunk_index}</span>
                          )}
                          {source.metadata.doc_type && (
                            <Badge variant="outline" className="text-xs">
                              {source.metadata.doc_type}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Copy button (visible on hover) */}
        {!isUser && (
          <div className="opacity-0 transition-opacity group-hover:opacity-100">
            <Button
              size="sm"
              variant="ghost"
              onClick={handleCopy}
              className="h-8 gap-2 text-xs"
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  Copy
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
