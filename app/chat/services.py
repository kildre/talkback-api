"""Chat business logic and service functions."""

from __future__ import annotations

import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy.orm import Session

from app.chat.models import Chat, Message
from app.chat.schemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse
from app.config import settings

logger = logging.getLogger(__name__)


class ChatService:
    """Service class for chat-related operations."""

    def __init__(self, db: Session):
        self.db = db

    def generate_chat_title(self, message: str) -> str:
        """Generate a meaningful title for a chat based on the first message."""
        logger.info("Attempting to generate title for message: %s...", message[:100])

        try:
            # Check if AWS credentials are configured
            if (
                not settings.AWS_ACCESS_KEY_ID
                or settings.AWS_ACCESS_KEY_ID in ["1234", "REPLACE_WITH_YOUR_ACCESS_KEY_ID"]
                or not settings.AWS_SECRET_ACCESS_KEY
                or settings.AWS_SECRET_ACCESS_KEY in ["REPLACE_WITH_YOUR_SECRET_ACCESS_KEY"]
            ):
                logger.warning("AWS credentials not configured, using truncated message")
                return message[:50] + "..." if len(message) > 50 else message

            session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION or "us-east-1",
            )
            bedrock_runtime = session.client("bedrock-runtime")

            # Use Claude to generate a concise title
            prompt = (
                "Generate a brief, meaningful title (3-6 words max) "
                "for a chat conversation that starts with this message:\n\n"
                f'"{message}"\n\n'
                "Respond with ONLY the title, no quotes, no explanation, "
                "no punctuation at the end."
            )

            logger.info("Calling Claude API for title generation...")
            response = bedrock_runtime.converse(
                modelId="us.anthropic.claude-sonnet-4-6",
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={
                    "temperature": 0.3,
                    "maxTokens": 50,
                },
            )

            title = (
                response.get("output", {})
                .get("message", {})
                .get("content", [{}])[0]
                .get("text", "")
                .strip()
            )

            logger.info("Claude returned title: %s", title)

            # Fallback if Claude returns nothing or too long
            if not title or len(title) > 100:
                logger.warning(
                    "Invalid title from Claude (empty or too long: %s chars)",
                    len(title) if title else 0,
                )
                return message[:50] + "..." if len(message) > 50 else message

            return title

        except (BotoCoreError, ClientError) as e:
            logger.error("Error generating chat title with Bedrock: %s", e)
            return message[:50] + "..." if len(message) > 50 else message
        except Exception as e:
            logger.error("Unexpected error generating chat title: %s", e)
            return message[:50] + "..." if len(message) > 50 else message

    def create_chat(self, chat_data: ChatCreate) -> ChatResponse:
        """Create a new chat conversation."""
        db_chat = Chat(
            title=chat_data.title,
            user_id=chat_data.user_id,
        )
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return ChatResponse.model_validate(db_chat)

    def get_chat(self, chat_id: int, user_id: str) -> Chat | None:
        """Get a chat by ID for a specific user."""
        return self.db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()

    def get_user_chats(self, user_id: str) -> list[ChatResponse]:
        """Get all chats for a user."""
        chats = self.db.query(Chat).filter(Chat.user_id == user_id).all()
        return [ChatResponse.model_validate(chat) for chat in chats]

    def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create a new message in a chat."""
        db_message = Message(
            chat_id=message_data.chat_id,
            role=message_data.role,
            content=message_data.content,
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return MessageResponse.model_validate(db_message)

    def get_chat_messages(self, chat_id: int) -> list[MessageResponse]:
        """Get all messages for a chat."""
        messages = (
            self.db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at)
            .all()
        )
        return [MessageResponse.model_validate(message) for message in messages]

    def delete_chat(self, chat_id: int, user_id: str) -> bool:
        """Delete a chat and all its messages."""
        chat = self.get_chat(chat_id, user_id)
        if not chat:
            return False

        # Delete all messages in the chat
        self.db.query(Message).filter(Message.chat_id == chat_id).delete()

        # Delete the chat
        self.db.delete(chat)
        self.db.commit()
        return True
