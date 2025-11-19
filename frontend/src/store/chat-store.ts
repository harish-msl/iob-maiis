import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import type {
  ChatMessage,
  ChatSession,
  ChatStreamChunk,
  RAGSource,
} from "@/lib/types/chat";

interface ChatState {
  // Current session
  currentSessionId: string | null;
  sessions: ChatSession[];
  messages: Record<string, ChatMessage[]>; // sessionId -> messages[]

  // Streaming state
  isStreaming: boolean;
  streamingMessageId: string | null;
  streamingContent: string;
  streamingSources: RAGSource[];

  // UI state
  selectedMessageId: string | null;
  isLoadingHistory: boolean;
  error: string | null;

  // Actions - Session management
  createSession: (title?: string) => ChatSession;
  setCurrentSession: (sessionId: string | null) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  deleteSession: (sessionId: string) => void;
  clearSessions: () => void;

  // Actions - Message management
  addMessage: (
    sessionId: string,
    message: Omit<ChatMessage, "id" | "timestamp">,
  ) => ChatMessage;
  updateMessage: (
    sessionId: string,
    messageId: string,
    updates: Partial<ChatMessage>,
  ) => void;
  deleteMessage: (sessionId: string, messageId: string) => void;
  clearMessages: (sessionId: string) => void;

  // Actions - Streaming
  startStreaming: (messageId: string) => void;
  appendStreamChunk: (chunk: ChatStreamChunk) => void;
  finishStreaming: (sources?: RAGSource[]) => void;
  cancelStreaming: () => void;

  // Actions - UI
  setSelectedMessage: (messageId: string | null) => void;
  setError: (error: string | null) => void;
  setLoadingHistory: (loading: boolean) => void;

  // Utilities
  getSessionMessages: (sessionId: string) => ChatMessage[];
  getCurrentMessages: () => ChatMessage[];
  getSessionById: (sessionId: string) => ChatSession | undefined;
}

