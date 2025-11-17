"""
Speech Service
Handles speech-to-text transcription and text-to-speech synthesis
"""

import io
import tempfile
from typing import Any, Dict, Optional

from loguru import logger
from pydub import AudioSegment

from app.core.config import get_settings

settings = get_settings()


class SpeechService:
    """
    Service for speech processing
    Handles audio transcription and speech synthesis
    """

    def __init__(self):
        self.supported_audio_formats = [".mp3", ".wav", ".ogg", ".flac", ".m4a"]
        self.default_language = "en-US"
        self.sample_rate = 16000

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en-US",
        format: str = "wav",
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using speech recognition

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

            # For this implementation, we'll use a placeholder
            # In production, integrate with:
            # - OpenAI Whisper API
            # - Google Cloud Speech-to-Text
            # - AWS Transcribe
            # - Azure Speech Services

            # Placeholder implementation
            import speech_recognition as sr

            # Create recognizer
            recognizer = sr.Recognizer()

            # Convert bytes to audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            try:
                # Load audio file
                with sr.AudioFile(temp_audio_path) as source:
                    audio = recognizer.record(source)

                # Perform recognition
                text = recognizer.recognize_google(audio, language=language)

                # Get audio duration
                audio_segment = AudioSegment.from_file(
                    io.BytesIO(audio_data), format="wav"
                )
                duration = len(audio_segment) / 1000.0  # Convert to seconds

                result = {
                    "text": text,
                    "language": language,
                    "duration": round(duration, 2),
                    "format": format,
                    "confidence": 0.95,  # Google doesn't provide confidence
                    "word_count": len(text.split()),
                }

                logger.info(
                    f"Transcription completed: {result['word_count']} words in {result['duration']}s"
                )

                return result

            finally:
                # Clean up temp file
                import os

                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

        except sr.UnknownValueError:
            logger.warning("Speech not recognized in audio")
            return {
                "text": "",
                "language": language,
                "error": "Could not understand audio",
            }
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
            raise Exception(f"Speech recognition service unavailable: {str(e)}")
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
        Convert text to speech

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

            # For this implementation, we'll use gTTS (Google Text-to-Speech)
            # In production, consider:
            # - ElevenLabs API (high quality)
            # - Google Cloud TTS
            # - AWS Polly
            # - Azure Speech Services

            from gtts import gTTS

            # Create TTS object
            tts = gTTS(text=text, lang=language.split("-")[0], slow=(speed < 1.0))

            # Save to bytes
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            audio_bytes = audio_buffer.getvalue()

            # Convert format if needed
            if format != "mp3":
                audio_bytes = await self._convert_output_format(audio_bytes, format)

            logger.info(f"Speech synthesis completed: {len(audio_bytes)} bytes")

            return audio_bytes

        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            raise

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

    async def detect_language(self, audio_data: bytes) -> str:
        """
        Detect language in audio

        Args:
            audio_data: Audio file bytes

        Returns:
            Detected language code

        Note:
            This is a basic implementation using speech recognition
            For production, use dedicated language detection services
        """
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()

            # Convert to WAV
            audio_data = await self._convert_audio_format(audio_data, "mp3")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name

            try:
                with sr.AudioFile(temp_audio_path) as source:
                    audio = recognizer.record(source)

                # Try different languages
                languages = ["en-US", "es-ES", "fr-FR", "de-DE", "it-IT"]

                for lang in languages:
                    try:
                        recognizer.recognize_google(audio, language=lang)
                        logger.info(f"Detected language: {lang}")
                        return lang
                    except sr.UnknownValueError:
                        continue

                return "en-US"  # Default fallback

            finally:
                import os

                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return "en-US"

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

    async def check_health(self) -> bool:
        """
        Check if speech service is available

        Returns:
            True if dependencies are installed and working
        """
        try:
            # Check if required packages are available
            import speech_recognition  # noqa: F401
            from gtts import gTTS  # noqa: F401

            # Try a simple synthesis
            test_tts = gTTS(text="test", lang="en")
            test_buffer = io.BytesIO()
            test_tts.write_to_fp(test_buffer)

            logger.info("Speech service is healthy")
            return True

        except Exception as e:
            logger.error(f"Speech service health check failed: {str(e)}")
            return False


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
