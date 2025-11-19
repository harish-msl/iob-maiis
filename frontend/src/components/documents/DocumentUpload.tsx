"use client";

import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  File,
  FileText,
  Image,
  FileSpreadsheet,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils/cn";

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: "pending" | "uploading" | "success" | "error";
  error?: string;
  documentId?: string;
}

interface DocumentUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  onFileComplete?: (fileId: string, documentId: string) => void;
  onFileError?: (fileId: string, error: string) => void;
  maxFiles?: number;
  maxSize?: number; // in MB
  acceptedTypes?: Record<string, string[]>;
  className?: string;
}

const DEFAULT_ACCEPTED_TYPES = {
  "application/pdf": [".pdf"],
  "image/*": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
  "application/msword": [".doc"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
    ".docx",
  ],
  "application/vnd.ms-excel": [".xls"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
    ".xlsx",
  ],
  "text/plain": [".txt"],
};

export function DocumentUpload({
  onUpload,
  onFileComplete: _onFileComplete,
  onFileError: _onFileError,
  maxFiles = 10,
  maxSize = 50, // 50MB default
  acceptedTypes,
  className,
}: DocumentUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      // Check max files limit
      const totalFiles = uploadedFiles.length + acceptedFiles.length;
      if (totalFiles > maxFiles) {
        alert(
          `Maximum ${maxFiles} files allowed. You can only upload ${maxFiles - uploadedFiles.length} more.`,
        );
        return;
      }

      // Create upload file objects
      const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
        file,
        id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        progress: 0,
        status: "pending" as const,
      }));

      setUploadedFiles((prev) => [...prev, ...newFiles]);
      setIsUploading(true);

      try {
        // Call upload handler
        await onUpload(acceptedFiles);

        // Update all files to success
        setUploadedFiles((prev) =>
          prev.map((f) =>
            newFiles.find((nf) => nf.id === f.id)
              ? { ...f, status: "success" as const, progress: 100 }
              : f,
          ),
        );
      } catch (error: any) {
        // Update files to error
        setUploadedFiles((prev) =>
          prev.map((f) =>
            newFiles.find((nf) => nf.id === f.id)
              ? { ...f, status: "error" as const, error: error.message }
              : f,
          ),
        );
      } finally {
        setIsUploading(false);
      }
    },
    [uploadedFiles.length, maxFiles, onUpload],
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } =
    useDropzone({
      onDrop,
      accept: acceptedTypes || DEFAULT_ACCEPTED_TYPES,
      maxSize: maxSize * 1024 * 1024, // Convert MB to bytes
      disabled: isUploading,
    });

  const removeFile = (fileId: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const clearAll = () => {
    setUploadedFiles([]);
  };

  const retryFile = async (fileId: string) => {
    const fileToRetry = uploadedFiles.find((f) => f.id === fileId);
    if (!fileToRetry) return;

    setUploadedFiles((prev) =>
      prev.map((f) =>
        f.id === fileId
          ? { ...f, status: "pending" as const, error: undefined }
          : f,
      ),
    );

    setIsUploading(true);
    try {
      await onUpload([fileToRetry.file]);
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? { ...f, status: "success" as const, progress: 100 }
            : f,
        ),
      );
    } catch (error: any) {
      setUploadedFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? { ...f, status: "error" as const, error: error.message }
            : f,
        ),
      );
    } finally {
      setIsUploading(false);
    }
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split(".").pop()?.toLowerCase();
    switch (ext) {
      case "pdf":
        return <FileText className="h-8 w-8 text-red-500" />;
      case "doc":
      case "docx":
        return <FileText className="h-8 w-8 text-blue-500" />;
      case "xls":
      case "xlsx":
        return <FileSpreadsheet className="h-8 w-8 text-green-500" />;
      case "png":
      case "jpg":
      case "jpeg":
      case "gif":
      case "webp":
        return <Image className="h-8 w-8 text-purple-500" />;
      default:
        return <File className="h-8 w-8 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const successCount = uploadedFiles.filter(
    (f) => f.status === "success",
  ).length;
  const errorCount = uploadedFiles.filter((f) => f.status === "error").length;
  const pendingCount = uploadedFiles.filter(
    (f) => f.status === "pending" || f.status === "uploading",
  ).length;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Upload Dropzone */}
      <Card
        {...getRootProps()}
        className={cn(
          "cursor-pointer border-2 border-dashed p-12 text-center transition-all",
          isDragActive && "border-primary bg-primary/5",
          isUploading && "pointer-events-none opacity-50",
          !isDragActive &&
            !isUploading &&
            "hover:border-primary hover:bg-muted/50",
        )}
      >
        <input {...getInputProps()} />
        <div className="mx-auto flex max-w-md flex-col items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <Upload
              className={cn(
                "h-8 w-8 text-primary",
                isDragActive && "animate-bounce",
              )}
            />
          </div>
          {isDragActive ? (
            <div>
              <p className="text-lg font-semibold">Drop files here</p>
              <p className="text-sm text-muted-foreground">Release to upload</p>
            </div>
          ) : (
            <div>
              <p className="text-lg font-semibold">Drag & drop files here</p>
              <p className="text-sm text-muted-foreground">
                or click to browse
              </p>
            </div>
          )}
          <div className="text-xs text-muted-foreground">
            <p>Accepted: PDF, Images, Word, Excel, Text files</p>
            <p>Maximum file size: {maxSize}MB</p>
            <p>Maximum files: {maxFiles}</p>
          </div>
        </div>
      </Card>

      {/* File Rejections */}
      {fileRejections.length > 0 && (
        <Card className="border-destructive/50 bg-destructive/10 p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 shrink-0 text-destructive" />
            <div className="flex-1">
              <p className="font-semibold text-destructive">
                Some files were rejected:
              </p>
              <ul className="mt-2 space-y-1 text-sm text-destructive">
                {fileRejections.map(({ file, errors }) => (
                  <li key={file.name}>
                    <span className="font-medium">{file.name}</span>:{" "}
                    {errors.map((e) => e.message).join(", ")}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      )}

      {/* Upload Summary */}
      {uploadedFiles.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-sm">
              <span className="font-semibold">{uploadedFiles.length}</span> file
              {uploadedFiles.length !== 1 ? "s" : ""}
            </div>
            {successCount > 0 && (
              <Badge variant="default" className="gap-1">
                <CheckCircle2 className="h-3 w-3" />
                {successCount} completed
              </Badge>
            )}
            {errorCount > 0 && (
              <Badge
                variant="outline"
                className="gap-1 border-destructive text-destructive"
              >
                <AlertCircle className="h-3 w-3" />
                {errorCount} failed
              </Badge>
            )}
            {pendingCount > 0 && (
              <Badge variant="secondary" className="gap-1">
                <Loader2 className="h-3 w-3 animate-spin" />
                {pendingCount} pending
              </Badge>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAll}
            disabled={isUploading}
          >
            Clear All
          </Button>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          {uploadedFiles.map((uploadedFile) => (
            <Card
              key={uploadedFile.id}
              className={cn(
                "p-4 transition-all",
                uploadedFile.status === "error" &&
                  "border-destructive/50 bg-destructive/5",
              )}
            >
              <div className="flex items-center gap-4">
                {/* File Icon */}
                <div className="shrink-0">
                  {getFileIcon(uploadedFile.file.name)}
                </div>

                {/* File Info */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate font-medium">
                      {uploadedFile.file.name}
                    </p>
                    {uploadedFile.status === "success" && (
                      <CheckCircle2 className="h-4 w-4 shrink-0 text-green-500" />
                    )}
                    {uploadedFile.status === "error" && (
                      <AlertCircle className="h-4 w-4 shrink-0 text-destructive" />
                    )}
                    {uploadedFile.status === "uploading" && (
                      <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(uploadedFile.file.size)}
                  </p>

                  {/* Error Message */}
                  {uploadedFile.status === "error" && uploadedFile.error && (
                    <p className="mt-1 text-sm text-destructive">
                      {uploadedFile.error}
                    </p>
                  )}

                  {/* Progress Bar */}
                  {(uploadedFile.status === "uploading" ||
                    uploadedFile.status === "pending") && (
                    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full bg-primary transition-all duration-300"
                        style={{ width: `${uploadedFile.progress}%` }}
                      />
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex shrink-0 items-center gap-2">
                  {uploadedFile.status === "error" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => retryFile(uploadedFile.id)}
                      disabled={isUploading}
                    >
                      Retry
                    </Button>
                  )}
                  {uploadedFile.status !== "uploading" && (
                    <button
                      onClick={() => removeFile(uploadedFile.id)}
                      className="rounded p-1 hover:bg-muted"
                      disabled={isUploading}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
