# Voice Interface - Quick Start Guide

## 🎤 Overview

The Voice Interface provides speech-to-text transcription, text-to-speech synthesis, and audio recording capabilities for the RAG Multimodal Banking Assistant.

**Implementation Status:** ✅ Complete  
**Lines of Code:** ~1,550  
**Components:** 7

---

## 🚀 Quick Start

### 1. Basic Usage in Chat

The voice button is already integrated into the chat input:

```tsx
// Chat page automatically includes voice controls
import { ChatInput } from '@/components/chat/ChatInput';

<ChatInput onSendMessage={handleSend} />
```

**User Flow:**
1. Click the microphone icon 🎤 in chat input
2. Grant microphone permission (first time only)
3. Click "Start Recording"
4. Speak your message
5. Click "Stop Recording"
6. Click "Transcribe"
7. Transcribed text auto-fills the input
8. Send message as normal

### 2. Standalone Voice Controls

Use the `VoiceControls` component anywhere:

```tsx
import { VoiceControls } from '@/components/voice';

export function MyComponent() {
  const handleTranscription = (text: string) => {
    console.log('User said:', text);
    // Do something with the transcribed text
  };

  return (
    <VoiceControls
      onTranscription={handleTranscription}
      onError={(error) => console.error(error)}
    />
  );
}
```

### 3. Custom Voice Hook

For complete control, use the `useVoice` hook:

```tsx
import { useVoice } from '@/components/voice';

export function CustomRecorder() {
  const voice = useVoice({
    autoTranscribe: true,
    language: 'en-US',
    onTranscription: (text) => {
      console.log('Transcribed:', text);
    },
  });

  return (
    <div>
      <button onClick={voice.startRecording}>
        {voice.isRecording ? '⏹️ Stop' : '🎤 Record'}
      </button>
      
      {voice.transcription.text && (
        <p>{voice.transcription.text}</p>
      )}
      
      <button onClick={() => voice.speak('Hello world')}>
        🔊 Speak
      </button>
    </div>
  );
}
```

---

## 📋 Common Use Cases

### Recording & Transcription

```tsx
const voice = useVoice({
  autoTranscribe: true,
  language: 'en-US',
});

// Start recording
await voice.startRecording();

// Stop recording (auto-transcribe if enabled)
voice.stopRecording();

// Manual transcription
await voice.transcribeRecording();

// Access result
const text = voice.transcription.text;
const confidence = voice.transcription.confidence;
```

### Text-to-Speech

```tsx
const voice = useVoice();

// Basic TTS
await voice.speak('Hello, welcome to our banking service!');

// With options
await voice.speak('Hello!', {
  speed: 1.5,        // 0.5x to 2.0x
  language: 'en-US',
  voice: 'female',   // if supported
});

// Stop speaking
voice.stopSpeaking();
```

### Multi-Language Support

```tsx
const voice = useVoice({
  language: 'es-ES', // Spanish
});

// Change language dynamically
voice.updateSettings({ language: 'fr-FR' }); // French

// Supported languages:
// en-US, en-GB, es-ES, fr-FR, de-DE, it-IT,
// pt-PT, zh-CN, ja-JP, ko-KR
```

### Permission Handling

```tsx
const voice = useVoice();

// Check permission status
if (!voice.hasPermission) {
  const granted = await voice.requestPermission();
  
  if (!granted) {
    alert('Microphone access required');
  }
}

// Start recording only if permitted
if (voice.hasPermission) {
  await voice.startRecording();
}
```

---

## 🎨 Component Examples

### VoiceRecorder Component

```tsx
import { VoiceRecorder } from '@/components/voice';

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
  onSend={() => voice.transcribeRecording()}
/>
```

**Features:**
- 40-bar animated waveform
- Duration timer (MM:SS format)
- Pause/resume controls
- Visual recording indicator

### AudioPlayer Component

```tsx
import { AudioPlayer } from '@/components/voice';

<AudioPlayer
  audio={voice.currentAudio}
  isPlaying={voice.isSpeaking}
  onPlay={() => voice.currentAudio?.play()}
  onPause={() => voice.currentAudio?.pause()}
  onStop={voice.stopSpeaking}
/>
```

