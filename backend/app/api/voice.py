"""
Voice API Router
Handles speech-to-text transcription and text-to-speech synthesis
"""

import base64
import io
from typing import Any, Dict, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import Response
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.services.speech_service import get_speech_service

router = APIRouter(prefix="/voice", tags=["voice"])

# ============================================================================
# Schemas
# ============================================================================


class TranscribeRequest(BaseModel):
    """Speech-to-text transcription request"""

    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio data")
    language: str = Field("en-US", description="Language code (e.g., en-US, es-ES)")
    format: str = Field("wav", description="Audio format (wav, mp3, ogg, flac)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "audio_base64": "UklGRiQAAABXQVZFZm10...",
                    "language": "en-US",
                    "format": "wav",
                }
            ]
        }
    }


class TranscribeResponse(BaseModel):
    """Transcription response"""

    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Language used")
    duration: float = Field(..., description="Audio duration in seconds")
    confidence: float = Field(..., description="Transcription confidence score")
    word_count: int = Field(..., description="Number of words transcribed")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hello, I would like to open a savings account.",
                    "language": "en-US",
                    "duration": 3.5,
                    "confidence": 0.95,
                    "word_count": 9,
                }
            ]
        }
    }


class SynthesizeRequest(BaseModel):
    """Text-to-speech synthesis request"""

    text: str = Field(..., min_length=1, description="Text to synthesize")
    language: str = Field("en-US", description="Language code")
    voice: Optional[str] = Field(None, description="Voice ID/name (optional)")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech rate (0.5 to 2.0)")
    format: str = Field("mp3", description="Output audio format (mp3, wav)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Welcome to our banking service. How may I help you today?",
                    "language": "en-US",
                    "speed": 1.0,
                    "format": "mp3",
                }
            ]
        }
    }


class SynthesizeResponse(BaseModel):
    """Synthesis response with audio data"""

    audio_base64: str = Field(..., description="Base64 encoded audio")
    format: str = Field(..., description="Audio format")
    size_bytes: int = Field(..., description="Audio size in bytes")
    text_length: int = Field(..., description="Length of input text")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "audio_base64": "SUQzBAAAAAAAI1RTU0UAAAA...",
                    "format": "mp3",
                    "size_bytes": 15360,
                    "text_length": 62,
                }
            ]
        }
    }


class AudioInfoResponse(BaseModel):
    """Audio information response"""

    duration: float = Field(..., description="Duration in seconds")
    channels: int = Field(..., description="Number of audio channels")
    sample_rate: int = Field(..., description="Sample rate in Hz")
    format: str = Field(..., description="Audio format")
    size_bytes: int = Field(..., description="File size in bytes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "duration": 3.5,
                    "channels": 1,
                    "sample_rate": 16000,
                    "format": "wav",
                    "size_bytes": 112000,
                }
            ]
        }
    }


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = "en-US",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TranscribeResponse:
    """
    Transcribe audio to text (Speech-to-Text)

    Upload an audio file and receive the transcribed text.

    Args:
        audio: Audio file (WAV, MP3, OGG, FLAC, M4A)
        language: Language code (e.g., en-US, es-ES, fr-FR)
        current_user: Authenticated user
        db: Database session

    Returns:
        Transcribed text with metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/voice/transcribe" \
          -H "Authorization: Bearer YOUR_TOKEN" \
          -F "audio=@recording.wav" \
          -F "language=en-US"
        ```
    """
    try:
        # Validate file
        if not audio.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided",
            )

        # Read audio data
        audio_data = await audio.read()
        file_size = len(audio_data)

        # Check file size (max 25MB)
        max_size = 25 * 1024 * 1024  # 25MB
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio file too large. Maximum size is {max_size / 1024 / 1024}MB",
            )

        logger.info(
            f"User {current_user.id} transcribing audio: {audio.filename} ({file_size} bytes)"
        )

        # Get speech service
        speech_service = get_speech_service()

        # Detect format from content type or filename
        format_type = "wav"
        if audio.content_type:
            if "mp3" in audio.content_type:
                format_type = "mp3"
            elif "ogg" in audio.content_type:
                format_type = "ogg"
            elif "flac" in audio.content_type:
                format_type = "flac"
        elif audio.filename:
            if audio.filename.endswith(".mp3"):
                format_type = "mp3"
            elif audio.filename.endswith(".ogg"):
                format_type = "ogg"
            elif audio.filename.endswith(".flac"):
                format_type = "flac"

        # Transcribe audio
        result = await speech_service.transcribe_audio(
            audio_data=audio_data,
            language=language,
            format=format_type,
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"],
            )

        logger.info(
            f"Transcription completed: {result.get('word_count', 0)} words in {result.get('duration', 0)}s"
        )

        return TranscribeResponse(
            text=result["text"],
            language=result["language"],
            duration=result.get("duration", 0.0),
            confidence=result.get("confidence", 0.0),
            word_count=result.get("word_count", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}",
        )


