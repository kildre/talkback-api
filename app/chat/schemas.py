"""Chat Pydantic schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Base message schema."""

    role: str
    content: str


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    chat_id: int


class VoiceSettings(BaseModel):
    """Schema for voice settings."""

    voice: str = "en-GB-Neural2-B"
    speed: float = 3.0
    pitch: float = 5.0


class MessageResponse(MessageBase):
    """Schema for message response."""

    id: int
    chat_id: int
    created_at: datetime
    voice_settings: VoiceSettings | None = Field(
        default_factory=lambda: VoiceSettings(), description="Voice settings for TTS"
    )

    class Config:
        from_attributes = True


class ChatBase(BaseModel):
    """Base chat schema."""

    title: str


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""

    user_id: str


class ChatResponse(ChatBase):
    """Schema for chat response."""

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatWithMessages(ChatResponse):
    """Schema for chat response with messages."""

    messages: list[MessageResponse] = []


class ImageContent(BaseModel):
    """Schema for image content in a message."""

    type: Literal["image"] = "image"
    format: str  # jpeg, png, gif, webp
    source: dict  # {"bytes": base64_string} or {"s3Location": {"uri": "..."}}

    class Config:
        extra = "allow"


class DocumentContent(BaseModel):
    """Schema for document content in a message."""

    type: Literal["document"] = "document"
    format: str  # pdf, csv, doc, docx, xls, xlsx, html, txt, md
    name: str
    source: dict  # {"bytes": base64_string} or {"s3Location": {"uri": "..."}}

    class Config:
        extra = "allow"


class ChatRequest(BaseModel):
    """Schema for chat request with message and optional images/documents."""

    message: str = Field(
        ..., min_length=1, description="The message text (required, non-empty)"
    )
    chat_id: int | None = None
    images: list[ImageContent] | None = None
    documents: list[DocumentContent] | None = None
    enable_tools: bool = True  # Allow per-request tool control

    class Config:
        extra = "ignore"
