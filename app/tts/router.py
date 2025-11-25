"""Text-to-Speech API endpoints."""

import logging
import re

from fastapi import APIRouter, HTTPException, Response, status
from google.cloud import texttospeech

from app.config import settings
from app.tts.schemas import TTSRequest

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/tts",
    tags=["Text-to-Speech"],
)


def strip_markdown(text: str) -> str:
    """
    Strip markdown formatting from text for TTS.

    Args:
        text: Text with potential markdown formatting

    Returns:
        Plain text without markdown formatting
    """
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)

    # Remove headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold and italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"___(.+?)___", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)

    # Remove links but keep link text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", text)

    # Remove blockquotes
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r"^(-{3,}|_{3,}|\*{3,})$", "", text, flags=re.MULTILINE)

    # Remove list markers
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up extra whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def get_tts_client():
    """Get Google Cloud Text-to-Speech client."""
    try:
        return texttospeech.TextToSpeechClient()
    except Exception as e:
        logger.error("Failed to create TTS client: %s", e)
        return None


@router.post("/")
async def text_to_speech(request: TTSRequest) -> Response:
    """
    Convert text to speech using Google Cloud Text-to-Speech API.

    Args:
        request: TTS request with text, voice, speed, and pitch parameters

    Returns:
        Audio content as MP3

    Raises:
        HTTPException: If text is empty or TTS conversion fails
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text is required",
        )

    # Get TTS client
    client = get_tts_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-speech service is not available",
        )

    try:
        # Strip markdown formatting from text
        clean_text = strip_markdown(request.text)

        # Build the voice request
        synthesis_input = texttospeech.SynthesisInput(text=clean_text)

        # Configure voice parameters
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=request.voice,
        )

        # Configure audio output
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=request.speed,
            pitch=request.pitch,
        )

        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        # Return the audio content
        return Response(
            content=response.audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
            },
        )

    except Exception as e:
        logger.error("TTS error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-speech failed: {str(e)}",
        ) from e