const generateId = () =>
  `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        currentSessionId: null,
        sessions: [],
        messages: {},
        isStreaming: false,
        streamingMessageId: null,
        streamingContent: "",
        streamingSources: [],
        selectedMessageId: null,
        isLoadingHistory: false,
        error: null,

        // Session management
        createSession: (title?: string) => {
          const session: ChatSession = {
            id: generateId(),
            title: title || `Chat ${new Date().toLocaleDateString()}`,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            message_count: 0,
          };

          set((state) => ({
            sessions: [session, ...state.sessions],
            currentSessionId: session.id,
            messages: {
              ...state.messages,
              [session.id]: [],
            },
          }));

          return session;
        },

        setCurrentSession: (sessionId) => {
          set({ currentSessionId: sessionId });
        },

        updateSessionTitle: (sessionId, title) => {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === sessionId
                ? { ...session, title, updated_at: new Date().toISOString() }
                : session,
            ),
          }));
        },

        deleteSession: (sessionId) => {
          set((state) => {
            const newMessages = { ...state.messages };
            delete newMessages[sessionId];

            return {
              sessions: state.sessions.filter((s) => s.id !== sessionId),
              messages: newMessages,
              currentSessionId:
                state.currentSessionId === sessionId
                  ? null
                  : state.currentSessionId,
            };
          });
        },

        clearSessions: () => {
          set({
            sessions: [],
            messages: {},
            currentSessionId: null,
          });
        },

        // Message management
        addMessage: (sessionId, messageData) => {
          const message: ChatMessage = {
            ...messageData,
            id: generateId(),
            timestamp: new Date().toISOString(),
          };

          set((state) => {
            const sessionMessages = state.messages[sessionId] || [];
            const updatedMessages = [...sessionMessages, message];

            return {
              messages: {
                ...state.messages,
                [sessionId]: updatedMessages,
              },
              sessions: state.sessions.map((session) =>
                session.id === sessionId
                  ? {
                      ...session,
                      message_count: updatedMessages.length,
                      updated_at: new Date().toISOString(),
                    }
                  : session,
              ),
            };
          });

          return message;
        },

        updateMessage: (sessionId, messageId, updates) => {
          set((state) => ({
            messages: {
              ...state.messages,
              [sessionId]: (state.messages[sessionId] || []).map((msg) =>
                msg.id === messageId ? { ...msg, ...updates } : msg,
              ),
            },
          }));
        },

        deleteMessage: (sessionId, messageId) => {
          set((state) => {
            const updatedMessages = (state.messages[sessionId] || []).filter(
              (msg) => msg.id !== messageId,
            );

            return {
              messages: {
                ...state.messages,
                [sessionId]: updatedMessages,
              },
              sessions: state.sessions.map((session) =>
                session.id === sessionId
                  ? {
                      ...session,
                      message_count: updatedMessages.length,
                      updated_at: new Date().toISOString(),
                    }
                  : session,
              ),
            };
          });
        },

        clearMessages: (sessionId) => {
          set((state) => ({
            messages: {
              ...state.messages,
              [sessionId]: [],
            },
            sessions: state.sessions.map((session) =>
              session.id === sessionId
                ? {
                    ...session,
                    message_count: 0,
                    updated_at: new Date().toISOString(),
                  }
                : session,
            ),
          }));
        },

        // Streaming
        startStreaming: (messageId) => {
          set({
            isStreaming: true,
            streamingMessageId: messageId,
            streamingContent: "",
            streamingSources: [],
          });
        },

        appendStreamChunk: (chunk) => {
          set((state) => {
            let newContent = state.streamingContent;
            let newSources = state.streamingSources;

            if (chunk.type === "token" && chunk.content) {
              newContent += chunk.content;
            }

            if (chunk.metadata?.sources) {
              newSources = chunk.metadata.sources;
            }

            // Update the streaming message in the current session
            const currentSessionId = state.currentSessionId;
            if (currentSessionId && state.streamingMessageId) {
              const updatedMessages = (
                state.messages[currentSessionId] || []
              ).map((msg) =>
                msg.id === state.streamingMessageId
                  ? {
                      ...msg,
                      content: newContent,
                      metadata: {
                        ...msg.metadata,
                        sources:
                          newSources.length > 0
                            ? newSources
                            : msg.metadata?.sources,
                      },
                    }
                  : msg,
              );

              return {
                streamingContent: newContent,
                streamingSources: newSources,
                messages: {
                  ...state.messages,
                  [currentSessionId]: updatedMessages,
                },
              };
            }

            return {
              streamingContent: newContent,
              streamingSources: newSources,
            };
          });
        },

        finishStreaming: (sources) => {
          set((state) => {
            const currentSessionId = state.currentSessionId;
            if (currentSessionId && state.streamingMessageId) {
              const finalSources = sources || state.streamingSources;
              const updatedMessages = (
                state.messages[currentSessionId] || []
              ).map((msg) =>
                msg.id === state.streamingMessageId
                  ? {
                      ...msg,
                      content: state.streamingContent,
                      metadata: {
                        ...msg.metadata,
                        sources:
                          finalSources.length > 0 ? finalSources : undefined,
                      },
                    }
                  : msg,
              );

              return {
                isStreaming: false,
                streamingMessageId: null,
                streamingContent: "",
                streamingSources: [],
                messages: {
                  ...state.messages,
                  [currentSessionId]: updatedMessages,
                },
              };
            }

            return {
              isStreaming: false,
              streamingMessageId: null,
              streamingContent: "",
              streamingSources: [],
            };
          });
        },

        cancelStreaming: () => {
          set((state) => {
            const currentSessionId = state.currentSessionId;
            if (currentSessionId && state.streamingMessageId) {
              // Remove the incomplete streaming message
              const updatedMessages = (
                state.messages[currentSessionId] || []
              ).filter((msg) => msg.id !== state.streamingMessageId);

              return {
                isStreaming: false,
                streamingMessageId: null,
                streamingContent: "",
                streamingSources: [],
                messages: {
                  ...state.messages,
                  [currentSessionId]: updatedMessages,
                },
              };
            }

            return {
              isStreaming: false,
              streamingMessageId: null,
              streamingContent: "",
              streamingSources: [],
            };
          });
        },

        // UI actions
        setSelectedMessage: (messageId) => {
          set({ selectedMessageId: messageId });
        },

        setError: (error) => {
          set({ error });
        },

        setLoadingHistory: (loading) => {
          set({ isLoadingHistory: loading });
        },

        // Utilities
        getSessionMessages: (sessionId) => {
          return get().messages[sessionId] || [];
        },

        getCurrentMessages: () => {
          const { currentSessionId, messages } = get();
          if (!currentSessionId) return [];
          return messages[currentSessionId] || [];
        },

        getSessionById: (sessionId) => {
          return get().sessions.find((s) => s.id === sessionId);
        },
      }),
      {
        name: "chat-storage",
        partialize: (state) => ({
          sessions: state.sessions,
          messages: state.messages,
          currentSessionId: state.currentSessionId,
        }),
      },
    ),
    { name: "ChatStore" },
  ),
);

// Selectors for optimized re-renders
export const useChatSessions = () => useChatStore((state) => state.sessions);
export const useCurrentSession = () =>
  useChatStore((state) => {
    if (!state.currentSessionId) return null;
    return state.getSessionById(state.currentSessionId);
  });
export const useCurrentMessages = () =>
  useChatStore((state) => state.getCurrentMessages());
export const useIsStreaming = () => useChatStore((state) => state.isStreaming);
export const useChatError = () => useChatStore((state) => state.error);
