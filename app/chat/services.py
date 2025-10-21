"""Chat business logic and service functions."""


from sqlalchemy.orm import Session

from app.chat.models import Chat, Message
from app.chat.schemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse


class ChatService:
    """Service class for chat-related operations."""

    def __init__(self, db: Session):
        self.db = db

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
        return (
            self.db.query(Chat)
            .filter(Chat.id == chat_id, Chat.user_id == user_id)
            .first()
        )

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
