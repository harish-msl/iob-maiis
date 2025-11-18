# Speech Provider Integration Guide

**IOB MAIIS - Production Speech/TTS Provider Documentation**

This guide covers the integration of production-grade Speech-to-Text (STT) and Text-to-Speech (TTS) providers in the IOB MAIIS banking assistant.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Supported Providers](#supported-providers)
4. [Quick Start](#quick-start)
5. [Provider Configuration](#provider-configuration)
6. [API Usage](#api-usage)
7. [Fallback & Resilience](#fallback--resilience)
8. [Cost Optimization](#cost-optimization)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Features](#advanced-features)

---

## Overview

The speech service uses a modular provider architecture that supports multiple STT and TTS providers with automatic fallback. This ensures high availability and allows you to choose the best provider for your needs.

### Key Features

- 🎯 **Multiple Provider Support**: OpenAI Whisper, ElevenLabs, Google Cloud, Azure, and more
- 🔄 **Automatic Fallback**: Gracefully falls back to alternative providers if primary fails
- 🚀 **Production Ready**: Built for scale with retry logic, timeouts, and error handling
- 💰 **Cost Efficient**: Mix and match providers based on quality and budget needs
- 🔧 **Easy Configuration**: Simple environment variable configuration
- 📊 **Monitoring**: Built-in health checks and logging

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Speech Service                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Provider Factory                         │  │
│  └────────────┬─────────────────────────┬────────────────┘  │
│               │                         │                    │
│       ┌───────▼─────────┐       ┌──────▼────────┐          │
│       │  STT Provider   │       │  TTS Provider │          │
│       │   (Primary)     │       │   (Primary)   │          │
│       └───────┬─────────┘       └──────┬────────┘          │
│               │                         │                    │
│       ┌───────▼─────────┐       ┌──────▼────────┐          │
│       │  STT Provider   │       │  TTS Provider │          │
│       │   (Fallback)    │       │   (Fallback)  │          │
│       └─────────────────┘       └───────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Provider Interface

All providers implement standard interfaces:

**STTProvider**:
- `transcribe()` - Convert audio to text
- `detect_language()` - Detect spoken language
- `check_health()` - Verify provider availability

**TTSProvider**:
- `synthesize()` - Convert text to speech
- `list_voices()` - Get available voices
- `check_health()` - Verify provider availability

---

## Supported Providers

### Speech-to-Text (STT)

| Provider | Quality | Speed | Cost | Languages | Notes |
|----------|---------|-------|------|-----------|-------|
| **OpenAI Whisper** | ⭐⭐⭐⭐⭐ | Fast | $0.006/min | 90+ | Best overall, multilingual |
| **Google Cloud** | ⭐⭐⭐⭐ | Fast | $0.006/15s | 120+ | Good integration options |
| **Azure Speech** | ⭐⭐⭐⭐ | Fast | $1/hour | 100+ | Enterprise features |
| **Placeholder (Free)** | ⭐⭐ | Slow | Free | 50+ | Google Speech Recognition API |

### Text-to-Speech (TTS)

| Provider | Quality | Speed | Cost | Voices | Notes |
|----------|---------|-------|------|--------|-------|
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | Fast | $5-22/mo | 100+ | Most natural, emotional voices |
| **OpenAI TTS** | ⭐⭐⭐⭐ | Fast | $15/1M chars | 6 | Good quality, simple API |
| **Google Cloud** | ⭐⭐⭐⭐ | Fast | $4/1M chars | 400+ | Wide language support |
| **Azure Speech** | ⭐⭐⭐⭐ | Fast | $16/1M chars | 400+ | Neural voices available |
| **Placeholder (Free)** | ⭐⭐ | Slow | Free | Limited | gTTS (Google Text-to-Speech) |

---

## Quick Start

### 1. Production Setup (Recommended)

**OpenAI Whisper + ElevenLabs** - Best quality for production

```bash
# In backend/.env
STT_PROVIDER=openai
TTS_PROVIDER=elevenlabs

# API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# Enable fallback
ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=true
```

**Get API Keys**:
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys

### 2. Development Setup

**Free placeholder providers** - No API keys needed

```bash
# In backend/.env
STT_PROVIDER=placeholder
TTS_PROVIDER=placeholder

# No API keys required
ENABLE_STT_FALLBACK=false
ENABLE_TTS_FALLBACK=false
```

### 3. Hybrid Setup

**OpenAI STT + Free TTS** - Good quality STT, save on TTS

```bash
# In backend/.env
STT_PROVIDER=openai
TTS_PROVIDER=placeholder

OPENAI_API_KEY=sk-your-openai-key-here
ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=false
```

### 4. Verify Installation

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Test the service
python -c "
from app.services.speech_service import get_speech_service
import asyncio

async def test():
    service = get_speech_service()
    health = await service.check_health()
    print('Health Status:', health)

asyncio.run(test())
"
```

---

## Provider Configuration

### OpenAI Whisper (STT)

```bash
# Required
OPENAI_API_KEY=sk-proj-...

# Optional - Advanced Settings
OPENAI_WHISPER_MODEL=whisper-1          # Model version
OPENAI_WHISPER_TIMEOUT=30               # API timeout (seconds)
OPENAI_WHISPER_MAX_RETRIES=3            # Retry attempts
```

**Features**:
- 99%+ accuracy for English
- Automatic language detection
- Handles accents and background noise well
- Timestamp information available
- Supports 90+ languages

**Pricing**: ~$0.006 per minute of audio

### ElevenLabs (TTS)

```bash
# Required
ELEVENLABS_API_KEY=your-api-key

# Voice Configuration
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel (default)
ELEVENLABS_MODEL_ID=eleven_monolingual_v1

# Voice Settings (0.0 - 1.0)
ELEVENLABS_STABILITY=0.5                   # Consistency
ELEVENLABS_SIMILARITY_BOOST=0.75           # Voice accuracy
ELEVENLABS_TIMEOUT=30
```

**Popular Voices**:
- `21m00Tcm4TlvDq8ikWAM` - Rachel (warm female, professional)
- `pNInz6obpgDQGcFmaJgB` - Adam (deep male, authoritative)
- `EXAVITQu4vr4xnSDxMaL` - Bella (soft female, friendly)
- `ErXwobaYiN019PkySvjV` - Antoni (male, well-rounded)

**Pricing**:
- Free: 10,000 characters/month
- Starter: $5/month (30,000 characters)
- Creator: $22/month (100,000 characters)

### Google Cloud Speech

```bash
# Required
GOOGLE_CLOUD_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# STT Configuration
GOOGLE_CLOUD_STT_MODEL=latest_long

# TTS Configuration
GOOGLE_CLOUD_TTS_VOICE=en-US-Neural2-C
```

### Azure Speech

```bash
# Required
AZURE_SPEECH_KEY=your-subscription-key
AZURE_SPEECH_REGION=eastus

# TTS Voice
AZURE_TTS_VOICE=en-US-AriaNeural
```

---

## API Usage

### Speech-to-Text (Transcription)

```python
from app.services.speech_service import get_speech_service

# Get service instance
speech_service = get_speech_service()

# Transcribe audio file
with open("audio.wav", "rb") as f:
    audio_data = f.read()

result = await speech_service.transcribe_audio(
    audio_data=audio_data,
    language="en",
    format="wav"
)

print(f"Transcription: {result['text']}")
print(f"Duration: {result['duration']}s")
print(f"Confidence: {result['confidence']}")
print(f"Word count: {result['word_count']}")
print(f"Provider: {result['provider']}")
```

**Response Format**:
```json
{
  "text": "Hello, I would like to check my account balance.",
  "language": "en",
  "duration": 3.5,
  "confidence": 0.95,
  "word_count": 9,
  "provider": "openai-whisper",
  "segments": [...]  // Word-level timing (if available)
}
```

### Text-to-Speech (Synthesis)

```python
from app.services.speech_service import get_speech_service

speech_service = get_speech_service()

# Synthesize speech
audio_bytes = await speech_service.synthesize_speech(
    text="Your account balance is $1,234.56",
    language="en",
    voice="21m00Tcm4TlvDq8ikWAM",  # ElevenLabs Rachel
    speed=1.0,
    format="mp3"
)

# Save to file
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

### List Available Voices

```python
# Get available voices
voices = await speech_service.list_voices(language="en")

for voice in voices:
    print(f"{voice['name']} ({voice['id']})")
    print(f"  Category: {voice['category']}")
    print(f"  Description: {voice['description']}")
```

### Language Detection

```python
# Detect language from audio
with open("audio.wav", "rb") as f:
    audio_data = f.read()

language = await speech_service.detect_language(audio_data)
print(f"Detected language: {language}")
```

### Health Check

```python
# Check provider health
health = await speech_service.check_health()

print(f"Service status: {health['service']}")
for provider_name, status in health['providers'].items():
    print(f"{provider_name}: {status['status']}")
```

---

## Fallback & Resilience

### How Fallback Works

1. **Primary Provider Attempt**: Service tries the configured primary provider
2. **Failure Detection**: If primary fails (timeout, API error, quota exceeded)
3. **Fallback Activation**: Automatically switches to fallback provider
4. **Logging**: All failures and fallbacks are logged for monitoring

### Configuration

```bash
# Enable automatic fallback
ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=true

# Primary providers (high quality, paid)
STT_PROVIDER=openai
TTS_PROVIDER=elevenlabs

# Fallback providers (free, local)
# Automatically uses placeholder providers
```

### Example Flow

```
User Request → Primary (OpenAI Whisper)
                  ↓ (API Error)
              Fallback (Google Speech Recognition)
                  ↓ (Success)
              Return Result
```

### Retry Logic

- **Automatic Retries**: 3 attempts with exponential backoff (2^n seconds)
- **Timeout Protection**: Configurable timeouts prevent hanging requests
- **Circuit Breaker**: Future enhancement to prevent cascading failures

---

## Cost Optimization

### Strategy 1: Hybrid Providers

Use premium STT (high accuracy needed) + free TTS (quality less critical):

```bash
STT_PROVIDER=openai        # $0.006/min - high accuracy
TTS_PROVIDER=placeholder   # Free - acceptable quality
```

**Savings**: ~90% vs using premium for both

### Strategy 2: Conditional Quality

Use different providers based on use case:

```python
# High-value transaction → Premium STT
if transaction_amount > 1000:
    provider = "openai"
else:
    provider = "placeholder"
```

### Strategy 3: Caching

Cache TTS results for common phrases:

```python
# Common banking responses
cached_responses = {
    "balance_greeting": audio_bytes_cached,
    "transaction_confirmation": audio_bytes_cached
}
```

### Strategy 4: Batch Processing

Process multiple requests together to reduce API calls:

```python
# Batch transcription
results = await batch_transcribe([audio1, audio2, audio3])
```

### Monthly Cost Examples

**Small Scale** (100 users, 10 min/user/month):
- STT: 1000 min × $0.006 = **$6**
- TTS: ~50K chars × $0.005 = **$0.25** (ElevenLabs free tier)
- **Total: ~$6.25/month**

**Medium Scale** (1000 users, 10 min/user/month):
- STT: 10,000 min × $0.006 = **$60**
- TTS: ~500K chars → **$22/month** (ElevenLabs Creator)
- **Total: ~$82/month**

**Large Scale** (10,000 users, 10 min/user/month):
- STT: 100,000 min × $0.006 = **$600**
- TTS: ~5M chars × $0.005 = **$25** (Custom pricing)
- **Total: ~$625/month**

---

## Troubleshooting

### Common Issues

#### 1. API Key Errors

```
Error: OpenAI API key not configured
```

**Solution**:
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Set in .env file
OPENAI_API_KEY=sk-proj-...

# Restart service
docker-compose restart backend
```

#### 2. Provider Timeout

```
Error: OpenAI Whisper API timeout
```

**Solution**:
```bash
# Increase timeout
OPENAI_WHISPER_TIMEOUT=60

# Enable fallback
ENABLE_STT_FALLBACK=true
```

#### 3. Audio Format Issues

```
Error: Unsupported audio format
```

**Solution**:
- Ensure audio is in supported format (wav, mp3, ogg, flac, m4a)
- Check sample rate (16000 Hz recommended)
- Verify file is not corrupted

#### 4. Quota Exceeded

```
Error: You exceeded your current quota
```

**Solution**:
1. Check your API usage dashboard
2. Enable fallback provider
3. Upgrade API plan
4. Implement rate limiting

#### 5. Poor Transcription Quality

**Solutions**:
- Improve audio quality (reduce background noise)
- Use higher sample rate (16000 Hz minimum)
- Specify correct language
- Try different STT provider
- Enable noise reduction preprocessing

### Testing Providers

```bash
# Test STT provider
curl -X POST http://localhost:8000/api/v1/voice/transcribe \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@test.wav" \
  -F "language=en"

# Test TTS provider
curl -X POST http://localhost:8000/api/v1/voice/synthesize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "language": "en"}' \
  --output test_output.mp3

# Check health
curl http://localhost:8000/api/v1/voice/health
```

### Debugging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Check provider health
health = await speech_service.check_health()
print(json.dumps(health, indent=2))
```

---

## Advanced Features

### Custom Voice Selection

```python
# List all available voices
voices = await speech_service.list_voices()

# Filter by category
professional_voices = [
    v for v in voices 
    if v['category'] == 'professional'
]

# Use specific voice
audio = await speech_service.synthesize_speech(
    text="Welcome to our bank",
    voice=professional_voices[0]['id']
)
```

### Audio Processing

```python
# Get audio metadata
info = await speech_service.get_audio_info(
    audio_data=audio_bytes,
    format="wav"
)
print(f"Duration: {info['duration']}s")
print(f"Sample rate: {info['sample_rate']} Hz")

# Trim silence
trimmed_audio = await speech_service.trim_silence(
    audio_data=audio_bytes,
    format="wav",
    silence_thresh=-50
)
```

### Multi-language Support

```python
# Auto-detect and transcribe
result = await speech_service.transcribe_audio(
    audio_data=audio_bytes,
    language="auto"  # Auto-detect
)

# Get detected language
detected_lang = result['language']

# Respond in same language
response = await speech_service.synthesize_speech(
    text=translated_response,
    language=detected_lang
)
```

### Streaming (Future Enhancement)

```python
# Real-time streaming transcription
async for chunk in speech_service.stream_transcribe(audio_stream):
    print(f"Partial: {chunk['text']}")
    
# Real-time streaming synthesis
async for audio_chunk in speech_service.stream_synthesize(text):
    await play_audio(audio_chunk)
```

---

## Best Practices

### 1. Always Enable Fallback in Production

```bash
ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=true
```

### 2. Set Appropriate Timeouts

```bash
# Balance between user experience and cost
OPENAI_WHISPER_TIMEOUT=30
ELEVENLABS_TIMEOUT=30
```

### 3. Monitor Usage and Costs

```python
# Track API usage
metrics = {
    'stt_calls': counter,
    'tts_calls': counter,
    'fallback_triggers': counter,
    'errors': counter
}
```

### 4. Cache Common Responses

```python
# Cache frequently used TTS outputs
@lru_cache(maxsize=100)
async def get_cached_tts(text: str, voice: str):
    return await speech_service.synthesize_speech(text, voice=voice)
```

### 5. Validate Audio Input

```python
# Check audio before processing
if audio_size > MAX_SIZE:
    raise ValueError("Audio too large")
if duration > MAX_DURATION:
    raise ValueError("Audio too long")
```

### 6. Implement Rate Limiting

```python
# Prevent abuse
@limiter.limit("100/hour")
async def transcribe_endpoint():
    ...
```

### 7. Use Environment-Specific Configs

```bash
# Development
STT_PROVIDER=placeholder
TTS_PROVIDER=placeholder

# Staging
STT_PROVIDER=openai
TTS_PROVIDER=placeholder

# Production
STT_PROVIDER=openai
TTS_PROVIDER=elevenlabs
```

---

## Migration Guide

### From Placeholder to Production

**Step 1**: Get API keys
```bash
# Sign up and get keys
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
```

**Step 2**: Update configuration
```bash
# Change providers
STT_PROVIDER=openai
TTS_PROVIDER=elevenlabs

# Keep fallback enabled during migration
ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=true
```

**Step 3**: Test thoroughly
```bash
# Run integration tests
pytest tests/integration/test_speech_providers.py -v

# Test with real audio
python scripts/test_speech.py
```

**Step 4**: Monitor after deployment
```bash
# Watch logs
docker-compose logs -f backend | grep -i speech

# Check health endpoint
curl http://localhost:8000/api/v1/voice/health
```

---

## Support & Resources

### Documentation
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [ElevenLabs API](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [Google Cloud Speech](https://cloud.google.com/speech-to-text/docs)
- [Azure Speech Services](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/)

### Related Docs
- `VOICE_INTERFACE.md` - Frontend voice interface guide
- `VOICE_QUICKSTART.md` - Quick setup guide
- `API_REFERENCE.md` - Voice API endpoints
- `TESTING_GUIDE.md` - Testing voice features

### Getting Help
- Check logs: `docker-compose logs backend`
- Health check: `/api/v1/voice/health`
- GitHub Issues: Report bugs and feature requests

---

**Last Updated**: 2025-01-17  
**Version**: 1.0.0  
**Maintainer**: IOB MAIIS Team