"use client";

import React, { useState } from "react";
import {
  Mic,
  Volume2,
  Settings,
  X,
  Check,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils/cn";
import { VoiceRecorder } from "./VoiceRecorder";
import { AudioPlayer } from "./AudioPlayer";
import { useVoice } from "./useVoice";

interface VoiceControlsProps {
  onTranscription?: (text: string) => void;
  onError?: (error: Error) => void;
  className?: string;
  compact?: boolean;
}

export function VoiceControls({
  onTranscription,
  onError,
  className,
  compact = false,
}: VoiceControlsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const voice = useVoice({
    onTranscription,
    onError,
  });

  const handleSendRecording = () => {
    if (voice.recording) {
      voice.transcribeRecording();
    }
  };

  const handleSpeak = (text: string) => {
    voice.speak(text);
  };

  if (compact && !isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        variant="outline"
        size="icon"
        className={cn("relative", className)}
        title="Voice controls"
      >
        <Mic className="h-5 w-5" />
        {voice.isRecording && (
          <span className="absolute -right-1 -top-1 flex h-3 w-3">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-500 opacity-75" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-red-500" />
          </span>
        )}
      </Button>
    );
  }

  return (
    <Card className={cn("relative overflow-hidden", className)}>
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4">
        <div className="flex items-center gap-2">
          <Mic className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Voice Assistant</h3>
          {voice.isRecording && (
            <Badge variant="destructive" className="animate-pulse">
              Recording
            </Badge>
          )}
          {voice.isSpeaking && (
            <Badge variant="default" className="animate-pulse">
              Speaking
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={() => setShowSettings(!showSettings)}
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            title="Settings"
          >
            <Settings className="h-4 w-4" />
          </Button>
          {compact && (
            <Button
              onClick={() => setIsOpen(false)}
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              title="Close"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="border-b bg-muted/30 p-4">
          <div className="space-y-4">
            {/* Language Selection */}
            <div>
              <label className="mb-2 block text-sm font-medium">Language</label>
              <select
                value={voice.settings.language}
                onChange={(e) =>
                  voice.updateSettings({ language: e.target.value })
                }
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
              >
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="es-ES">Spanish</option>
                <option value="fr-FR">French</option>
                <option value="de-DE">German</option>
                <option value="it-IT">Italian</option>
                <option value="pt-PT">Portuguese</option>
                <option value="zh-CN">Chinese</option>
                <option value="ja-JP">Japanese</option>
                <option value="ko-KR">Korean</option>
              </select>
            </div>

            {/* Auto Transcribe */}
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">Auto Transcribe</label>
              <input
                type="checkbox"
                checked={voice.settings.autoTranscribe}
                onChange={(e) =>
                  voice.updateSettings({ autoTranscribe: e.target.checked })
                }
                className="h-4 w-4 rounded border-gray-300"
              />
            </div>

            {/* TTS Enabled */}
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">
                Text-to-Speech Enabled
              </label>
              <input
                type="checkbox"
                checked={voice.settings.ttsEnabled}
                onChange={(e) =>
                  voice.updateSettings({ ttsEnabled: e.target.checked })
                }
                className="h-4 w-4 rounded border-gray-300"
              />
            </div>

            {/* TTS Speed */}
            {voice.settings.ttsEnabled && (
              <div>
                <label className="mb-2 block text-sm font-medium">
                  Speech Speed: {voice.settings.ttsSpeed.toFixed(1)}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={voice.settings.ttsSpeed}
                  onChange={(e) =>
                    voice.updateSettings({
                      ttsSpeed: parseFloat(e.target.value),
                    })
                  }
                  className="w-full"
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="space-y-4 p-4">
        {/* Permission Check */}
        {!voice.hasPermission && (
          <div className="rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              <div className="flex-1">
                <h4 className="font-medium text-yellow-900 dark:text-yellow-100">
                  Microphone Access Required
                </h4>
                <p className="mt-1 text-sm text-yellow-800 dark:text-yellow-200">
                  Please grant microphone permission to use voice features.
                </p>
                <Button
                  onClick={voice.requestPermission}
                  variant="outline"
                  size="sm"
                  className="mt-3"
                >
                  Grant Permission
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Voice Recorder */}
        <VoiceRecorder
          isRecording={voice.isRecording}
          isPaused={voice.isPaused}
          duration={voice.recordingDuration}
          waveformData={voice.waveformData}
          onStart={voice.startRecording}
          onStop={voice.stopRecording}
          onPause={voice.pauseRecording}
          onResume={voice.resumeRecording}
          onCancel={voice.cancelRecording}
          onSend={handleSendRecording}
          disabled={!voice.hasPermission}
        />

        {/* Recording Info */}
        {voice.recording && !voice.isRecording && (
          <div className="rounded-lg border bg-muted/30 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Check className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium">Recording Complete</p>
                  <p className="text-xs text-muted-foreground">
                    Duration: {voice.recording.duration.toFixed(2)}s
                  </p>
                </div>
              </div>
              <Button
                onClick={() => voice.transcribeRecording()}
                disabled={voice.transcription.isTranscribing}
                size="sm"
              >
                {voice.transcription.isTranscribing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Transcribing...
                  </>
                ) : (
                  "Transcribe"
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Transcription Result */}
        {voice.transcription.text && (
          <div className="rounded-lg border bg-card p-4">
            <div className="mb-2 flex items-center justify-between">
              <h4 className="text-sm font-medium">Transcription</h4>
              {voice.transcription.confidence && (
                <Badge variant="outline">
                  {Math.round(voice.transcription.confidence * 100)}% confident
                </Badge>
              )}
            </div>
            <p className="text-sm">{voice.transcription.text}</p>
            {voice.transcription.duration && (
              <p className="mt-2 text-xs text-muted-foreground">
                Audio duration: {voice.transcription.duration.toFixed(2)}s
              </p>
            )}
          </div>
        )}

        {/* Transcription Error */}
        {voice.transcription.error && (
          <div className="rounded-lg border border-red-500/50 bg-red-500/10 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <div>
                <h4 className="font-medium text-red-900 dark:text-red-100">
                  Transcription Failed
                </h4>
                <p className="mt-1 text-sm text-red-800 dark:text-red-200">
                  {voice.transcription.error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Audio Player for TTS */}
        {voice.isSpeaking && voice.currentAudio && (
          <AudioPlayer
            audio={voice.currentAudio}
            isPlaying={voice.isSpeaking}
            onStop={voice.stopSpeaking}
          />
        )}

        {/* Quick TTS Test */}
        {voice.settings.ttsEnabled && (
          <div className="rounded-lg border bg-muted/30 p-4">
            <h4 className="mb-3 text-sm font-medium">Test Text-to-Speech</h4>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Enter text to speak..."
                className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    const input = e.target as HTMLInputElement;
                    if (input.value.trim()) {
                      handleSpeak(input.value);
                      input.value = "";
                    }
                  }
                }}
              />
              <Button
                onClick={(e) => {
                  const input = (e.target as HTMLElement)
                    .closest(".rounded-lg")
                    ?.querySelector("input") as HTMLInputElement;
                  if (input?.value.trim()) {
                    handleSpeak(input.value);
                    input.value = "";
                  }
                }}
                size="sm"
                disabled={voice.isSpeaking}
              >
                <Volume2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="border-t bg-muted/30 px-4 py-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            Language: {voice.settings.language.split("-")[0].toUpperCase()}
          </span>
          <span>
            {voice.settings.autoTranscribe && "Auto-transcribe enabled"}
          </span>
        </div>
      </div>
    </Card>
  );
}