**Features:**
- Progress bar with seek
- Play/pause/restart controls
- Volume slider with mute
- Time display

### VoiceControls Component

```tsx
import { VoiceControls } from '@/components/voice';

// Full interface
<VoiceControls
  onTranscription={(text) => handleText(text)}
  onError={(error) => handleError(error)}
/>

// Compact mode (icon only)
<VoiceControls
  compact={true}
  onTranscription={handleText}
/>
```

**Features:**
- Complete recording interface
- Settings panel
- Permission request UI
- TTS test input
- Error handling

---

## ⚙️ Configuration

### Voice Settings

```tsx
const voice = useVoice();

// Update settings
voice.updateSettings({
  language: 'en-US',      // Transcription language
  autoTranscribe: true,   // Auto-transcribe after recording
  ttsEnabled: true,       // Enable text-to-speech
  ttsSpeed: 1.2,         // Speech speed (0.5 - 2.0)
  ttsVoice: 'female',    // Voice selection (if available)
});

// Access current settings
console.log(voice.settings);
```

### API Configuration

The voice API client is pre-configured:

```tsx
import { voiceApi } from '@/lib/api/voice';

// Transcribe audio file
const result = await voiceApi.transcribeAudio(audioFile, 'en-US');

// Transcribe base64
const result = await voiceApi.transcribeBase64(
  base64Audio,
  'en-US',
  'wav'
);

// Generate speech
const audio = await voiceApi.synthesizeAudioFile('Hello!', {
  language: 'en-US',
  speed: 1.0,
  format: 'mp3',
});
```

---

## 🔧 Advanced Usage

### Custom Waveform Visualization

```tsx
const voice = useVoice();

// Access waveform data
const { data, maxAmplitude } = voice.waveformData;

// data: number[] - Array of amplitude values (-1 to 1)
// maxAmplitude: number - Peak amplitude in current frame

// Render custom visualization
<canvas ref={canvasRef} />
<script>
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Draw waveform
    data.forEach((value, index) => {
      const height = Math.abs(value) * 100;
      ctx.fillRect(index * 5, 50 - height/2, 3, height);
    });
  }, [data]);
</script>
```

### Recording with Pause/Resume

```tsx
const voice = useVoice();

// Start recording
await voice.startRecording();

// Pause (waveform freezes)
voice.pauseRecording();

// Resume (waveform resumes)
voice.resumeRecording();

// Stop (generates final recording)
voice.stopRecording();

// Cancel (discards recording)
voice.cancelRecording();
```

### Error Handling

```tsx
const voice = useVoice({
  onError: (error) => {
    if (error.message.includes('permission')) {
      alert('Please grant microphone access');
    } else if (error.message.includes('network')) {
      alert('Network error. Please try again.');
    } else {
      console.error('Voice error:', error);
    }
  },
});
```

### State Management

```tsx
const voice = useVoice();

// Recording state
voice.isRecording    // boolean
voice.isPaused       // boolean
voice.recordingDuration // number (seconds)
voice.recording      // AudioRecording | null
voice.waveformData   // WaveformData

// Transcription state
voice.transcription.text         // string
voice.transcription.isTranscribing // boolean
voice.transcription.confidence   // number (0-1)
voice.transcription.duration     // number (seconds)
voice.transcription.error        // string | undefined

// TTS state
voice.isSpeaking     // boolean
voice.currentAudio   // HTMLAudioElement | null

// Permission state
voice.hasPermission  // boolean
```

---

## 🧪 Testing

### Manual Testing Checklist

```bash
# 1. Permission
□ Click voice button
□ Grant microphone permission
□ Verify permission granted

# 2. Recording
□ Start recording
□ Verify waveform animating
□ Verify duration timer running
□ Speak clearly
□ Stop recording
□ Verify recording saved

# 3. Transcription
□ Click "Transcribe"
□ Verify loading indicator
□ Verify transcribed text displayed
□ Verify confidence score shown
□ Check text accuracy

# 4. TTS
□ Enter text in TTS input
□ Click speak button
□ Verify audio plays
□ Test pause/resume
□ Test volume control
□ Test speed adjustment

# 5. Chat Integration
□ Click mic in chat input
□ Record voice message
□ Transcribe
□ Verify text auto-fills chat input
□ Send message
```

