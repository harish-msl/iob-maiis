"use client";

import React, { useRef, useState } from "react";
import { Send, Paperclip, X, Loader2, Mic } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";
import { VoiceControls } from "@/components/voice";

interface ChatInputProps {
  onSendMessage: (message: string, files?: File[]) => void;
  disabled?: boolean;
  placeholder?: string;
  maxFiles?: number;
  maxFileSize?: number; // in MB
  acceptedFileTypes?: string[];
  className?: string;
}

export function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder = "Type a message...",
  maxFiles = 5,
  maxFileSize = 10,
  acceptedFileTypes = [
    "image/*",
    "application/pdf",
    ".txt",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
  ],
  className,
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [showVoiceControls, setShowVoiceControls] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-resize textarea
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    adjustTextareaHeight();
  };

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newFiles: File[] = [];
    const errors: string[] = [];

    Array.from(files).forEach((file) => {
      // Check file size
      if (file.size > maxFileSize * 1024 * 1024) {
        errors.push(`${file.name} exceeds ${maxFileSize}MB limit`);
        return;
      }

      // Check total file count
      if (attachedFiles.length + newFiles.length >= maxFiles) {
        errors.push(`Maximum ${maxFiles} files allowed`);
        return;
      }

      newFiles.push(file);
    });

    if (errors.length > 0) {
      alert(errors.join("\n"));
    }

    if (newFiles.length > 0) {
      setAttachedFiles([...attachedFiles, ...newFiles]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files);
    // Reset input to allow selecting the same file again
    e.target.value = "";
  };

  const removeFile = (index: number) => {
    setAttachedFiles(attachedFiles.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedMessage = message.trim();

    // Don't send if both message and files are empty
    if (!trimmedMessage && attachedFiles.length === 0) return;

    // Send message with optional files
    onSendMessage(
      trimmedMessage || "Attached files",
      attachedFiles.length > 0 ? attachedFiles : undefined,
    );

    // Reset state
    setMessage("");
    setAttachedFiles([]);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Drag and drop handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    handleFileSelect(files);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const handleVoiceTranscription = (text: string) => {
    setMessage(text);
    setShowVoiceControls(false);
    // Auto-focus textarea after transcription
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  return (
    <div className={cn("relative", className)}>
      {/* Voice Controls Modal */}
      {showVoiceControls && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-2xl">
            <VoiceControls
              onTranscription={handleVoiceTranscription}
              onError={(error) => console.error("Voice error:", error)}
            />
            <Button
              onClick={() => setShowVoiceControls(false)}
              variant="outline"
              className="mt-4 w-full"
            >
              Close Voice Controls
            </Button>
          </div>
        </div>
      )}
      {/* Drag overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-50 flex items-center justify-center rounded-lg border-2 border-dashed border-primary bg-primary/5 backdrop-blur-sm">
          <div className="text-center">
            <Paperclip className="mx-auto h-8 w-8 text-primary" />
            <p className="mt-2 text-sm font-medium">Drop files to attach</p>
          </div>
        </div>
      )}

      {/* Attached files preview */}
      {attachedFiles.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2 rounded-lg border bg-muted/50 p-3">
          {attachedFiles.map((file, index) => (
            <div
              key={index}
              className="group flex items-center gap-2 rounded-md border bg-background px-3 py-2 text-sm"
            >
              <Paperclip className="h-4 w-4 text-muted-foreground" />
              <div className="flex flex-col">
                <span className="max-w-[200px] truncate font-medium">
                  {file.name}
                </span>
                <span className="text-xs text-muted-foreground">
                  {formatFileSize(file.size)}
                </span>
              </div>
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="ml-2 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input form */}
      <form
        onSubmit={handleSubmit}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className="relative flex items-end gap-2 rounded-lg border bg-background p-2 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2"
      >
        {/* File upload button */}
        <div className="flex items-end gap-1 pb-1">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={acceptedFileTypes.join(",")}
            onChange={handleFileInputChange}
            className="hidden"
            disabled={disabled || attachedFiles.length >= maxFiles}
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || attachedFiles.length >= maxFiles}
            className="h-9 w-9 p-0"
            title="Attach files"
          >
            <Paperclip className="h-5 w-5" />
          </Button>

          {/* Voice button */}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setShowVoiceControls(true)}
            disabled={disabled}
            className="h-9 w-9 p-0"
            title="Voice input"
          >
            <Mic className="h-5 w-5" />
          </Button>
        </div>

        {/* Text input */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="min-h-[40px] flex-1 resize-none bg-transparent px-2 py-2 text-sm placeholder:text-muted-foreground focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
          style={{ maxHeight: "200px" }}
        />

        {/* Send button */}
        <div className="flex items-end pb-1">
          <Button
            type="submit"
            size="sm"
            disabled={
              disabled || (!message.trim() && attachedFiles.length === 0)
            }
            className="h-9 w-9 p-0"
            title="Send message"
          >
            {disabled ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </div>
      </form>

      {/* Helper text */}
      <div className="mt-2 flex items-center justify-between px-1 text-xs text-muted-foreground">
        <span>
          Press <kbd className="rounded bg-muted px-1">Enter</kbd> to send,{" "}
          <kbd className="rounded bg-muted px-1">Shift+Enter</kbd> for new line
        </span>
        {attachedFiles.length > 0 && (
          <span>
            {attachedFiles.length}/{maxFiles} files
          </span>
        )}
      </div>
    </div>
  );
}
