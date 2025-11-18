# Speech Providers - Quick Reference

**Production-ready Speech/TTS integration for IOB MAIIS**

---

## 🚀 Quick Start

### 1. Production Setup (Recommended)

```bash
# In backend/.env
STT_PROVIDER=openai
TTS_PROVIDER=elevenlabs

OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here

ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=true
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys

### 2. Development Setup (Free)

```bash
# In backend/.env
STT_PROVIDER=placeholder
TTS_PROVIDER=placeholder
```

No API keys needed!

---

## 📦 Installation

```bash
cd backend
pip install -r requirements.txt
```

**New dependencies:**
- `elevenlabs==1.8.0` - ElevenLabs TTS API
- `gTTS==2.5.3` - Google Text-to-Speech (fallback)

---

## ✅ Verify Installation

```bash
# Test providers
python scripts/test_speech_providers.py

# Check health endpoint
curl http://localhost:8000/api/v1/voice/health
```

---

## 🎯 Supported Providers

### Speech-to-Text (STT)

| Provider | Quality | Cost | Use Case |
|----------|---------|------|----------|
| **openai** | ⭐⭐⭐⭐⭐ | $0.006/min | **Production** |
| placeholder | ⭐⭐ | Free | Development |

### Text-to-Speech (TTS)

| Provider | Quality | Cost | Use Case |
|----------|---------|------|----------|
| **elevenlabs** | ⭐⭐⭐⭐⭐ | $5-22/mo | **Production** |
| placeholder | ⭐⭐ | Free | Development |

---

## 💰 Cost Estimates

**Small** (100 users, 10 min/user/month):
- ~$6/month

**Medium** (1,000 users, 10 min/user/month):
- ~$82/month

**Large** (10,000 users, 10 min/user/month):
- ~$625/month

---

## 🔧 Configuration Options

### Provider Selection

```bash
# STT providers: openai, google, azure, placeholder
STT_PROVIDER=openai

# TTS providers: elevenlabs, openai, google, azure, placeholder
TTS_PROVIDER=elevenlabs
```

### OpenAI Whisper (STT)

```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_WHISPER_MODEL=whisper-1
OPENAI_WHISPER_TIMEOUT=30
OPENAI_WHISPER_MAX_RETRIES=3
```

### ElevenLabs (TTS)

```bash
ELEVENLABS_API_KEY=your-key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel
ELEVENLABS_MODEL_ID=eleven_monolingual_v1
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.75
```

**Popular Voices:**
- `21m00Tcm4TlvDq8ikWAM` - Rachel (warm female)
- `pNInz6obpgDQGcFmaJgB` - Adam (deep male)
- `EXAVITQu4vr4xnSDxMaL` - Bella (soft female)
- `ErXwobaYiN019PkySvjV` - Antoni (male)

### Fallback Settings

```bash
ENABLE_STT_FALLBACK=true  # Recommended for production
ENABLE_TTS_FALLBACK=true  # Recommended for production
```

---

## 📖 Usage Examples

### Speech-to-Text

```python
from app.services.speech_service import get_speech_service

speech_service = get_speech_service()

# Transcribe audio
with open("audio.wav", "rb") as f:
    result = await speech_service.transcribe_audio(
        audio_data=f.read(),
        language="en",
        format="wav"
    )

print(result["text"])
```

### Text-to-Speech

```python
# Synthesize speech
audio_bytes = await speech_service.synthesize_speech(
    text="Your account balance is $1,234.56",
    language="en",
    voice="21m00Tcm4TlvDq8ikWAM",
    speed=1.0
)

with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

### List Voices

```python
# Get available voices
voices = await speech_service.list_voices(language="en")
for voice in voices:
    print(f"{voice['name']} ({voice['id']})")
```

### Health Check

```python
# Check provider health
health = await speech_service.check_health()
print(health)
```

---

## 🔄 Fallback & Resilience

### How It Works

```
Primary Provider (OpenAI/ElevenLabs)
    ↓ (try)
    ├─ Success → Return result
    └─ Failure → Log error
          ↓
    Fallback Provider (Placeholder)
          ↓ (try)
          ├─ Success → Return result
          └─ Failure → Raise exception
```

**Features:**
- Automatic retry (3 attempts, exponential backoff)
- Graceful fallback to free providers
- Detailed logging for debugging
- No downtime during provider issues

---

## 🐛 Troubleshooting

### Common Issues

**1. API Key Error**
```
Error: OpenAI API key not configured
```
**Solution:** Set `OPENAI_API_KEY` in `.env` file

**2. Provider Timeout**
```
Error: OpenAI Whisper API timeout
```
**Solution:** Increase `OPENAI_WHISPER_TIMEOUT=60` or enable fallback

**3. Quota Exceeded**
```
Error: You exceeded your current quota
```
**Solution:** Check API usage dashboard, enable fallback, or upgrade plan

**4. Poor Quality**
- Improve audio quality (reduce background noise)
- Use higher sample rate (16000 Hz minimum)
- Specify correct language
- Try different provider

