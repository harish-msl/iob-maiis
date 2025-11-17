'use client';

import React, { useState } from 'react';
import {
  Copy,
  Check,
  Download,
  Search,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Eye,
  EyeOff,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils/cn';

interface OCRViewerProps {
  text: string;
  filename?: string;
  metadata?: {
    pages?: number;
    word_count?: number;
    confidence?: number;
    language?: string;
    [key: string]: any;
  };
  className?: string;
}

export function OCRViewer({ text, filename, metadata, className }: OCRViewerProps) {
  const [copied, setCopied] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [fontSize, setFontSize] = useState(14);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showLineNumbers, setShowLineNumbers] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename || 'document'}_ocr.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts
      .map((part, index) =>
        part.toLowerCase() === query.toLowerCase()
          ? `<mark class="bg-yellow-200 dark:bg-yellow-800">${part}</mark>`
          : part
      )
      .join('');
  };

  const lines = text.split('\n');
  const displayText = searchQuery ? highlightText(text, searchQuery) : text;

  const matchCount = searchQuery
    ? (text.match(new RegExp(searchQuery, 'gi')) || []).length
    : 0;

  return (
    <Card className={cn('flex flex-col overflow-hidden', className)}>
      {/* Header */}
      <div className="border-b bg-muted/50 p-4">
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold">OCR Extracted Text</h3>
            {filename && (
              <p className="text-sm text-muted-foreground">{filename}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowLineNumbers(!showLineNumbers)}
              title={showLineNumbers ? 'Hide line numbers' : 'Show line numbers'}
            >
              {showLineNumbers ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFontSize(Math.max(10, fontSize - 2))}
              disabled={fontSize <= 10}
              title="Decrease font size"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFontSize(Math.min(24, fontSize + 2))}
              disabled={fontSize >= 24}
              title="Increase font size"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? 'Collapse' : 'Expand'}
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={handleCopy}>
              {copied ? (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Copy
                </>
              )}
            </Button>
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="mr-2 h-4 w-4" />
              Download
            </Button>
          </div>
        </div>

        {/* Metadata */}
        {metadata && (
          <div className="mb-4 flex flex-wrap gap-2">
            {metadata.word_count !== undefined && (
              <Badge variant="secondary">
                {metadata.word_count.toLocaleString()} words
              </Badge>
            )}
            {metadata.pages !== undefined && (
              <Badge variant="secondary">
                {metadata.pages} page{metadata.pages !== 1 ? 's' : ''}
              </Badge>
            )}
            {metadata.confidence !== undefined && (
              <Badge
                variant="outline"
                className={cn(
                  metadata.confidence > 0.9 && 'border-green-500 text-green-500',
                  metadata.confidence > 0.7 &&
                    metadata.confidence <= 0.9 &&
                    'border-yellow-500 text-yellow-500',
                  metadata.confidence <= 0.7 && 'border-orange-500 text-orange-500'
                )}
              >
                {(metadata.confidence * 100).toFixed(0)}% confidence
              </Badge>
            )}
            {metadata.language && (
              <Badge variant="secondary">{metadata.language}</Badge>
            )}
          </div>
        )}

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search in text..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
          {searchQuery && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <Badge variant="secondary" className="text-xs">
                {matchCount} match{matchCount !== 1 ? 'es' : ''}
              </Badge>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div
        className={cn(
          'flex-1 overflow-auto p-6',
          isExpanded && 'max-h-[600px]'
        )}
      >
        {text ? (
          <div className="relative">
            {showLineNumbers ? (
              <div className="flex gap-4">
                {/* Line numbers */}
                <div className="select-none text-right text-muted-foreground">
                  {lines.map((_, index) => (
                    <div
                      key={index}
                      className="leading-relaxed"
                      style={{ fontSize: `${fontSize}px` }}
                    >
                      {index + 1}
                    </div>
                  ))}
                </div>
                {/* Text content */}
                <div className="flex-1">
                  <pre
                    className="whitespace-pre-wrap break-words font-mono leading-relaxed"
                    style={{ fontSize: `${fontSize}px` }}
                    dangerouslySetInnerHTML={{ __html: displayText }}
                  />
                </div>
              </div>
            ) : (
              <pre
                className="whitespace-pre-wrap break-words font-mono leading-relaxed"
                style={{ fontSize: `${fontSize}px` }}
                dangerouslySetInnerHTML={{ __html: displayText }}
              />
            )}
          </div>
        ) : (
          <div className="flex h-full items-center justify-center text-center">
            <div className="max-w-md">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                <Search className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">No Text Available</h3>
              <p className="text-sm text-muted-foreground">
                OCR processing hasn't been performed on this document yet, or no
                text was detected.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      {text && (
        <div className="border-t bg-muted/50 p-3 text-center text-sm text-muted-foreground">
          {lines.length} line{lines.length !== 1 ? 's' : ''} •{' '}
          {text.split(/\s+/).filter(Boolean).length} word
          {text.split(/\s+/).filter(Boolean).length !== 1 ? 's' : ''} •{' '}
          {text.length} character{text.length !== 1 ? 's' : ''}
        </div>
      )}
    </Card>
  );
}
