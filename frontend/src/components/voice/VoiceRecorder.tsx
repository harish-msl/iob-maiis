"use client";

import React from "react";
import { Mic, Square, Pause, Play, Trash2, Send } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils/cn";
import type { WaveformData } from "./types";

interface VoiceRecorderProps {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  waveformData: WaveformData;
  onStart: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
  onCancel: () => void;
  onSend?: () => void;
  disabled?: boolean;
  className?: string;
}

export function VoiceRecorder({
  isRecording,
  isPaused,
  duration,
  waveformData,
  onStart,
  onStop,
  onPause,
  onResume,
  onCancel,
  onSend,
  disabled = false,
  className,
}: VoiceRecorderProps) {
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const renderWaveform = () => {
    if (!isRecording || waveformData.data.length === 0) {
      return (
        <div className="flex items-center justify-center gap-1">
          {Array.from({ length: 40 }).map((_, i) => (
            <div
              key={i}
              className="w-1 rounded-full bg-muted transition-all"
              style={{ height: "4px" }}
            />
          ))}
        </div>
      );
    }

    // Sample waveform data to fit display
    const sampleSize = 40;
    const step = Math.max(1, Math.floor(waveformData.data.length / sampleSize));
    const sampledData = [];

    for (let i = 0; i < waveformData.data.length; i += step) {
      if (sampledData.length >= sampleSize) break;
      sampledData.push(waveformData.data[i]);
    }

    return (
      <div className="flex items-center justify-center gap-1">
        {sampledData.map((value, i) => {
          const height = Math.max(4, Math.abs(value) * 32);
          return (
            <div
              key={i}
              className={cn(
                "w-1 rounded-full transition-all",
                isPaused ? "bg-muted-foreground/50" : "bg-primary",
              )}
              style={{
                height: `${height}px`,
                animation: isPaused ? "none" : "pulse 1s ease-in-out infinite",
                animationDelay: `${i * 0.05}s`,
              }}
            />
          );
        })}
      </div>
    );
  };

  return (
    <div
      className={cn(
        "flex flex-col gap-4 rounded-lg border bg-card p-4",
        className,
      )}
    >
      {/* Waveform visualization */}
      <div className="relative flex h-16 items-center justify-center overflow-hidden rounded-md bg-muted/30 px-4">
        {renderWaveform()}
        {isRecording && !isPaused && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent animate-shimmer" />
        )}
      </div>

      {/* Duration display */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isRecording && (
            <>
              <div
                className={cn(
                  "h-3 w-3 rounded-full",
                  isPaused ? "bg-yellow-500" : "bg-red-500 animate-pulse",
                )}
              />
              <span className="text-sm font-medium text-muted-foreground">
                {isPaused ? "Paused" : "Recording"}
              </span>
            </>
          )}
        </div>
        <span className="font-mono text-lg font-semibold">
          {formatDuration(duration)}
        </span>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-2">
        {!isRecording ? (
          // Start recording button
          <Button
            onClick={onStart}
            disabled={disabled}
            size="lg"
            className="gap-2"
          >
            <Mic className="h-5 w-5" />
            Start Recording
          </Button>
        ) : (
          <>
            {/* Pause/Resume button */}
            <Button
              onClick={isPaused ? onResume : onPause}
              variant="outline"
              size="icon"
              title={isPaused ? "Resume" : "Pause"}
            >
              {isPaused ? (
                <Play className="h-5 w-5" />
              ) : (
                <Pause className="h-5 w-5" />
              )}
            </Button>

            {/* Stop button */}
            <Button
              onClick={onStop}
              variant="destructive"
              size="icon"
              title="Stop recording"
            >
              <Square className="h-5 w-5" />
            </Button>

            {/* Cancel button */}
            <Button
              onClick={onCancel}
              variant="ghost"
              size="icon"
              title="Cancel"
            >
              <Trash2 className="h-5 w-5" />
            </Button>

            {/* Send button (if provided) */}
            {onSend && (
              <Button
                onClick={onSend}
                variant="default"
                size="icon"
                title="Send recording"
              >
                <Send className="h-5 w-5" />
              </Button>
            )}
          </>
        )}
      </div>

      {/* Helper text */}
      {!isRecording && (
        <p className="text-center text-xs text-muted-foreground">
          Click the microphone to start recording your voice message
        </p>
      )}

      {isRecording && (
        <p className="text-center text-xs text-muted-foreground">
          {isPaused
            ? "Recording paused. Click play to resume."
            : "Recording in progress. Speak clearly into your microphone."}
        </p>
      )}

      <style jsx>{`
        @keyframes pulse {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }

        @keyframes shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
}
