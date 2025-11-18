#!/usr/bin/env python3
"""
Speech Provider Test Script
Tests STT and TTS providers with real audio samples
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.config import get_settings
from app.services.speech_service import get_speech_service
from loguru import logger

settings = get_settings()


async def test_stt_provider():
    """Test Speech-to-Text provider"""
    logger.info("=" * 60)
    logger.info("Testing STT Provider")
    logger.info("=" * 60)

    try:
        service = get_speech_service()

        # Create a simple test audio (silence for now)
        # In real usage, load actual audio file
        logger.info(f"STT Provider: {settings.STT_PROVIDER}")

        # Check if we have a test audio file
        test_audio_path = backend_path / "tests" / "fixtures" / "test_audio.wav"

        if test_audio_path.exists():
            with open(test_audio_path, "rb") as f:
                audio_data = f.read()

            logger.info(f"Testing with audio file: {test_audio_path}")
            logger.info(f"Audio size: {len(audio_data)} bytes")

            result = await service.transcribe_audio(
                audio_data=audio_data, language="en", format="wav"
            )

            logger.success("✓ STT Transcription successful!")
            logger.info(f"  Text: {result.get('text', 'N/A')}")
            logger.info(f"  Language: {result.get('language', 'N/A')}")
            logger.info(f"  Duration: {result.get('duration', 'N/A')}s")
            logger.info(f"  Confidence: {result.get('confidence', 'N/A')}")
            logger.info(f"  Word Count: {result.get('word_count', 'N/A')}")
            logger.info(f"  Provider: {result.get('provider', 'N/A')}")

            return True
        else:
            logger.warning(
                f"No test audio file found at {test_audio_path}. Skipping STT test."
            )
            logger.info(
                "To test STT, place a WAV file at tests/fixtures/test_audio.wav"
            )
            return None

    except Exception as e:
        logger.error(f"✗ STT test failed: {str(e)}")
        return False


async def test_tts_provider():
    """Test Text-to-Speech provider"""
    logger.info("=" * 60)
    logger.info("Testing TTS Provider")
    logger.info("=" * 60)

    try:
        service = get_speech_service()

        logger.info(f"TTS Provider: {settings.TTS_PROVIDER}")

        test_text = "Hello, this is a test of the text to speech system. Your account balance is one thousand two hundred thirty four dollars and fifty six cents."

        logger.info(f"Synthesizing text: '{test_text[:50]}...'")

        audio_bytes = await service.synthesize_speech(
            text=test_text, language="en", speed=1.0, format="mp3"
        )

        logger.success("✓ TTS Synthesis successful!")
        logger.info(f"  Audio size: {len(audio_bytes)} bytes")
        logger.info(f"  Format: MP3")

        # Save output
        output_path = backend_path / "tests" / "output" / "test_tts_output.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"  Saved to: {output_path}")

        return True

    except Exception as e:
        logger.error(f"✗ TTS test failed: {str(e)}")
        return False


async def test_list_voices():
    """Test listing available voices"""
    logger.info("=" * 60)
    logger.info("Testing Voice Listing")
    logger.info("=" * 60)

    try:
        service = get_speech_service()

        voices = await service.list_voices(language="en")

        logger.success(f"✓ Found {len(voices)} voices")

        if voices:
            logger.info("Available voices:")
            for i, voice in enumerate(voices[:5], 1):  # Show first 5
                logger.info(
                    f"  {i}. {voice.get('name', 'N/A')} ({voice.get('id', 'N/A')})"
                )
                if voice.get("category"):
                    logger.info(f"     Category: {voice['category']}")

            if len(voices) > 5:
                logger.info(f"  ... and {len(voices) - 5} more")

        return True

    except Exception as e:
        logger.error(f"✗ Voice listing failed: {str(e)}")
        return False


async def test_health_check():
    """Test provider health checks"""
    logger.info("=" * 60)
    logger.info("Testing Provider Health")
    logger.info("=" * 60)

    try:
        service = get_speech_service()

        health = await service.check_health()

        logger.info(f"Service Status: {health.get('service', 'unknown')}")

        if "providers" in health:
            logger.info("Provider Status:")
            for provider_name, status in health["providers"].items():
                status_icon = "✓" if status.get("status") == "healthy" else "✗"
                logger.info(
                    f"  {status_icon} {provider_name}: {status.get('status', 'unknown')}"
                )
                if status.get("provider"):
                    logger.info(f"     Provider: {status['provider']}")
                if status.get("error"):
                    logger.warning(f"     Error: {status['error']}")

        return health.get("service") == "healthy"

    except Exception as e:
        logger.error(f"✗ Health check failed: {str(e)}")
        return False


async def test_audio_info():
    """Test audio info extraction"""
    logger.info("=" * 60)
    logger.info("Testing Audio Info")
    logger.info("=" * 60)

    try:
        service = get_speech_service()

        test_audio_path = backend_path / "tests" / "fixtures" / "test_audio.wav"

        if test_audio_path.exists():
            with open(test_audio_path, "rb") as f:
                audio_data = f.read()

            info = await service.get_audio_info(audio_data=audio_data, format="wav")

            logger.success("✓ Audio info extraction successful!")
            logger.info(f"  Duration: {info.get('duration', 'N/A')}s")
            logger.info(f"  Channels: {info.get('channels', 'N/A')}")
            logger.info(f"  Sample Rate: {info.get('sample_rate', 'N/A')} Hz")
            logger.info(f"  Sample Width: {info.get('sample_width', 'N/A')} bytes")
            logger.info(f"  Frame Count: {info.get('frame_count', 'N/A')}")
            logger.info(f"  Size: {info.get('size_bytes', 'N/A')} bytes")

            return True
        else:
            logger.warning(
                f"No test audio file found at {test_audio_path}. Skipping audio info test."
            )
            return None

    except Exception as e:
        logger.error(f"✗ Audio info test failed: {str(e)}")
        return False


def print_configuration():
    """Print current configuration"""
    logger.info("=" * 60)
    logger.info("Current Configuration")
    logger.info("=" * 60)

    config_items = {
        "STT Provider": settings.STT_PROVIDER,
        "TTS Provider": settings.TTS_PROVIDER,
        "STT Fallback": settings.ENABLE_STT_FALLBACK,
        "TTS Fallback": settings.ENABLE_TTS_FALLBACK,
        "OpenAI API Key": "✓ Set" if settings.OPENAI_API_KEY else "✗ Not set",
        "ElevenLabs API Key": "✓ Set" if settings.ELEVENLABS_API_KEY else "✗ Not set",
    }

    for key, value in config_items.items():
        logger.info(f"  {key}: {value}")

    logger.info("")


def print_summary(results):
    """Print test summary"""
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    total_tests = len([r for r in results.values() if r is not None])
    passed_tests = len([r for r in results.values() if r is True])
    failed_tests = len([r for r in results.values() if r is False])
    skipped_tests = len([r for r in results.values() if r is None])

    logger.info(f"Total Tests: {total_tests}")
    logger.success(f"Passed: {passed_tests}")
    logger.error(f"Failed: {failed_tests}")
    if skipped_tests > 0:
        logger.warning(f"Skipped: {skipped_tests}")

    logger.info("")

    for test_name, result in results.items():
        if result is True:
            logger.success(f"✓ {test_name}")
        elif result is False:
            logger.error(f"✗ {test_name}")
        else:
            logger.warning(f"⊘ {test_name} (skipped)")

    logger.info("=" * 60)

    return failed_tests == 0


async def main():
    """Run all tests"""
    logger.info("Speech Provider Test Suite")
    logger.info("=" * 60)
    logger.info("")

    # Print configuration
    print_configuration()

    # Run tests
    results = {
        "Health Check": await test_health_check(),
        "STT Provider": await test_stt_provider(),
        "TTS Provider": await test_tts_provider(),
        "Voice Listing": await test_list_voices(),
        "Audio Info": await test_audio_info(),
    }

    # Print summary
    logger.info("")
    success = print_summary(results)

    # Recommendations
    logger.info("")
    logger.info("Recommendations:")
    if not settings.OPENAI_API_KEY and settings.STT_PROVIDER == "openai":
        logger.warning("  • Set OPENAI_API_KEY in .env for OpenAI Whisper STT")
    if not settings.ELEVENLABS_API_KEY and settings.TTS_PROVIDER == "elevenlabs":
        logger.warning("  • Set ELEVENLABS_API_KEY in .env for ElevenLabs TTS")
    if settings.STT_PROVIDER == "placeholder":
        logger.info("  • Consider upgrading to OpenAI Whisper for better STT quality")
    if settings.TTS_PROVIDER == "placeholder":
        logger.info("  • Consider upgrading to ElevenLabs for better TTS quality")
    if not settings.ENABLE_STT_FALLBACK or not settings.ENABLE_TTS_FALLBACK:
        logger.warning("  • Enable fallback providers for production resilience")

    logger.info("")
    logger.info("For more information, see docs/SPEECH_PROVIDERS.md")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
