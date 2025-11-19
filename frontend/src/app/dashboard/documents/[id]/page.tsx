'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ArrowLeft,
  Download,
  Trash2,
  RefreshCw,
  HardDrive,
  FileText,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { OCRViewer } from '@/components/documents/OCRViewer';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api/client';
import { formatDate } from '@/lib/utils/format';

type Document = {
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
    confidence?: number;
    language?: string;
    [key: string]: any;
  };
};

export default function DocumentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const documentId = params.id as string;

  const [document, setDocument] = useState<Document | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocument = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.getDocument(documentId);
        setDocument(response.data);
      } catch (err: any) {
        setError(err.message || 'Failed to load document');
        console.error('Failed to fetch document:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocument();
  }, [documentId]);

  const handleProcessOCR = async () => {
    if (!document) return;

    setIsProcessing(true);
    try {
      await apiClient.processOCR(documentId);
      setDocument({ ...document, status: 'processing' });

      // Poll for updates
      const pollInterval = setInterval(async () => {
        try {
          const response = await apiClient.getDocument(documentId);
          setDocument(response.data);

          if (response.data.status === 'processed' || response.data.status === 'error') {
            clearInterval(pollInterval);
            setIsProcessing(false);
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 3000);

      // Stop polling after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsProcessing(false);
      }, 120000);
    } catch (err: any) {
      setError(err.message || 'Failed to process OCR');
      setIsProcessing(false);
    }
  };

  const handleIngest = async () => {
    if (!document) return;

    if (!document.ocr_text) {
      alert('Please process OCR first before ingesting to vector database');
      return;
    }

    setIsIngesting(true);
    try {
      await apiClient.ingestDocuments([documentId]);
      alert('Document successfully ingested to vector database!');
    } catch (err: any) {
      setError(err.message || 'Failed to ingest document');
    } finally {
      setIsIngesting(false);
    }
  };

  const handleDownload = () => {
    if (!document?.ocr_text) {
      alert('No OCR text available to download');
      return;
    }

    const blob = new Blob([document.ocr_text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = window.document.createElement('a');
    a.href = url;
    a.download = `${document.filename}_ocr.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleDelete = async () => {
    if (!document) return;

    if (window.confirm(`Are you sure you want to delete "${document.filename}"?`)) {
      try {
        await apiClient.deleteDocument(documentId);
        router.push('/dashboard/documents');
      } catch (err: any) {
        setError(err.message || 'Failed to delete document');
      }
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'uploaded':
        return <Badge variant="secondary">Uploaded</Badge>;
      case 'processing':
        return (
          <Badge variant="outline" className="border-blue-500 text-blue-500">
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
            Processing
          </Badge>
        );
      case 'processed':
        return (
          <Badge variant="default">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Processed
          </Badge>
        );
      case 'error':
        return (
          <Badge variant="outline" className="border-red-500 text-red-500">
            <AlertCircle className="mr-1 h-3 w-3" />
            Error
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto space-y-6 p-6">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-64 animate-pulse rounded-lg bg-muted" />
        <div className="h-96 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="container mx-auto p-6">
        <Card className="p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
            <AlertCircle className="h-8 w-8 text-destructive" />
          </div>
          <h3 className="mb-2 text-lg font-semibold">Document Not Found</h3>
          <p className="mb-6 text-sm text-muted-foreground">
            {error || 'The document you are looking for does not exist.'}
          </p>
          <Button onClick={() => router.push('/dashboard/documents')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Documents
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard/documents')}
          className="gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Documents
        </Button>

        <div className="flex gap-2">
          {document.status === 'uploaded' && (
            <Button
              onClick={handleProcessOCR}
              disabled={isProcessing}
              variant="outline"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Process OCR
                </>
              )}
            </Button>
          )}
          {document.status === 'processed' && document.ocr_text && (
            <>
              <Button onClick={handleDownload} variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Download OCR Text
              </Button>
              <Button
                onClick={handleIngest}
                disabled={isIngesting}
                variant="outline"
              >
                {isIngesting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Ingesting...
                  </>
                ) : (
                  <>
                    <HardDrive className="mr-2 h-4 w-4" />
                    Ingest to Vector DB
                  </>
                )}
              </Button>
            </>
          )}
          <Button onClick={handleDelete} variant="outline">
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {/* Document Info Card */}
      <Card className="p-6">
        <div className="flex items-start gap-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-primary/10">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <div className="flex-1">
            <div className="mb-2 flex items-center gap-3">
              <h1 className="text-2xl font-bold">{document.filename}</h1>
              {getStatusBadge(document.status)}
            </div>
            <div className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <span className="text-muted-foreground">File Type:</span>{' '}
                <span className="font-medium">{document.file_type}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Size:</span>{' '}
                <span className="font-medium">
                  {formatFileSize(document.file_size)}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Uploaded:</span>{' '}
                <span className="font-medium">
                  {formatDate(document.upload_date)}
                </span>
              </div>
              {document.metadata?.pages && (
                <div>
                  <span className="text-muted-foreground">Pages:</span>{' '}
                  <span className="font-medium">{document.metadata.pages}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Processing Status Message */}
        {document.status === 'uploaded' && (
          <div className="mt-4 rounded-lg border border-blue-500/50 bg-blue-500/10 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 shrink-0 text-blue-500" />
              <div>
                <p className="font-semibold text-blue-700 dark:text-blue-400">
                  OCR Not Processed
                </p>
                <p className="mt-1 text-sm text-blue-600 dark:text-blue-300">
                  This document hasn't been processed yet. Click "Process OCR" to
                  extract text from the document.
                </p>
              </div>
            </div>
          </div>
        )}

        {document.status === 'processing' && (
          <div className="mt-4 rounded-lg border border-blue-500/50 bg-blue-500/10 p-4">
            <div className="flex items-start gap-3">
              <Loader2 className="h-5 w-5 shrink-0 animate-spin text-blue-500" />
              <div>
                <p className="font-semibold text-blue-700 dark:text-blue-400">
                  Processing in Progress
                </p>
                <p className="mt-1 text-sm text-blue-600 dark:text-blue-300">
                  OCR is currently extracting text from your document. This may take a
                  few moments...
                </p>
              </div>
            </div>
          </div>
        )}

        {document.status === 'error' && (
          <div className="mt-4 rounded-lg border border-destructive/50 bg-destructive/10 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 shrink-0 text-destructive" />
              <div>
                <p className="font-semibold text-destructive">Processing Failed</p>
                <p className="mt-1 text-sm text-destructive/90">
                  An error occurred while processing this document. Please try again or
                  contact support.
                </p>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* OCR Viewer */}
      {document.status === 'processed' && document.ocr_text && (
        <OCRViewer
          text={document.ocr_text}
          filename={document.filename}
          metadata={document.metadata}
        />
      )}

      {/* Empty State for No OCR */}
      {!document.ocr_text && document.status !== 'processing' && (
        <Card className="p-12 text-center">
          <div className="mx-auto max-w-md">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">No OCR Text Available</h3>
            <p className="mb-6 text-sm text-muted-foreground">
              {document.status === 'uploaded'
                ? 'Process this document to extract text using OCR technology.'
                : 'OCR text extraction is not available for this document.'}
            </p>
            {document.status === 'uploaded' && (
              <Button onClick={handleProcessOCR} disabled={isProcessing}>
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Process OCR Now
                  </>
                )}
              </Button>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