### Testing

```bash
# Test STT
curl -X POST http://localhost:8000/api/v1/voice/transcribe \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@test.wav" \
  -F "language=en"

# Test TTS
curl -X POST http://localhost:8000/api/v1/voice/synthesize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "language": "en"}' \
  --output test_output.mp3

# Check health
curl http://localhost:8000/api/v1/voice/health
```

---

## 📋 Configuration Scenarios

### 1. Production (Best Quality)

```bash
STT_PROVIDER=openai
TTS_PROVIDER=elevenlabs
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=true
```

### 2. Development (Free)

```bash
STT_PROVIDER=placeholder
TTS_PROVIDER=placeholder
```

### 3. Hybrid (Cost-Optimized)

```bash
STT_PROVIDER=openai          # High quality STT
TTS_PROVIDER=placeholder     # Free TTS
OPENAI_API_KEY=sk-...
ENABLE_STT_FALLBACK=true
```

### 4. Testing (No API Calls)

```bash
STT_PROVIDER=placeholder
TTS_PROVIDER=placeholder
ENABLE_STT_FALLBACK=false
ENABLE_TTS_FALLBACK=false
```

---

## 📚 Documentation

- **Full Guide**: `docs/SPEECH_PROVIDERS.md` (comprehensive 772-line guide)
- **Environment Template**: `backend/.env.speech.example` (all options with examples)
- **Test Script**: `backend/scripts/test_speech_providers.py` (validation script)
- **Session Log**: `docs/sessions/SESSION_2025_01_17_SPEECH_PROVIDERS.md` (implementation details)

---

## 🎯 Best Practices

1. ✅ **Always enable fallback in production**
   ```bash
   ENABLE_STT_FALLBACK=true
   ENABLE_TTS_FALLBACK=true
   ```

2. ✅ **Use environment-specific configs**
   - Development: placeholder providers
   - Staging: hybrid (test with real APIs)
   - Production: premium providers

3. ✅ **Monitor usage and costs**
   - Check API dashboards regularly
   - Set up spending alerts
   - Track fallback trigger rate

4. ✅ **Cache common responses**
   ```python
   # Cache frequently used TTS outputs
   common_phrases = {
       "welcome": cached_audio_bytes,
       "goodbye": cached_audio_bytes
   }
   ```

5. ✅ **Implement rate limiting**
   - Prevent abuse
   - Control costs
   - Protect API quotas

---

## 🔐 Security

- **API Keys**: Store in environment variables, never commit to git
- **Secrets Management**: Use AWS Secrets Manager or Azure Key Vault in production
- **Rate Limiting**: Implement on all endpoints
- **Input Validation**: Check audio size, duration, and format
- **Monitoring**: Track unusual usage patterns

---

## 🚀 Migration Guide

### From Placeholder to Production

**Step 1:** Get API keys
```bash
# Sign up and obtain keys
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
```

**Step 2:** Update `.env`
```bash
STT_PROVIDER=openai
TTS_PROVIDER=elevenlabs
ENABLE_STT_FALLBACK=true
ENABLE_TTS_FALLBACK=true
```

**Step 3:** Test
```bash
python scripts/test_speech_providers.py
```

**Step 4:** Deploy
```bash
docker-compose restart backend
```

**Step 5:** Monitor
```bash
# Watch logs
docker-compose logs -f backend | grep -i speech

# Check health
curl http://localhost:8000/api/v1/voice/health
```

---

## 📞 Support

- **Issues**: Check logs at `docker-compose logs backend`
- **Health Check**: `/api/v1/voice/health` endpoint
- **Documentation**: See `docs/SPEECH_PROVIDERS.md`
- **Test Script**: Run `python scripts/test_speech_providers.py`

---

## 📊 Architecture

```
SpeechService
    ├── STT Provider (Primary: OpenAI Whisper)
    │   └── Fallback (Placeholder: Google Speech Recognition)
    │
    └── TTS Provider (Primary: ElevenLabs)
        └── Fallback (Placeholder: gTTS)
```

**Features:**
- Modular provider architecture
- Automatic fallback on failure
- Retry with exponential backoff
- Comprehensive error handling
- Health monitoring
- Voice management

---

## ✨ Key Features

- 🎯 **Multiple Providers**: OpenAI, ElevenLabs, Google, Azure, and more
- 🔄 **Automatic Fallback**: Graceful degradation on provider failure
- 🚀 **Production Ready**: Built for scale with retry logic and monitoring
- 💰 **Cost Efficient**: Mix and match providers based on needs
- 🔧 **Easy Configuration**: Simple environment variable setup
- 📊 **Health Monitoring**: Built-in health checks and logging
- 🌍 **Multilingual**: Support for 90+ languages
- 🎙️ **High Quality**: Industry-leading STT and TTS providers

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-17  
**Status**: ✅ Production Ready

For detailed documentation, see `docs/SPEECH_PROVIDERS.md`
