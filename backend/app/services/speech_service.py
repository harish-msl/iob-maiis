"""
Speech Service
Handles speech-to-text transcription and text-to-speech synthesis
Uses provider architecture with fallback support for production environments
"""

import io
from typing import Any, Dict, Optional

from loguru import logger
from pydub import AudioSegment

from app.core.config import get_settings
from app.services.speech_providers import (
    PlaceholderSTTProvider,
    PlaceholderTTSProvider,
    SpeechProviderFactory,
    STTProvider,
    TTSProvider,
)

settings = get_settings()


class SpeechService:
    """
    Service for speech processing with provider support
    Handles audio transcription and speech synthesis with fallback
    """

    def __init__(self):
        self.supported_audio_formats = [".mp3", ".wav", ".ogg", ".flac", ".m4a"]
        self.default_language = "en-US"
        self.sample_rate = 16000

        # Initialize providers
        self._init_providers()

    def _init_providers(self):
        """Initialize STT and TTS providers with fallback"""
        try:
            # Create primary providers
            self.stt_provider: STTProvider = SpeechProviderFactory.create_stt_provider()
            self.tts_provider: TTSProvider = SpeechProviderFactory.create_tts_provider()

            # Create fallback providers if enabled
            if settings.ENABLE_STT_FALLBACK:
                self.stt_fallback: STTProvider = PlaceholderSTTProvider()
            else:
                self.stt_fallback = None

            if settings.ENABLE_TTS_FALLBACK:
                self.tts_fallback: TTSProvider = PlaceholderTTSProvider()
            else:
                self.tts_fallback = None

            logger.info(
                f"Speech service initialized: STT={settings.STT_PROVIDER}, TTS={settings.TTS_PROVIDER}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize speech providers: {str(e)}")
            # Use placeholder providers as last resort
            self.stt_provider = PlaceholderSTTProvider()
            self.tts_provider = PlaceholderTTSProvider()
            self.stt_fallback = None
            self.tts_fallback = None

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en-US",
        format: str = "wav",
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using configured STT provider

        Args:
            audio_data: Audio file bytes
            language: Language code (e.g., 'en-US', 'es-ES')
            format: Audio format (wav, mp3, etc.)

        Returns:
            Dict with transcribed text and metadata

        Example:
            with open("audio.wav", "rb") as f:
                result = await speech_service.transcribe_audio(f.read())
            print(result["text"])
        """
        try:
            logger.info(f"Transcribing audio (format: {format}, language: {language})")

            # Convert audio to proper format if needed
            audio_data = await self._convert_audio_format(audio_data, format)

            # Normalize language code (remove region if provider doesn't support it)
            lang_code = self._normalize_language_code(language)

            # Try primary provider
            try:
                result = await self.stt_provider.transcribe(
                    audio_data, language=lang_code, format="wav"
                )
                logger.info(
                    f"Transcription completed with primary provider: {result.get('word_count', 0)} words"
                )
                return result

            except Exception as primary_error:
                logger.warning(
                    f"Primary STT provider failed: {str(primary_error)}, trying fallback"
                )

                # Try fallback if available
                if self.stt_fallback:
                    try:
                        result = await self.stt_fallback.transcribe(
                            audio_data, language=language, format="wav"
                        )
                        logger.info(
                            f"Transcription completed with fallback provider: {result.get('word_count', 0)} words"
                        )
                        return result
                    except Exception as fallback_error:
                        logger.error(
                            f"Fallback STT provider also failed: {str(fallback_error)}"
                        )
                        raise primary_error  # Raise original error
                else:
                    raise

        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            raise

    async def synthesize_speech(
        self,
        text: str,
        language: str = "en-US",
        voice: Optional[str] = None,
        speed: float = 1.0,
        format: str = "mp3",
    ) -> bytes:
        """
        Convert text to speech using configured TTS provider

        Args:
            text: Text to synthesize
            language: Language code
            voice: Optional voice ID/name
            speed: Speech rate (0.5 to 2.0)
            format: Output audio format (mp3, wav)

        Returns:
            Audio file bytes

        Example:
            audio_bytes = await speech_service.synthesize_speech(
                "Hello, welcome to our banking service"
            )
            with open("output.mp3", "wb") as f:
                f.write(audio_bytes)
        """
        try:
            logger.info(f"Synthesizing speech (language: {language}, speed: {speed})")

            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            # Normalize language code
            lang_code = self._normalize_language_code(language)

            # Try primary provider
            try:
                audio_bytes = await self.tts_provider.synthesize(
                    text=text,
                    language=lang_code,
                    voice=voice,
                    speed=speed,
                )
                logger.info(
                    f"Speech synthesis completed with primary provider: {len(audio_bytes)} bytes"
                )

                # Convert format if needed
                if format != "mp3":
                    audio_bytes = await self._convert_output_format(audio_bytes, format)

                return audio_bytes

            except Exception as primary_error:
                logger.warning(
                    f"Primary TTS provider failed: {str(primary_error)}, trying fallback"
                )

                # Try fallback if available
                if self.tts_fallback:
                    try:
                        audio_bytes = await self.tts_fallback.synthesize(
                            text=text,
                            language=lang_code,
                            voice=voice,
                            speed=speed,
                        )
                        logger.info(
                            f"Speech synthesis completed with fallback provider: {len(audio_bytes)} bytes"
                        )

                        # Convert format if needed
                        if format != "mp3":
                            audio_bytes = await self._convert_output_format(
                                audio_bytes, format
                            )

                        return audio_bytes

                    except Exception as fallback_error:
                        logger.error(
                            f"Fallback TTS provider also failed: {str(fallback_error)}"
                        )
                        raise primary_error  # Raise original error
                else:
                    raise

        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            raise

    async def list_voices(self, language: Optional[str] = None) -> list:
        """
        List available voices from TTS provider

        Args:
            language: Optional language filter

        Returns:
            List of available voices with metadata
        """
        try:
            voices = await self.tts_provider.list_voices(language)
            return voices
        except Exception as e:
            logger.error(f"Failed to list voices: {str(e)}")
            return []

    async def _convert_audio_format(
        self, audio_data: bytes, input_format: str
    ) -> bytes:
        """
        Convert audio to WAV format for processing

        Args:
            audio_data: Input audio bytes
            input_format: Input format (mp3, wav, etc.)

        Returns:
            WAV format audio bytes
        """
        try:
            if input_format.lower() == "wav":
                return audio_data

            # Load audio with pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)

            # Convert to WAV
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(1)  # Mono

            # Export to bytes
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Audio format conversion failed: {str(e)}")
            raise

    async def _convert_output_format(
        self, audio_data: bytes, output_format: str
    ) -> bytes:
        """
        Convert audio output format

        Args:
            audio_data: Input audio bytes (MP3)
            output_format: Desired output format

        Returns:
            Converted audio bytes
        """
        try:
            # Load audio
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))

            # Convert format
            buffer = io.BytesIO()
            audio.export(buffer, format=output_format)
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Output format conversion failed: {str(e)}")
            raise

    def _normalize_language_code(self, language: str) -> str:
        """
        Normalize language code for provider compatibility

        Args:
            language: Language code (e.g., 'en-US', 'en', 'es-ES')

        Returns:
            Normalized language code
        """
        # Extract base language code (first part before hyphen)
        if "-" in language:
            return language.split("-")[0]
        return language

    async def detect_language(self, audio_data: bytes) -> str:
        """
        Detect language in audio

        Args:
            audio_data: Audio file bytes

        Returns:
            Detected language code

        Note:
            Uses primary STT provider's language detection
        """
        try:
            lang = await self.stt_provider.detect_language(audio_data)
            logger.info(f"Detected language: {lang}")
            return lang
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}, using default")
            return "en"

    async def get_audio_info(
        self, audio_data: bytes, format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Get information about audio file

        Args:
            audio_data: Audio file bytes
            format: Audio format

        Returns:
            Dict with audio metadata

        Example:
            info = await speech_service.get_audio_info(audio_bytes)
            print(f"Duration: {info['duration']}s")
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)

            return {
                "duration": len(audio) / 1000.0,  # seconds
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "format": format,
                "size_bytes": len(audio_data),
            }

        except Exception as e:
            logger.error(f"Failed to get audio info: {str(e)}")
            raise

    async def trim_silence(
        self, audio_data: bytes, format: str = "wav", silence_thresh: int = -50
    ) -> bytes:
        """
        Remove silence from beginning and end of audio

        Args:
            audio_data: Audio file bytes
            format: Audio format
            silence_thresh: Silence threshold in dBFS

        Returns:
            Trimmed audio bytes
        """
        try:
            from pydub.silence import detect_nonsilent

            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)

            # Detect non-silent chunks
            nonsilent_chunks = detect_nonsilent(
                audio, min_silence_len=100, silence_thresh=silence_thresh
            )

            if not nonsilent_chunks:
                return audio_data

            # Get start and end of speech
            start = nonsilent_chunks[0][0]
            end = nonsilent_chunks[-1][1]

            # Trim audio
            trimmed = audio[start:end]

            # Export to bytes
            buffer = io.BytesIO()
            trimmed.export(buffer, format=format)
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Silence trimming failed: {str(e)}")
            raise

    async def check_health(self) -> Dict[str, Any]:
        """
        Check if speech service and providers are available

        Returns:
            Dict with health status of all providers
        """
        health_status = {
            "service": "healthy",
            "providers": {},
        }

        try:
            # Check primary STT provider
            try:
                stt_healthy = await self.stt_provider.check_health()
                health_status["providers"]["stt_primary"] = {
                    "provider": settings.STT_PROVIDER,
                    "status": "healthy" if stt_healthy else "unhealthy",
                }
            except Exception as e:
                health_status["providers"]["stt_primary"] = {
                    "provider": settings.STT_PROVIDER,
                    "status": "error",
                    "error": str(e),
                }

            # Check primary TTS provider
            try:
                tts_healthy = await self.tts_provider.check_health()
                health_status["providers"]["tts_primary"] = {
                    "provider": settings.TTS_PROVIDER,
                    "status": "healthy" if tts_healthy else "unhealthy",
                }
            except Exception as e:
                health_status["providers"]["tts_primary"] = {
                    "provider": settings.TTS_PROVIDER,
                    "status": "error",
                    "error": str(e),
                }

            # Check fallback providers if available
            if self.stt_fallback:
                try:
                    fallback_healthy = await self.stt_fallback.check_health()
                    health_status["providers"]["stt_fallback"] = {
                        "provider": "placeholder",
                        "status": "healthy" if fallback_healthy else "unhealthy",
                    }
                except Exception as e:
                    health_status["providers"]["stt_fallback"] = {
                        "provider": "placeholder",
                        "status": "error",
                        "error": str(e),
                    }

            if self.tts_fallback:
                try:
                    fallback_healthy = await self.tts_fallback.check_health()
                    health_status["providers"]["tts_fallback"] = {
                        "provider": "placeholder",
                        "status": "healthy" if fallback_healthy else "unhealthy",
                    }
                except Exception as e:
                    health_status["providers"]["tts_fallback"] = {
                        "provider": "placeholder",
                        "status": "error",
                        "error": str(e),
                    }

            logger.info("Speech service health check completed")
            return health_status

        except Exception as e:
            logger.error(f"Speech service health check failed: {str(e)}")
            health_status["service"] = "unhealthy"
            health_status["error"] = str(e)
            return health_status


# Global instance
_speech_service: Optional[SpeechService] = None


def get_speech_service() -> SpeechService:
    """
    Get singleton instance of speech service

    Returns:
        SpeechService instance
    """
    global _speech_service
    if _speech_service is None:
        _speech_service = SpeechService()
    return _speech_service
