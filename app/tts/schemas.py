"""TTS Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """Schema for text-to-speech request."""

    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field(
        default="en-US-Neural2-D",
        description="Voice name (e.g., en-US-Neural2-D)",
    )
    speed: float = Field(
        default=0.9,
        ge=0.25,
        le=4.0,
        description="Speaking rate (0.25 to 4.0)",
    )
    pitch: float = Field(
        default=-2.0,
        ge=-20.0,
        le=20.0,
        description="Voice pitch (-20.0 to 20.0)",
    )
