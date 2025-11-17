/**
 * useVoice Hook
 * Manages voice recording, transcription, and text-to-speech state
 */

import { useState, useRef, useCallback, useEffect } from "react";
import { voiceApi } from "@/lib/api/voice";
import type {
  AudioRecording,
  TranscriptionState,
  VoiceSettings,
  WaveformData,
} from "./types";

interface UseVoiceOptions {
  onTranscription?: (text: string) => void;
  onError?: (error: Error) => void;
  autoTranscribe?: boolean;
  language?: string;
}

interface UseVoiceReturn {
  // Recording state
  isRecording: boolean;
  isPaused: boolean;
  recordingDuration: number;
  recording: AudioRecording | null;
  waveformData: WaveformData;

  // Transcription state
  transcription: TranscriptionState;

  // TTS state
  isSpeaking: boolean;
  currentAudio: HTMLAudioElement | null;

  // Recording controls
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  cancelRecording: () => void;

  // Transcription
  transcribeRecording: (recording?: AudioRecording) => Promise<void>;

  // TTS
  speak: (
    text: string,
    options?: {
      speed?: number;
      voice?: string;
      language?: string;
    },
  ) => Promise<void>;
  stopSpeaking: () => void;

  // Settings
  settings: VoiceSettings;
  updateSettings: (updates: Partial<VoiceSettings>) => void;

  // Permissions
  hasPermission: boolean;
  requestPermission: () => Promise<boolean>;
}

