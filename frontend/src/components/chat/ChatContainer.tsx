"use client";

import React, { useEffect, useRef, useState } from "react";
import { Loader2, AlertCircle, Trash2, RefreshCw } from "lucide-react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useChatStore } from "@/store/chat-store";
import { apiClient } from "@/lib/api/client";
import { cn } from "@/lib/utils/cn";
import type { ChatStreamChunk } from "@/lib/types/chat";

interface ChatContainerProps {
  sessionId?: string;
  className?: string;
}

export function ChatContainer({ sessionId, className }: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [isInitializing, setIsInitializing] = useState(false);

  const {
    currentSessionId,
    createSession,
    setCurrentSession,
    addMessage,
    getCurrentMessages,
    isStreaming,
    startStreaming,
    appendStreamChunk,
    finishStreaming,
    cancelStreaming,
    clearMessages,
    error,
    setError,
  } = useChatStore();

  const messages = getCurrentMessages();

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      if (!currentSessionId && !sessionId) {
        setIsInitializing(true);
        await createSession();
        setIsInitializing(false);
      } else if (sessionId && sessionId !== currentSessionId) {
        setCurrentSession(sessionId);
      }
    };
    initSession();
  }, [sessionId, currentSessionId, createSession, setCurrentSession]);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleSendMessage = async (messageText: string, files?: File[]) => {
    if (!currentSessionId) {
      setError("No active session");
      return;
    }

    setError(null);

    try {
      // Add user message
      addMessage(currentSessionId, {
        conversation_id: currentSessionId,
        role: "user",
        content: messageText,
      });

      // Create placeholder assistant message for streaming
      const assistantMessage = addMessage(currentSessionId, {
        conversation_id: currentSessionId,
        role: "assistant",
        content: "",
      });

      // Start streaming
      startStreaming(assistantMessage.id);

      // Create abort controller for this request
      abortControllerRef.current = new AbortController();

      // Prepare form data if files are attached
      let requestData: any = {
        message: messageText,
        stream: true,
      };

      if (files && files.length > 0) {
        const formData = new FormData();
        formData.append("message", messageText);
        files.forEach((file) => {
          formData.append("files", file);
        });
        formData.append("stream", "true");
        requestData = formData;
      }

      // Start SSE stream
      const response = await fetch(`${apiClient.getBaseURL()}/chat/stream`, {
        method: "POST",
        headers: files
          ? {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            }
          : {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
        body: files ? requestData : JSON.stringify(requestData),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Read SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("Failed to get response reader");
      }

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        // Decode chunk
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();

            if (data === "[DONE]") {
              finishStreaming();
              break;
            }

            try {
              const chunk: ChatStreamChunk = JSON.parse(data);

              if (chunk.type === "error") {
                throw new Error(chunk.error || "Streaming error");
              }

              appendStreamChunk(chunk);
            } catch (parseError) {
              console.error("Failed to parse SSE chunk:", parseError);
            }
          }
        }
      }

      // Ensure streaming is finished
      finishStreaming();
    } catch (error: any) {
      console.error("Chat error:", error);

      if (error.name === "AbortError") {
        setError("Message sending cancelled");
        cancelStreaming();
      } else {
        setError(error.message || "Failed to send message");
        finishStreaming();
      }
    } finally {
      abortControllerRef.current = null;
    }
  };

  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    cancelStreaming();
  };

  const handleClearChat = () => {
    if (
      currentSessionId &&
      window.confirm("Clear all messages in this chat?")
    ) {
      clearMessages(currentSessionId);
    }
  };

  const handleRetry = () => {
    if (messages.length > 0) {
      const lastUserMessage = [...messages]
        .reverse()
        .find((msg) => msg.role === "user");

      if (lastUserMessage) {
        handleSendMessage(lastUserMessage.content);
      }
    }
  };

  if (isInitializing) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-4 text-sm text-muted-foreground">
            Initializing chat...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("flex h-full flex-col", className)}>
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center p-8">
            <Card className="max-w-2xl p-8 text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <svg
                  className="h-8 w-8 text-primary"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Start a conversation
              </h3>
              <p className="mb-6 text-sm text-muted-foreground">
                Ask me anything about your banking needs. I can help with
                account information, transactions, document analysis, and more.
              </p>
              <div className="grid gap-2 text-left text-sm">
                <p className="font-medium">Try asking:</p>
                <ul className="space-y-1 text-muted-foreground">
                  <li>• "What's my current account balance?"</li>
                  <li>• "Show me transactions from last month"</li>
                  <li>• "Analyze this bank statement" (with file upload)</li>
                  <li>• "Help me transfer money to another account"</li>
                </ul>
              </div>
            </Card>
          </div>
        ) : (
          <div className="space-y-0">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                isStreaming={
                  isStreaming &&
                  message.id === useChatStore.getState().streamingMessageId
                }
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className="border-t bg-destructive/10 px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="ghost"
                onClick={handleRetry}
                className="h-8"
              >
                <RefreshCw className="mr-2 h-3 w-3" />
                Retry
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setError(null)}
                className="h-8"
              >
                Dismiss
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Input area */}
      <div className="border-t bg-background p-4">
        <div className="mx-auto max-w-4xl">
          {messages.length > 0 && (
            <div className="mb-3 flex items-center justify-end gap-2">
              <Button
                size="sm"
                variant="ghost"
                onClick={handleClearChat}
                disabled={isStreaming}
                className="h-8 text-xs"
              >
                <Trash2 className="mr-2 h-3 w-3" />
                Clear chat
              </Button>
            </div>
          )}

          {isStreaming ? (
            <div className="flex items-center justify-center gap-3 rounded-lg border bg-muted/50 p-4">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <span className="text-sm font-medium">AI is thinking...</span>
              <Button
                size="sm"
                variant="outline"
                onClick={handleStopStreaming}
                className="ml-auto"
              >
                Stop
              </Button>
            </div>
          ) : (
            <ChatInput
              onSendMessage={handleSendMessage}
              disabled={isStreaming}
              placeholder="Type your message... (supports file attachments)"
            />
          )}
        </div>
      </div>
    </div>
  );
}
