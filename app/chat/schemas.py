"""Chat Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
    """Base message schema."""

    role: str
    content: str


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    chat_id: int


class MessageResponse(MessageBase):
    """Schema for message response."""

    id: int
    chat_id: int
    created_at: datetime

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


class ChatRequest(BaseModel):
    """Schema for chat request with message."""

    message: str
    chat_id: int | None = None