### Browser Testing

**Supported Browsers:**
- ✅ Chrome 47+
- ✅ Firefox 25+
- ✅ Edge 79+
- ✅ Safari 14.1+
- ❌ Internet Explorer (not supported)

**Testing Checklist:**
```bash
# Chrome
□ Voice recording works
□ Waveform visualization smooth
□ TTS playback works

# Firefox
□ Voice recording works
□ Permission dialog appears
□ Audio playback works

# Safari
□ Request permission explicitly
□ Test audio recording
□ Test playback controls

# Edge
□ Full functionality test
□ Check waveform performance
```

---

## 🐛 Troubleshooting

### Microphone Not Working

```typescript
// Check permission status
const permission = await navigator.permissions.query({ 
  name: 'microphone' 
});

if (permission.state === 'denied') {
  alert('Microphone access denied. Please enable in browser settings.');
}

// Check if getUserMedia is supported
if (!navigator.mediaDevices?.getUserMedia) {
  alert('Voice recording not supported in this browser');
}
```

### No Audio Output

```typescript
// Check if browser supports audio
const audio = new Audio();
const canPlayMP3 = audio.canPlayType('audio/mp3');
const canPlayWAV = audio.canPlayType('audio/wav');

if (!canPlayMP3 && !canPlayWAV) {
  alert('Audio playback not supported');
}

// Check volume
if (voice.currentAudio) {
  console.log('Volume:', voice.currentAudio.volume);
  console.log('Muted:', voice.currentAudio.muted);
}
```

### Transcription Fails

```typescript
// Check recording
if (!voice.recording?.blob) {
  console.error('No recording available');
}

// Check file size
if (voice.recording?.blob.size === 0) {
  console.error('Recording is empty');
}

// Check network
try {
  await voiceApi.transcribeAudio(audioBlob);
} catch (error) {
  if (error.response?.status === 401) {
    console.error('Authentication required');
  } else if (error.response?.status === 413) {
    console.error('File too large');
  } else {
    console.error('Network error:', error);
  }
}
```

### HTTPS Required

```bash
# Voice features require HTTPS in production
# For local development:

# Option 1: Use localhost (automatically secure)
npm run dev
# Access at http://localhost:3000

# Option 2: Use ngrok for HTTPS
ngrok http 3000
# Access at https://xxxx.ngrok.io

# Option 3: Generate local SSL certificate
mkcert localhost
npm run dev -- --https
```

---

## 📊 Performance Tips

### Optimize Recording

```tsx
// Use smaller FFT size for better performance
const audioContext = new AudioContext();
const analyser = audioContext.createAnalyser();
analyser.fftSize = 128; // Smaller = better performance

// Sample waveform data
const sampleRate = 20; // Hz (lower = better performance)
```

### Lazy Load Voice Components

```tsx
import dynamic from 'next/dynamic';

// Lazy load voice controls (saves initial bundle size)
const VoiceControls = dynamic(
  () => import('@/components/voice').then(mod => mod.VoiceControls),
  { ssr: false }
);
```

### Cache TTS Audio

```tsx
const audioCache = new Map<string, Blob>();

const speakWithCache = async (text: string) => {
  // Check cache
  if (audioCache.has(text)) {
    const cachedAudio = audioCache.get(text)!;
    const url = URL.createObjectURL(cachedAudio);
    const audio = new Audio(url);
    await audio.play();
    return;
  }
  
  // Generate and cache
  const audioBlob = await voiceApi.synthesizeAudioFile(text);
  audioCache.set(text, audioBlob);
  
  const url = URL.createObjectURL(audioBlob);
  const audio = new Audio(url);
  await audio.play();
};
```

---

## 🔐 Security Notes

### HTTPS Requirement

```bash
# Production MUST use HTTPS
# Microphone access is blocked on non-HTTPS origins
# (except localhost for development)

# ✅ Allowed
https://yourapp.com
http://localhost:3000
http://127.0.0.1:3000

# ❌ Blocked
http://yourapp.com
http://192.168.1.100:3000
```

