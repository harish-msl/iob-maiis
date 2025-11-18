"""
Speech Provider Implementations
Modular provider architecture for STT and TTS services
Supports multiple providers with graceful fallback
"""

import io
import os
import tempfile
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger
from pydub import AudioSegment

from app.core.config import get_settings

settings = get_settings()


# ============================================
# BASE PROVIDER INTERFACES
# ============================================


class STTProvider(ABC):
    """Abstract base class for Speech-to-Text providers"""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        format: str = "wav",
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text

        Args:
            audio_data: Audio file bytes
            language: Language code (e.g., 'en', 'es', 'fr')
            format: Audio format (wav, mp3, etc.)

        Returns:
            Dict with:
                - text: Transcribed text
                - language: Detected/specified language
                - duration: Audio duration in seconds
                - confidence: Confidence score (0-1)
                - word_count: Number of words
        """
        pass

    @abstractmethod
    async def detect_language(self, audio_data: bytes) -> str:
        """Detect language in audio"""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if provider is available"""
        pass


class TTSProvider(ABC):
    """Abstract base class for Text-to-Speech providers"""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """
        Convert text to speech

        Args:
            text: Text to synthesize
            language: Language code
            voice: Voice ID/name
            speed: Speech rate (0.5 to 2.0)

        Returns:
            Audio file bytes (MP3)
        """
        pass

    @abstractmethod
    async def list_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available voices"""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if provider is available"""
        pass


# ============================================
# OPENAI WHISPER STT PROVIDER
# ============================================