@router.post("/transcribe-base64", response_model=TranscribeResponse)
async def transcribe_base64(
    request: TranscribeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TranscribeResponse:
    """
    Transcribe base64 encoded audio to text

    Alternative endpoint that accepts base64 encoded audio data in JSON.

    Args:
        request: Transcription request with base64 audio
        current_user: Authenticated user
        db: Database session

    Returns:
        Transcribed text with metadata

    Example:
        ```
        POST /api/voice/transcribe-base64
        {
            "audio_base64": "UklGRiQAAABXQVZF...",
            "language": "en-US",
            "format": "wav"
        }
        ```
    """
    try:
        if not request.audio_base64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="audio_base64 is required",
            )

        # Decode base64 audio
        try:
            audio_data = base64.b64decode(request.audio_base64)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid base64 data: {str(e)}",
            )

        logger.info(f"User {current_user.id} transcribing base64 audio")

        # Get speech service
        speech_service = get_speech_service()

        # Transcribe
        result = await speech_service.transcribe_audio(
            audio_data=audio_data,
            language=request.language,
            format=request.format,
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"],
            )

        return TranscribeResponse(
            text=result["text"],
            language=result["language"],
            duration=result.get("duration", 0.0),
            confidence=result.get("confidence", 0.0),
            word_count=result.get("word_count", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}",
        )


@router.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(
    request: SynthesizeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SynthesizeResponse:
    """
    Convert text to speech (Text-to-Speech)

    Generate audio from text input.

    Args:
        request: Synthesis request with text and options
        current_user: Authenticated user
        db: Database session

    Returns:
        Base64 encoded audio data

    Example:
        ```
        POST /api/voice/synthesize
        {
            "text": "Welcome to our banking service",
            "language": "en-US",
            "speed": 1.0,
            "format": "mp3"
        }
        ```
    """
    try:
        logger.info(
            f"User {current_user.id} synthesizing speech: {request.text[:50]}..."
        )

        # Get speech service
        speech_service = get_speech_service()

        # Synthesize speech
        audio_bytes = await speech_service.synthesize_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed,
            format=request.format,
        )

        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        logger.info(f"Speech synthesis completed: {len(audio_bytes)} bytes")

        return SynthesizeResponse(
            audio_base64=audio_base64,
            format=request.format,
            size_bytes=len(audio_bytes),
            text_length=len(request.text),
        )

    except Exception as e:
        logger.error(f"Speech synthesis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}",
        )


@router.post("/synthesize-audio")
async def synthesize_audio_file(
    request: SynthesizeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Response:
    """
    Convert text to speech and return audio file directly

    Returns audio file that can be played directly in browser.

    Args:
        request: Synthesis request
        current_user: Authenticated user
        db: Database session

    Returns:
        Audio file as binary response

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/voice/synthesize-audio" \
          -H "Authorization: Bearer YOUR_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"text": "Hello world", "format": "mp3"}' \
          --output speech.mp3
        ```
    """
    try:
        logger.info(f"User {current_user.id} requesting audio file synthesis")

        # Get speech service
        speech_service = get_speech_service()

        # Synthesize speech
        audio_bytes = await speech_service.synthesize_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed,
            format=request.format,
        )

        # Determine media type
        media_type = "audio/mpeg" if request.format == "mp3" else "audio/wav"

        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="speech.{request.format}"'
            },
        )

    except Exception as e:
        logger.error(f"Audio synthesis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio synthesis failed: {str(e)}",
        )


@router.post("/audio-info", response_model=AudioInfoResponse)
async def get_audio_info(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> AudioInfoResponse:
    """
    Get information about an audio file

    Args:
        audio: Audio file
        current_user: Authenticated user
        db: Database session

    Returns:
        Audio metadata (duration, sample rate, etc.)
    """
    try:
        # Read audio data
        audio_data = await audio.read()

        # Detect format
        format_type = "wav"
        if audio.content_type:
            if "mp3" in audio.content_type:
                format_type = "mp3"
            elif "ogg" in audio.content_type:
                format_type = "ogg"
            elif "flac" in audio.content_type:
                format_type = "flac"

        # Get speech service
        speech_service = get_speech_service()

        # Get audio info
        info = await speech_service.get_audio_info(
            audio_data=audio_data,
            format=format_type,
        )

        return AudioInfoResponse(
            duration=info["duration"],
            channels=info["channels"],
            sample_rate=info["sample_rate"],
            format=info["format"],
            size_bytes=info["size_bytes"],
        )

    except Exception as e:
        logger.error(f"Failed to get audio info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audio info: {str(e)}",
        )


@router.get("/health")
async def check_health() -> Dict[str, Any]:
    """
    Check health of voice/speech service

    Returns:
        Health status
    """
    try:
        speech_service = get_speech_service()
        is_healthy = await speech_service.check_health()

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "speech",
            "capabilities": {
                "transcription": True,
                "synthesis": True,
                "formats": ["wav", "mp3", "ogg", "flac", "m4a"],
            },
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }
