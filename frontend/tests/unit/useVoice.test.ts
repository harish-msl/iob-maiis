/**
 * Unit Tests for useVoice Hook
 *
 * Tests voice recording, transcription, and text-to-speech functionality
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useVoice } from '@/components/voice/useVoice';
import * as voiceApi from '@/lib/api/voice';
import {
  createMockAudioBlob,
  mockMediaRecorder,
  mockApiSuccess,
  mockApiError,
} from '../utils/test-utils';

// Mock the voice API
jest.mock('@/lib/api/voice');

describe('useVoice Hook', () => {
  let mockRecorder: any;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock navigator.mediaDevices
    Object.defineProperty(navigator, 'mediaDevices', {
      writable: true,
      value: {
        getUserMedia: jest.fn().mockResolvedValue({
          getTracks: jest.fn(() => [
            {
              stop: jest.fn(),
              kind: 'audio',
              enabled: true,
            },
          ]),
          getAudioTracks: jest.fn(() => [
            {
              stop: jest.fn(),
              kind: 'audio',
              enabled: true,
            },
          ]),
        }),
      },
    });

    // Mock MediaRecorder
    mockRecorder = {
      start: jest.fn(),
      stop: jest.fn(),
      pause: jest.fn(),
      resume: jest.fn(),
      state: 'inactive',
      ondataavailable: null,
      onstop: null,
      onerror: null,
    };

    (global.MediaRecorder as any) = jest.fn(() => mockRecorder);
    (global.MediaRecorder as any).isTypeSupported = jest.fn(() => true);

    // Mock AudioContext
    global.AudioContext = jest.fn().mockImplementation(() => ({
      createAnalyser: jest.fn(() => ({
        connect: jest.fn(),
        disconnect: jest.fn(),
        fftSize: 2048,
        frequencyBinCount: 1024,
        getByteTimeDomainData: jest.fn(),
      })),
      createMediaStreamSource: jest.fn(() => ({
        connect: jest.fn(),
        disconnect: jest.fn(),
      })),
      close: jest.fn(),
      state: 'running',
    })) as any;

    // Mock HTMLAudioElement
    window.HTMLAudioElement.prototype.play = jest.fn().mockResolvedValue(undefined);
    window.HTMLAudioElement.prototype.pause = jest.fn();
    window.HTMLAudioElement.prototype.load = jest.fn();
  });

  describe('Initialization', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useVoice());

      expect(result.current.isRecording).toBe(false);
      expect(result.current.isPaused).toBe(false);
      expect(result.current.isTranscribing).toBe(false);
      expect(result.current.isSpeaking).toBe(false);
      expect(result.current.duration).toBe(0);
      expect(result.current.transcribedText).toBe('');
      expect(result.current.error).toBeNull();
    });

    it('should initialize with custom settings', () => {
      const settings = {
        language: 'es',
        autoTranscribe: false,
        ttsSpeed: 1.5,
      };

      const { result } = renderHook(() => useVoice(settings));

      expect(result.current.settings.language).toBe('es');
      expect(result.current.settings.autoTranscribe).toBe(false);
      expect(result.current.settings.ttsSpeed).toBe(1.5);
    });
  });

  describe('Permission Management', () => {
    it('should request microphone permission successfully', async () => {
      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.requestPermission();
      });

      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        audio: true,
      });
      expect(result.current.hasPermission).toBe(true);
    });

    it('should handle permission denial', async () => {
      const mockError = new Error('Permission denied');
      (navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValueOnce(
        mockError
      );

      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.requestPermission();
      });

      expect(result.current.hasPermission).toBe(false);
      expect(result.current.error).toBe('Microphone permission denied');
    });
  });

  describe('Recording', () => {
    it('should start recording', async () => {
      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      expect(mockRecorder.start).toHaveBeenCalled();
      expect(result.current.isRecording).toBe(true);
      expect(result.current.isPaused).toBe(false);
    });

    it('should stop recording', async () => {
      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      await act(async () => {
        result.current.stopRecording();
      });

      expect(mockRecorder.stop).toHaveBeenCalled();
      expect(result.current.isRecording).toBe(false);
    });

    it('should pause and resume recording', async () => {
      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      await act(async () => {
        result.current.pauseRecording();
      });

      expect(mockRecorder.pause).toHaveBeenCalled();
      expect(result.current.isPaused).toBe(true);

      await act(async () => {
        result.current.resumeRecording();
      });

      expect(mockRecorder.resume).toHaveBeenCalled();
      expect(result.current.isPaused).toBe(false);
    });

    it('should cancel recording and clear data', async () => {
      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      await act(async () => {
        result.current.cancelRecording();
      });

      expect(result.current.isRecording).toBe(false);
      expect(result.current.duration).toBe(0);
      expect(result.current.audioBlob).toBeNull();
    });

    it('should track recording duration', async () => {
      jest.useFakeTimers();
      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      act(() => {
        jest.advanceTimersByTime(3000); // 3 seconds
      });

      expect(result.current.duration).toBeGreaterThan(0);

      jest.useRealTimers();
    });
  });

  describe('Transcription', () => {
    it('should transcribe audio successfully', async () => {
      const mockTranscription = {
        text: 'Hello, this is a test transcription',
        language: 'en',
        confidence: 0.95,
        duration: 5.2,
      };

      (voiceApi.transcribeAudio as jest.Mock).mockResolvedValueOnce(
        mockTranscription
      );

      const { result } = renderHook(() => useVoice());
      const audioBlob = createMockAudioBlob();

      await act(async () => {
        await result.current.transcribe(audioBlob);
      });

      expect(voiceApi.transcribeAudio).toHaveBeenCalledWith(audioBlob, 'en');
      expect(result.current.transcribedText).toBe(mockTranscription.text);
      expect(result.current.isTranscribing).toBe(false);
    });

    it('should handle transcription error', async () => {
      const mockError = new Error('Transcription failed');
      (voiceApi.transcribeAudio as jest.Mock).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useVoice());
      const audioBlob = createMockAudioBlob();

      await act(async () => {
        await result.current.transcribe(audioBlob);
      });

      expect(result.current.error).toBe('Failed to transcribe audio');
      expect(result.current.isTranscribing).toBe(false);
    });

    it('should auto-transcribe when enabled', async () => {
      const mockTranscription = {
        text: 'Auto transcribed text',
        language: 'en',
        confidence: 0.95,
        duration: 3.0,
      };

      (voiceApi.transcribeAudio as jest.Mock).mockResolvedValueOnce(
        mockTranscription
      );

      const { result } = renderHook(() =>
        useVoice({ autoTranscribe: true })
      );

      await act(async () => {
        await result.current.startRecording();
      });

      // Simulate recording stop with data
      const audioBlob = createMockAudioBlob();

      await act(async () => {
        mockRecorder.ondataavailable?.({ data: audioBlob });
        mockRecorder.onstop?.();
      });

      await waitFor(() => {
        expect(result.current.transcribedText).toBe(mockTranscription.text);
      });
    });
  });

  describe('Text-to-Speech', () => {
    it('should synthesize and play speech', async () => {
      const mockAudioBlob = new Blob(['mock audio data'], { type: 'audio/mp3' });
      (voiceApi.synthesizeSpeechAudio as jest.Mock).mockResolvedValueOnce(
        mockAudioBlob
      );

      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.speak('Hello world');
      });

      expect(voiceApi.synthesizeSpeechAudio).toHaveBeenCalledWith(
        'Hello world',
        'en',
        1.0
      );
      expect(result.current.isSpeaking).toBe(false); // After completion
    });

    it('should handle TTS error', async () => {
      const mockError = new Error('TTS failed');
      (voiceApi.synthesizeSpeechAudio as jest.Mock).mockRejectedValueOnce(
        mockError
      );

      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.speak('Hello world');
      });

      expect(result.current.error).toBe('Failed to synthesize speech');
      expect(result.current.isSpeaking).toBe(false);
    });

    it('should stop speaking', async () => {
      const mockAudioBlob = new Blob(['mock audio data'], { type: 'audio/mp3' });
      (voiceApi.synthesizeSpeechAudio as jest.Mock).mockResolvedValueOnce(
        mockAudioBlob
      );

      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.speak('Hello world');
      });

      act(() => {
        result.current.stopSpeaking();
      });

      expect(result.current.isSpeaking).toBe(false);
    });
  });

  describe('Settings', () => {
    it('should update language setting', () => {
      const { result } = renderHook(() => useVoice());

      act(() => {
        result.current.updateSettings({ language: 'es' });
      });

      expect(result.current.settings.language).toBe('es');
    });

    it('should update auto-transcribe setting', () => {
      const { result } = renderHook(() => useVoice());

      act(() => {
        result.current.updateSettings({ autoTranscribe: false });
      });

      expect(result.current.settings.autoTranscribe).toBe(false);
    });

    it('should update TTS speed setting', () => {
      const { result } = renderHook(() => useVoice());

      act(() => {
        result.current.updateSettings({ ttsSpeed: 1.5 });
      });

      expect(result.current.settings.ttsSpeed).toBe(1.5);
    });
  });

  describe('Error Handling', () => {
    it('should clear error', () => {
      const { result } = renderHook(() => useVoice());

      // Set an error
      act(() => {
        (result.current as any).setError('Test error');
      });

      expect(result.current.error).toBe('Test error');

      // Clear error
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });

    it('should handle recording without permission', async () => {
      (navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValueOnce(
        new Error('Permission denied')
      );

      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      expect(result.current.error).toBeTruthy();
      expect(result.current.isRecording).toBe(false);
    });
  });

  describe('Cleanup', () => {
    it('should cleanup resources on unmount', async () => {
      const { result, unmount } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      unmount();

      // Verify cleanup was called
      expect(mockRecorder.stop).toHaveBeenCalled();
    });

    it('should stop media stream on cleanup', async () => {
      const mockStop = jest.fn();
      const mockGetTracks = jest.fn(() => [{ stop: mockStop }]);

      (navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValueOnce({
        getTracks: mockGetTracks,
        getAudioTracks: mockGetTracks,
      });

      const { result, unmount } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      unmount();

      expect(mockStop).toHaveBeenCalled();
    });
  });

  describe('Waveform Data', () => {
    it('should provide waveform data during recording', async () => {
      const { result } = renderHook(() => useVoice());

      await act(async () => {
        await result.current.startRecording();
      });

      // Waveform data should be available
      expect(result.current.waveformData).toBeDefined();
      expect(Array.isArray(result.current.waveformData)).toBe(true);
    });
  });
});
