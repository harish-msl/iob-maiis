/**
 * Voice Feature Types
 */

export interface AudioRecording {
  blob: Blob;
  url: string;
  duration: number;
  timestamp: number;
}

export interface TranscriptionState {
  text: string;
  isTranscribing: boolean;
  confidence?: number;
  duration?: number;
  error?: string;
}

export interface VoiceSettings {
  language: string;
  autoTranscribe: boolean;
  ttsEnabled: boolean;
  ttsSpeed: number;
  ttsVoice?: string;
}

export interface WaveformData {
  data: number[];
  maxAmplitude: number;
}