export function useVoice(options: UseVoiceOptions = {}): UseVoiceReturn {
  const {
    onTranscription,
    onError,
    autoTranscribe = false,
    language = "en-US",
  } = options;

  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recording, setRecording] = useState<AudioRecording | null>(null);
  const [waveformData, setWaveformData] = useState<WaveformData>({
    data: [],
    maxAmplitude: 0,
  });

  // Transcription state
  const [transcription, setTranscription] = useState<TranscriptionState>({
    text: "",
    isTranscribing: false,
  });

  // TTS state
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(
    null,
  );

  // Settings
  const [settings, setSettings] = useState<VoiceSettings>({
    language,
    autoTranscribe,
    ttsEnabled: true,
    ttsSpeed: 1.0,
  });

  // Permission state
  const [hasPermission, setHasPermission] = useState(false);

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const durationIntervalRef = useRef<number | null>(null);

  // Request microphone permission
  const requestPermission = useCallback(async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      setHasPermission(true);
      return true;
    } catch (error) {
      console.error("Microphone permission denied:", error);
      setHasPermission(false);
      onError?.(error as Error);
      return false;
    }
  }, [onError]);

  // Initialize audio context for waveform visualization
  const initializeAudioContext = useCallback((stream: MediaStream) => {
    const audioContext = new (window.AudioContext ||
      (window as any).webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    audioContextRef.current = audioContext;
    analyserRef.current = analyser;

    return analyser;
  }, []);

  // Animate waveform
  const animateWaveform = useCallback(() => {
    if (!analyserRef.current || !isRecording || isPaused) return;

    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const updateWaveform = () => {
      analyser.getByteTimeDomainData(dataArray);

      const data = Array.from(dataArray).map((value) => (value - 128) / 128);
      const maxAmplitude = Math.max(...data.map(Math.abs));

      setWaveformData({ data, maxAmplitude });

      animationFrameRef.current = requestAnimationFrame(updateWaveform);
    };

    updateWaveform();
  }, [isRecording, isPaused]);

  // Start duration timer
  const startDurationTimer = useCallback(() => {
    startTimeRef.current = Date.now();
    durationIntervalRef.current = window.setInterval(() => {
      setRecordingDuration((Date.now() - startTimeRef.current) / 1000);
    }, 100);
  }, []);

  // Stop duration timer
  const stopDurationTimer = useCallback(() => {
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }
    setRecordingDuration(0);
  }, []);

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      // Request permission if needed
      if (!hasPermission) {
        const granted = await requestPermission();
        if (!granted) return;
      }

      // Get media stream
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });

      streamRef.current = stream;

      // Initialize audio context for visualization
      initializeAudioContext(stream);

      // Create media recorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm;codecs=opus",
        });

        const audioUrl = URL.createObjectURL(audioBlob);
        const duration = recordingDuration;

        const newRecording: AudioRecording = {
          blob: audioBlob,
          url: audioUrl,
          duration,
          timestamp: Date.now(),
        };

        setRecording(newRecording);

        // Auto-transcribe if enabled
        if (settings.autoTranscribe && audioBlob.size > 0) {
          await transcribeRecording(newRecording);
        }

        // Cleanup
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();

      setIsRecording(true);
      setIsPaused(false);
      startDurationTimer();
      animateWaveform();
    } catch (error) {
      console.error("Failed to start recording:", error);
      onError?.(error as Error);
    }
  }, [
    hasPermission,
    requestPermission,
    initializeAudioContext,
    settings.autoTranscribe,
    recordingDuration,
    startDurationTimer,
    animateWaveform,
    onError,
  ]);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      stopDurationTimer();

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }

      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    }
  }, [isRecording, stopDurationTimer]);

  // Pause recording
  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    }
  }, [isRecording, isPaused]);

  // Resume recording
  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      animateWaveform();
    }
  }, [isRecording, isPaused, animateWaveform]);

  // Cancel recording
  const cancelRecording = useCallback(() => {
    stopRecording();
    setRecording(null);
    setRecordingDuration(0);
    audioChunksRef.current = [];
  }, [stopRecording]);

  // Transcribe recording
  const transcribeRecording = useCallback(
    async (recordingToTranscribe?: AudioRecording) => {
      const targetRecording = recordingToTranscribe || recording;

      if (!targetRecording) {
        console.warn("No recording to transcribe");
        return;
      }

      setTranscription({
        text: "",
        isTranscribing: true,
      });

      try {
        const result = await voiceApi.transcribeAudio(
          targetRecording.blob,
          settings.language,
        );

        setTranscription({
          text: result.text,
          isTranscribing: false,
          confidence: result.confidence,
          duration: result.duration,
        });

        onTranscription?.(result.text);
      } catch (error) {
        console.error("Transcription failed:", error);
        setTranscription({
          text: "",
          isTranscribing: false,
          error: (error as Error).message,
        });
        onError?.(error as Error);
      }
    },
    [recording, settings.language, onTranscription, onError],
  );

  // Text-to-speech
  const speak = useCallback(
    async (
      text: string,
      options: {
        speed?: number;
        voice?: string;
        language?: string;
      } = {},
    ) => {
      if (!settings.ttsEnabled) return;

      // Stop current speech if playing
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
      }

      setIsSpeaking(true);

      try {
        const audioBlob = await voiceApi.synthesizeAudioFile(text, {
          language: options.language || settings.language,
          speed: options.speed || settings.ttsSpeed,
          voice: options.voice || settings.ttsVoice,
          format: "mp3",
        });

        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);

        audio.onended = () => {
          setIsSpeaking(false);
          setCurrentAudio(null);
          URL.revokeObjectURL(audioUrl);
        };

        audio.onerror = (error) => {
          console.error("Audio playback error:", error);
          setIsSpeaking(false);
          setCurrentAudio(null);
          URL.revokeObjectURL(audioUrl);
        };

        setCurrentAudio(audio);
        await audio.play();
      } catch (error) {
        console.error("Text-to-speech failed:", error);
        setIsSpeaking(false);
        onError?.(error as Error);
      }
    },
    [settings, currentAudio, onError],
  );

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setIsSpeaking(false);
      setCurrentAudio(null);
    }
  }, [currentAudio]);

  // Update settings
  const updateSettings = useCallback((updates: Partial<VoiceSettings>) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Stop recording if active
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }

      // Stop stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      // Stop audio
      if (currentAudio) {
        currentAudio.pause();
      }

      // Cancel animation
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      // Clear timer
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }

      // Close audio context
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }

      // Revoke recording URL
      if (recording?.url) {
        URL.revokeObjectURL(recording.url);
      }
    };
  }, [isRecording, currentAudio, recording]);

  return {
    // Recording state
    isRecording,
    isPaused,
    recordingDuration,
    recording,
    waveformData,

    // Transcription state
    transcription,

    // TTS state
    isSpeaking,
    currentAudio,

    // Recording controls
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    cancelRecording,

    // Transcription
    transcribeRecording,

    // TTS
    speak,
    stopSpeaking,

    // Settings
    settings,
    updateSettings,

    // Permissions
    hasPermission,
    requestPermission,
  };
}
