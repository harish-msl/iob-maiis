'use client';

import React, { useEffect, useState } from 'react';
import {
  Upload,
  FileText,
  RefreshCw,
  Grid3x3,
  List,
  Search,
  Filter,
} from 'lucide-react';
import { DocumentUpload } from '@/components/documents/DocumentUpload';
import { DocumentCard } from '@/components/documents/DocumentCard';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { apiClient } from '@/lib/api/client';
import { cn } from '@/lib/utils/cn';
import { useRouter } from 'next/navigation';

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
    [key: string]: any;
  };
};

type ViewMode = 'grid' | 'list';
type FilterType = 'all' | 'uploaded' | 'processing' | 'processed' | 'error';

export default function DocumentsPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [showUpload, setShowUpload] = useState(false);

  // Fetch documents
  const fetchDocuments = async () => {
    try {
      setError(null);
      const response = await apiClient.documents.list();
      setDocuments(response.data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
      console.error('Failed to fetch documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchDocuments();
    setIsRefreshing(false);
  };

  const handleUpload = async (files: File[]) => {
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      await apiClient.documents.upload(formData);
      await fetchDocuments();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Upload failed');
    }
  };

  const handleView = (documentId: string) => {
    router.push(`/dashboard/documents/${documentId}`);
  };

  const handleDownload = async (documentId: string) => {
    try {
      const document = documents.find((d) => d.id === documentId);
      if (!document) return;

      // For now, create a text file with OCR text if available
      if (document.ocr_text) {
        const blob = new Blob([document.ocr_text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${document.filename}_ocr.txt`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert('No downloadable content available. OCR not yet processed.');
      }
    } catch (err) {
      console.error('Download failed:', err);
      alert('Failed to download document');
    }
  };

  const handleDelete = async (documentId: string) => {
    try {
      await apiClient.documents.delete(documentId);
      await fetchDocuments();
    } catch (err: any) {
      console.error('Delete failed:', err);
      alert('Failed to delete document');
    }
  };

  const handleProcessOCR = async (documentId: string) => {
    try {
      await apiClient.documents.processOCR(documentId);
      // Update document status
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === documentId ? { ...doc, status: 'processing' as const } : doc
        )
      );
      // Refresh after a delay to get updated status
      setTimeout(fetchDocuments, 2000);
    } catch (err: any) {
      console.error('OCR processing failed:', err);
      alert('Failed to process OCR');
    }
  };

  const handleIngest = async (documentId: string) => {
    try {
      await apiClient.documents.ingest(documentId);
      alert('Document ingested to vector database successfully!');
    } catch (err: any) {
      console.error('Ingestion failed:', err);
      alert('Failed to ingest document to vector database');
    }
  };

  // Filter and search documents
  const filteredDocuments = documents.filter((doc) => {
    // Filter by type
    if (filterType !== 'all' && doc.status !== filterType) {
      return false;
    }

    // Search by filename
    if (searchQuery && !doc.filename.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }

    return true;
  });

  const statusCounts = {
    all: documents.length,
    uploaded: documents.filter((d) => d.status === 'uploaded').length,
    processing: documents.filter((d) => d.status === 'processing').length,
    processed: documents.filter((d) => d.status === 'processed').length,
    error: documents.filter((d) => d.status === 'error').length,
  };

  if (isLoading) {
    return (
      <div className="container mx-auto space-y-6 p-6">
        {/* Loading skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 animate-pulse rounded bg-muted" />
            <div className="h-4 w-64 animate-pulse rounded bg-muted" />
          </div>
          <div className="h-10 w-32 animate-pulse rounded bg-muted" />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground">
            Upload and manage your documents for AI analysis
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw
              className={cn('mr-2 h-4 w-4', isRefreshing && 'animate-spin')}
            />
            Refresh
          </Button>
          <Button onClick={() => setShowUpload(!showUpload)}>
            <Upload className="mr-2 h-4 w-4" />
            {showUpload ? 'Hide Upload' : 'Upload Files'}
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/10 p-4">
          <p className="text-sm text-destructive">{error}</p>
        </Card>
      )}

      {/* Upload Section */}
      {showUpload && (
        <DocumentUpload
          onUpload={handleUpload}
          maxFiles={10}
          maxSize={50}
        />
      )}

      {/* Filters and Search */}
      <Card className="p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          {/* Search */}
          <div className="relative flex-1 lg:max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          <div className="flex items-center gap-4">
            {/* Status Filter */}
            <div className="flex items-center gap-1 rounded-lg border p-1">
              {(['all', 'uploaded', 'processing', 'processed', 'error'] as FilterType[]).map(
                (type) => (
                  <button
                    key={type}
                    onClick={() => setFilterType(type)}
                    className={cn(
                      'rounded px-3 py-1.5 text-sm font-medium transition-colors',
                      filterType === type
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-muted'
                    )}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                    {statusCounts[type] > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        {statusCounts[type]}
                      </Badge>
                    )}
                  </button>
                )
              )}
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center gap-1 rounded-lg border p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'rounded p-2 transition-colors',
                  viewMode === 'grid'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted'
                )}
              >
                <Grid3x3 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'rounded p-2 transition-colors',
                  viewMode === 'list'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted'
                )}
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Results count */}
        <div className="mt-4 text-sm text-muted-foreground">
          Showing {filteredDocuments.length} of {documents.length} document
          {documents.length !== 1 ? 's' : ''}
        </div>
      </Card>

      {/* Documents Grid/List */}
      {filteredDocuments.length > 0 ? (
        <div
          className={cn(
            viewMode === 'grid'
              ? 'grid gap-6 md:grid-cols-2 lg:grid-cols-3'
              : 'space-y-4'
          )}
        >
          {filteredDocuments.map((document) => (
            <DocumentCard
              key={document.id}
              document={document}
              onView={handleView}
              onDownload={handleDownload}
              onDelete={handleDelete}
              onProcessOCR={handleProcessOCR}
              onIngest={handleIngest}
            />
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <div className="mx-auto max-w-md">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">
              {searchQuery || filterType !== 'all'
                ? 'No Documents Found'
                : 'No Documents Yet'}
            </h3>
            <p className="mb-6 text-sm text-muted-foreground">
              {searchQuery || filterType !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Upload your first document to get started with AI-powered analysis'}
            </p>
            {!showUpload && !searchQuery && filterType === 'all' && (
              <Button onClick={() => setShowUpload(true)}>
                <Upload className="mr-2 h-4 w-4" />
                Upload Document
              </Button>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
