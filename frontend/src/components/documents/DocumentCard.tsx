'use client';

import React, { useState } from 'react';
import {
  FileText,
  Image,
  File,
  FileSpreadsheet,
  Download,
  Trash2,
  Eye,
  RefreshCw,
  MoreVertical,
  Calendar,
  FileType,
  HardDrive,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu';
import { cn } from '@/lib/utils/cn';
import { formatDate } from '@/lib/utils/format';

interface DocumentCardProps {
  document: {
    id: string;
    filename: string;
    file_type: string;
    file_size: number;
    upload_date: string;
    status: 'uploaded' | 'processing' | 'processed' | 'error';
    ocr_text?: string;
    metadata?: {
      pages?: number;
      word_count?: number;
      [key: string]: any;
    };
  };
  onView?: (documentId: string) => void;
  onDownload?: (documentId: string) => void;
  onDelete?: (documentId: string) => void;
  onProcessOCR?: (documentId: string) => void;
  onIngest?: (documentId: string) => void;
  className?: string;
}

export function DocumentCard({
  document,
  onView,
  onDownload,
  onDelete,
  onProcessOCR,
  onIngest,
  className,
}: DocumentCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const getFileIcon = (fileType: string) => {
    const type = fileType.toLowerCase();
    if (type.includes('pdf')) {
      return <FileText className="h-10 w-10 text-red-500" />;
    }
    if (type.includes('image')) {
      return <Image className="h-10 w-10 text-purple-500" />;
    }
    if (type.includes('word') || type.includes('document')) {
      return <FileText className="h-10 w-10 text-blue-500" />;
    }
    if (type.includes('excel') || type.includes('spreadsheet')) {
      return <FileSpreadsheet className="h-10 w-10 text-green-500" />;
    }
    return <File className="h-10 w-10 text-gray-500" />;
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'uploaded':
        return <Badge variant="secondary">Uploaded</Badge>;
      case 'processing':
        return (
          <Badge variant="outline" className="border-blue-500 text-blue-500">
            <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
            Processing
          </Badge>
        );
      case 'processed':
        return <Badge variant="default">Processed</Badge>;
      case 'error':
        return (
          <Badge variant="outline" className="border-red-500 text-red-500">
            Error
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const handleDelete = async () => {
    if (!onDelete) return;

    if (window.confirm(`Are you sure you want to delete "${document.filename}"?`)) {
      setIsDeleting(true);
      try {
        await onDelete(document.id);
      } catch (error) {
        console.error('Delete failed:', error);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const handleProcessOCR = async () => {
    if (!onProcessOCR) return;

    setIsProcessing(true);
    try {
      await onProcessOCR(document.id);
    } catch (error) {
      console.error('OCR processing failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card
      className={cn(
        'group relative overflow-hidden transition-all hover:shadow-lg',
        onView && 'cursor-pointer',
        className
      )}
      onClick={() => onView?.(document.id)}
    >
      <div className="p-6">
        {/* Header */}
        <div className="mb-4 flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-muted">
              {getFileIcon(document.file_type)}
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="mb-1 truncate font-semibold" title={document.filename}>
                {document.filename}
              </h3>
              <div className="flex flex-wrap items-center gap-2">
                {getStatusBadge(document.status)}
                <Badge variant="outline" className="text-xs">
                  {document.file_type}
                </Badge>
              </div>
            </div>
          </div>

          {/* Actions Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 opacity-0 transition-opacity group-hover:opacity-100"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {onView && (
                <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onView(document.id); }}>
                  <Eye className="mr-2 h-4 w-4" />
                  View
                </DropdownMenuItem>
              )}
              {onDownload && (
                <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onDownload(document.id); }}>
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </DropdownMenuItem>
              )}
              {onProcessOCR && document.status === 'uploaded' && (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    handleProcessOCR();
                  }}
                  disabled={isProcessing}
                >
                  <RefreshCw className={cn('mr-2 h-4 w-4', isProcessing && 'animate-spin')} />
                  Process OCR
                </DropdownMenuItem>
              )}
              {onIngest && document.status === 'processed' && (
                <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onIngest(document.id); }}>
                  <HardDrive className="mr-2 h-4 w-4" />
                  Ingest to Vector DB
                </DropdownMenuItem>
              )}
              {onDelete && (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete();
                  }}
                  disabled={isDeleting}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Metadata */}
        <div className="space-y-3">
          {/* File Info */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <HardDrive className="h-4 w-4" />
              <span>{formatFileSize(document.file_size)}</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>{formatDate(document.upload_date, 'short')}</span>
            </div>
          </div>

          {/* Additional Metadata */}
          {document.metadata && (
            <div className="flex flex-wrap gap-2">
              {document.metadata.pages && (
                <Badge variant="secondary" className="text-xs">
                  {document.metadata.pages} page{document.metadata.pages !== 1 ? 's' : ''}
                </Badge>
              )}
              {document.metadata.word_count && (
                <Badge variant="secondary" className="text-xs">
                  {document.metadata.word_count.toLocaleString()} words
                </Badge>
              )}
            </div>
          )}

          {/* OCR Preview */}
          {document.ocr_text && (
            <div className="rounded-lg border bg-muted/50 p-3">
              <p className="mb-1 text-xs font-semibold text-muted-foreground">OCR Text Preview</p>
              <p className="line-clamp-2 text-sm text-foreground">
                {document.ocr_text}
              </p>
            </div>
          )}
        </div>

        {/* Quick Actions (visible on hover) */}
        <div className="mt-4 flex gap-2 opacity-0 transition-opacity group-hover:opacity-100">
          {onView && (
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onView(document.id);
              }}
              className="flex-1"
            >
              <Eye className="mr-2 h-4 w-4" />
              View
            </Button>
          )}
          {onDownload && (
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onDownload(document.id);
              }}
              className="flex-1"
            >
              <Download className="mr-2 h-4 w-4" />
              Download
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