### Permission Best Practices

```tsx
// 1. Request permission only when needed
// DON'T request on page load
// DO request when user clicks voice button

// 2. Handle permission denial gracefully
const voice = useVoice({
  onError: (error) => {
    if (error.message.includes('permission')) {
      showPermissionDialog();
    }
  },
});

// 3. Show clear permission UI
{!voice.hasPermission && (
  <Alert>
    Microphone access required for voice input.
    <Button onClick={voice.requestPermission}>
      Grant Permission
    </Button>
  </Alert>
)}
```

### Data Privacy

```tsx
// Voice recordings are NOT stored by default
// Transcriptions are sent to backend for processing
// TTS text is sent to speech synthesis API

// To implement recording storage:
const saveRecording = async (recording: AudioRecording) => {
  const formData = new FormData();
  formData.append('audio', recording.blob);
  
  await apiClient.post('/api/recordings', formData);
};
```

---

## 📚 API Reference

### useVoice Hook

```typescript
interface UseVoiceOptions {
  onTranscription?: (text: string) => void;
  onError?: (error: Error) => void;
  autoTranscribe?: boolean;
  language?: string;
}

const voice = useVoice(options);

// Recording Methods
voice.startRecording(): Promise<void>
voice.stopRecording(): void
voice.pauseRecording(): void
voice.resumeRecording(): void
voice.cancelRecording(): void

// Transcription Methods
voice.transcribeRecording(recording?: AudioRecording): Promise<void>

// TTS Methods
voice.speak(text: string, options?: SpeakOptions): Promise<void>
voice.stopSpeaking(): void

// Settings Methods
voice.updateSettings(updates: Partial<VoiceSettings>): void

// Permission Methods
voice.requestPermission(): Promise<boolean>
```

### Voice API Client

```typescript
// Transcription
voiceApi.transcribeAudio(
  audioFile: File | Blob,
  language?: string
): Promise<TranscriptionResult>

voiceApi.transcribeBase64(
  audioBase64: string,
  language?: string,
  format?: string
): Promise<TranscriptionResult>

// Text-to-Speech
voiceApi.synthesizeSpeech(
  text: string,
  options?: SynthesisOptions
): Promise<SynthesisResult>

voiceApi.synthesizeAudioFile(
  text: string,
  options?: SynthesisOptions
): Promise<Blob>
```

---

## 🎯 Next Steps

1. **Try the Chat Integration**
   - Open chat page
   - Click microphone icon
   - Record and transcribe

2. **Test TTS**
   - Open voice controls
   - Enter text in TTS input
   - Click speak button

3. **Explore Settings**
   - Change language
   - Adjust speech speed
   - Toggle auto-transcribe

4. **Customize**
   - Use `useVoice` hook in your components
   - Build custom voice interfaces
   - Integrate with your workflows

---

## 💡 Tips & Tricks

### Quick Voice Message in Chat

```bash
1. Click mic icon 🎤
2. Click "Start Recording"
3. Speak your message
4. Click "Stop"
5. Click "Transcribe"
6. Text auto-fills → Click "Send"
```

### Keyboard Shortcuts (TODO)

```tsx
// Future enhancement: keyboard shortcuts
// Space: Toggle recording
// Enter: Send transcription
// Escape: Cancel recording
```

### Best Recording Practices

- 🎤 Speak clearly and at a normal pace
- 🔇 Minimize background noise
- 📏 Keep recordings under 1 minute for best results
- 🌐 Use correct language setting
- ✅ Test microphone before important recordings

---

## 📞 Support

**Issues?**
- Check browser console for errors
- Verify HTTPS/localhost
- Check microphone permissions
- Test in different browser

**Documentation:**
- `VOICE_INTERFACE_COMPLETE.md` - Full technical documentation
- `PROJECT_STATUS.md` - Overall project status
- Backend API docs at `/docs` (when running)

---

**Version:** 1.0  
**Last Updated:** 2025-01-17  
**Status:** ✅ Production Ready