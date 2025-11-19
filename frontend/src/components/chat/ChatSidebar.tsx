'use client';

import React, { useState } from 'react';
import {
  Plus,
  MessageSquare,
  Trash2,
  Edit2,
  Check,
  X,
  MoreVertical,
  Calendar,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useChatStore } from '@/store/chat-store';
import { cn } from '@/lib/utils/cn';
import { formatDistanceToNow } from '@/lib/utils/format';

interface ChatSidebarProps {
  className?: string;
  onClose?: () => void;
}

export function ChatSidebar({ className, onClose }: ChatSidebarProps) {
  const {
    sessions,
    currentSessionId,
    createSession,
    setCurrentSession,
    updateSessionTitle,
    deleteSession,
    getSessionMessages,
  } = useChatStore();

  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');

  const handleCreateSession = () => {
    const newSession = createSession();
    setCurrentSession(newSession.id);
    if (onClose) onClose();
  };

  const handleSelectSession = (sessionId: string) => {
    setCurrentSession(sessionId);
    if (onClose) onClose();
  };

  const handleStartEdit = (sessionId: string, currentTitle: string) => {
    setEditingSessionId(sessionId);
    setEditingTitle(currentTitle);
  };

  const handleSaveEdit = (sessionId: string) => {
    if (editingTitle.trim()) {
      updateSessionTitle(sessionId, editingTitle.trim());
    }
    setEditingSessionId(null);
    setEditingTitle('');
  };

  const handleCancelEdit = () => {
    setEditingSessionId(null);
    setEditingTitle('');
  };

  const handleDeleteSession = (sessionId: string) => {
    if (window.confirm('Delete this chat? This action cannot be undone.')) {
      deleteSession(sessionId);
    }
  };

  const getSessionPreview = (sessionId: string): string => {
    const messages = getSessionMessages(sessionId);
    if (messages.length === 0) return 'No messages yet';

    const lastMessage = messages[messages.length - 1];
    const preview = lastMessage.content.slice(0, 60);
    return preview.length < lastMessage.content.length
      ? `${preview}...`
      : preview;
  };

  return (
    <div className={cn('flex h-full flex-col bg-background', className)}>
      {/* Header */}
      <div className="border-b p-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Chats</h2>
          {onClose && (
            <Button
              size="sm"
              variant="ghost"
              onClick={onClose}
              className="h-8 w-8 p-0 lg:hidden"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        <Button onClick={handleCreateSession} className="w-full">
          <Plus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="flex h-full items-center justify-center p-8 text-center">
            <div className="text-muted-foreground">
              <MessageSquare className="mx-auto mb-3 h-12 w-12 opacity-50" />
              <p className="text-sm">No chats yet</p>
              <p className="mt-1 text-xs">Start a new conversation</p>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => {
              const isActive = session.id === currentSessionId;
              const isEditing = editingSessionId === session.id;

              return (
                <Card
                  key={session.id}
                  className={cn(
                    'group cursor-pointer border-0 p-3 transition-all hover:bg-muted/50',
                    isActive && 'bg-primary/10 hover:bg-primary/15'
                  )}
                >
                  {isEditing ? (
                    <div className="flex items-center gap-2">
                      <Input
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleSaveEdit(session.id);
                          } else if (e.key === 'Escape') {
                            handleCancelEdit();
                          }
                        }}
                        className="h-8 text-sm"
                        autoFocus
                      />
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleSaveEdit(session.id)}
                        className="h-8 w-8 p-0"
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleCancelEdit}
                        className="h-8 w-8 p-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <div
                      onClick={() => handleSelectSession(session.id)}
                      className="flex items-start gap-3"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <MessageSquare
                            className={cn(
                              'h-4 w-4 shrink-0',
                              isActive ? 'text-primary' : 'text-muted-foreground'
                            )}
                          />
                          <h3
                            className={cn(
                              'truncate text-sm font-medium',
                              isActive && 'text-primary'
                            )}
                          >
                            {session.title}
                          </h3>
                        </div>

                        <p className="mt-1 truncate text-xs text-muted-foreground">
                          {getSessionPreview(session.id)}
                        </p>

                        <div className="mt-2 flex items-center gap-2">
                          <Badge variant="secondary" className="text-xs">
                            {session.message_count} message
                            {session.message_count !== 1 ? 's' : ''}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(session.updated_at))}
                          </span>
                        </div>
                      </div>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-8 w-8 p-0 opacity-0 transition-opacity group-hover:opacity-100"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStartEdit(session.id, session.title);
                            }}
                          >
                            <Edit2 className="mr-2 h-4 w-4" />
                            Rename
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteSession(session.id);
                            }}
                            className="text-destructive focus:text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer with stats */}
      {sessions.length > 0 && (
        <div className="border-t p-4">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <Calendar className="h-3 w-3" />
              <span>{sessions.length} total chats</span>
            </div>
            <span>
              {sessions.reduce((acc, s) => acc + s.message_count, 0)} messages
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