class OpenAIWhisperProvider(STTProvider):
    """OpenAI Whisper API for speech-to-text transcription"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_WHISPER_MODEL
        self.timeout = settings.OPENAI_WHISPER_TIMEOUT
        self.max_retries = settings.OPENAI_WHISPER_MAX_RETRIES
        self.base_url = "https://api.openai.com/v1/audio"

        if not self.api_key:
            logger.warning("OpenAI API key not configured")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        format: str = "wav",
    ) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            if not self.api_key:
                raise ValueError("OpenAI API key not configured")

            logger.info(
                f"Transcribing with OpenAI Whisper (language: {language}, format: {format})"
            )

            # Get audio duration
            audio_segment = AudioSegment.from_file(
                io.BytesIO(audio_data), format=format
            )
            duration = len(audio_segment) / 1000.0

            # Prepare file for upload
            files = {
                "file": (f"audio.{format}", io.BytesIO(audio_data), f"audio/{format}")
            }
            data = {
                "model": self.model,
                "language": language if language != "auto" else None,
                "response_format": "verbose_json",  # Get detailed response
            }

            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            headers = {"Authorization": f"Bearer {self.api_key}"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for attempt in range(self.max_retries):
                    try:
                        response = await client.post(
                            f"{self.base_url}/transcriptions",
                            headers=headers,
                            files=files,
                            data=data,
                        )
                        response.raise_for_status()
                        break
                    except httpx.HTTPStatusError as e:
                        if attempt == self.max_retries - 1:
                            raise
                        logger.warning(
                            f"OpenAI Whisper API error (attempt {attempt + 1}/{self.max_retries}): {str(e)}"
                        )
                        await asyncio.sleep(2**attempt)  # Exponential backoff

            result = response.json()

            # Extract text and metadata
            transcription = {
                "text": result.get("text", ""),
                "language": result.get("language", language),
                "duration": result.get("duration", duration),
                "confidence": 0.95,  # Whisper doesn't provide confidence, use high default
                "word_count": len(result.get("text", "").split()),
                "provider": "openai-whisper",
            }

            # Add segments if available (for word-level timing)
            if "segments" in result:
                transcription["segments"] = result["segments"]

            logger.info(
                f"OpenAI Whisper transcription completed: {transcription['word_count']} words"
            )

            return transcription

        except Exception as e:
            logger.error(f"OpenAI Whisper transcription failed: {str(e)}")
            raise

    async def detect_language(self, audio_data: bytes) -> str:
        """Detect language using Whisper API (auto-detect mode)"""
        try:
            result = await self.transcribe(audio_data, language="auto")
            return result.get("language", "en")
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return "en"

    async def check_health(self) -> bool:
        """Check if OpenAI API is accessible"""
        try:
            if not self.api_key:
                return False

            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models", headers=headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            return False


# ============================================
# ELEVENLABS TTS PROVIDER
# ============================================


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs API for high-quality text-to-speech"""

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        self.model_id = settings.ELEVENLABS_MODEL_ID
        self.stability = settings.ELEVENLABS_STABILITY
        self.similarity_boost = settings.ELEVENLABS_SIMILARITY_BOOST
        self.timeout = settings.ELEVENLABS_TIMEOUT
        self.base_url = "https://api.elevenlabs.io/v1"

        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")

    async def synthesize(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """Synthesize speech using ElevenLabs API"""
        try:
            if not self.api_key:
                raise ValueError("ElevenLabs API key not configured")

            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            logger.info(
                f"Synthesizing with ElevenLabs (voice: {voice or self.voice_id}, speed: {speed})"
            )

            # Use specified voice or default
            voice_id = voice or self.voice_id

            # ElevenLabs API request
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
            }

            payload = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost,
                    "style": 0.0,
                    "use_speaker_boost": True,
                },
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

            audio_bytes = response.content

            # Apply speed adjustment if needed (using pydub)
            if speed != 1.0 and speed > 0:
                audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
                # Change speed by adjusting frame rate
                audio = audio._spawn(
                    audio.raw_data,
                    overrides={"frame_rate": int(audio.frame_rate * speed)},
                )
                audio = audio.set_frame_rate(audio.frame_rate)

                buffer = io.BytesIO()
                audio.export(buffer, format="mp3")
                buffer.seek(0)
                audio_bytes = buffer.getvalue()

            logger.info(f"ElevenLabs synthesis completed: {len(audio_bytes)} bytes")

            return audio_bytes

        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {str(e)}")
            raise

    async def list_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available ElevenLabs voices"""
        try:
            if not self.api_key:
                raise ValueError("ElevenLabs API key not configured")

            headers = {"xi-api-key": self.api_key}

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/voices", headers=headers)
                response.raise_for_status()

            result = response.json()
            voices = result.get("voices", [])

            # Format voice list
            formatted_voices = [
                {
                    "id": voice["voice_id"],
                    "name": voice["name"],
                    "category": voice.get("category", "general"),
                    "description": voice.get("description", ""),
                    "labels": voice.get("labels", {}),
                }
                for voice in voices
            ]

            return formatted_voices

        except Exception as e:
            logger.error(f"Failed to list ElevenLabs voices: {str(e)}")
            return []

    async def check_health(self) -> bool:
        """Check if ElevenLabs API is accessible"""
        try:
            if not self.api_key:
                return False

            headers = {"xi-api-key": self.api_key}
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/voices", headers=headers)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"ElevenLabs health check failed: {str(e)}")
            return False


# ============================================
# PLACEHOLDER/FALLBACK PROVIDERS
# ============================================


class PlaceholderSTTProvider(STTProvider):
    """Fallback STT using Google Speech Recognition (free tier)"""

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        format: str = "wav",
    ) -> Dict[str, Any]:
        """Transcribe using speech_recognition library"""
        try:
            import speech_recognition as sr

            logger.info(
                f"Transcribing with placeholder STT (Google Speech Recognition)"
            )

            recognizer = sr.Recognizer()

            # Convert to WAV if needed
            if format.lower() != "wav":
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
                buffer = io.BytesIO()
                audio.export(buffer, format="wav")
                buffer.seek(0)
                audio_data = buffer.getvalue()

            # Get duration
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
            duration = len(audio_segment) / 1000.0

            # Write to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            try:
                with sr.AudioFile(temp_audio_path) as source:
                    audio = recognizer.record(source)

                # Map language codes
                lang_map = {
                    "en": "en-US",
                    "es": "es-ES",
                    "fr": "fr-FR",
                    "de": "de-DE",
                    "it": "it-IT",
                }
                google_lang = lang_map.get(language, f"{language}-US")

                text = recognizer.recognize_google(audio, language=google_lang)

                return {
                    "text": text,
                    "language": language,
                    "duration": round(duration, 2),
                    "confidence": 0.85,
                    "word_count": len(text.split()),
                    "provider": "placeholder-google",
                }

            finally:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

        except sr.UnknownValueError:
            logger.warning("Speech not recognized in audio")
            return {
                "text": "",
                "language": language,
                "error": "Could not understand audio",
                "provider": "placeholder-google",
            }
        except Exception as e:
            logger.error(f"Placeholder STT failed: {str(e)}")
            raise

    async def detect_language(self, audio_data: bytes) -> str:
        """Simple language detection"""
        return "en"

    async def check_health(self) -> bool:
        """Check if speech_recognition is available"""
        try:
            import speech_recognition

            return True
        except ImportError:
            return False


class PlaceholderTTSProvider(TTSProvider):
    """Fallback TTS using gTTS (Google Text-to-Speech free tier)"""

    async def synthesize(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """Synthesize using gTTS"""
        try:
            from gtts import gTTS

            logger.info(f"Synthesizing with placeholder TTS (gTTS)")

            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=(speed < 1.0))

            # Save to bytes
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            return audio_buffer.getvalue()

        except Exception as e:
            logger.error(f"Placeholder TTS failed: {str(e)}")
            raise

    async def list_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """gTTS uses default voices per language"""
        return [{"id": "default", "name": "Default", "language": language or "en"}]

    async def check_health(self) -> bool:
        """Check if gTTS is available"""
        try:
            from gtts import gTTS

            return True
        except ImportError:
            return False


# ============================================
# PROVIDER FACTORY
# ============================================


class SpeechProviderFactory:
    """Factory to create and manage speech providers"""

    @staticmethod
    def create_stt_provider(provider_name: Optional[str] = None) -> STTProvider:
        """
        Create STT provider based on configuration

        Args:
            provider_name: Override provider from config

        Returns:
            STTProvider instance
        """
        provider = provider_name or settings.STT_PROVIDER

        if provider == "openai":
            return OpenAIWhisperProvider()
        elif provider == "placeholder":
            return PlaceholderSTTProvider()
        else:
            logger.warning(f"Unknown STT provider '{provider}', using placeholder")
            return PlaceholderSTTProvider()

    @staticmethod
    def create_tts_provider(provider_name: Optional[str] = None) -> TTSProvider:
        """
        Create TTS provider based on configuration

        Args:
            provider_name: Override provider from config

        Returns:
            TTSProvider instance
        """
        provider = provider_name or settings.TTS_PROVIDER

        if provider == "elevenlabs":
            return ElevenLabsProvider()
        elif provider == "placeholder":
            return PlaceholderTTSProvider()
        else:
            logger.warning(f"Unknown TTS provider '{provider}', using placeholder")
            return PlaceholderTTSProvider()


# Import asyncio for sleep
import asyncio
