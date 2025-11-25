"""Tests for chat API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.chat.models import Chat, Message


@pytest.fixture
def mock_bedrock_client():
    """Mock AWS Bedrock client."""
    with patch("app.chat.router.get_bedrock_client") as mock:
        client = MagicMock()
        # Mock the retrieve_and_generate method to return a proper response
        client.retrieve_and_generate.return_value = {
            "output": {"text": "Mocked AI response"}
        }
        mock.return_value = client
        yield client


@pytest.fixture
def mock_boto3_session():
    """Mock boto3 session for tool calling."""
    with patch("app.chat.router.boto3.Session") as mock_session:
        session = MagicMock()
        bedrock_runtime = MagicMock()
        session.client.return_value = bedrock_runtime
        mock_session.return_value = session
        yield session, bedrock_runtime


class TestChatEndpoints:
    """Test chat API endpoints."""

    @patch("app.chat.router.handle_knowledge_base_query", new_callable=AsyncMock)
    def test_send_message_creates_chat(
        self, mock_kb_query, client, db_session, mock_bedrock_client
    ):
        """Test sending a message creates a chat and message."""
        # Mock the knowledge base query to return a proper async response
        mock_kb_query.return_value = "Test response from AI"

        response = client.post(
            "/chat",
            json={"message": "Hello, test message", "enable_tools": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "chat_id" in data
        assert "content" in data
        assert data["role"] == "assistant"

        # Verify chat was created in database
        chat = db_session.query(Chat).filter(Chat.id == data["chat_id"]).first()
        assert chat is not None
        assert chat.user_id == "demo-user"

    def test_get_user_chats(self, client, db_session):
        """Test retrieving all chats for a user."""
        # Create test chats for demo-user
        chat1 = Chat(title="Chat 1", user_id="demo-user")
        chat2 = Chat(title="Chat 2", user_id="demo-user")
        chat3 = Chat(title="Chat 3", user_id="other-user")
        db_session.add_all([chat1, chat2, chat3])
        db_session.commit()

        response = client.get("/chat")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(chat["user_id"] == "demo-user" for chat in data)

    def test_get_chat_with_messages(self, client, db_session):
        """Test retrieving a specific chat with its messages."""
        # Create test chat and messages for demo-user
        chat = Chat(title="Test Chat", user_id="demo-user")
        db_session.add(chat)
        db_session.commit()

        message1 = Message(chat_id=chat.id, role="user", content="Hello")
        message2 = Message(chat_id=chat.id, role="assistant", content="Hi there!")
        db_session.add_all([message1, message2])
        db_session.commit()

        response = client.get(f"/chat/{chat.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chat.id
        assert data["title"] == "Test Chat"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "Hello"
        assert data["messages"][1]["content"] == "Hi there!"

    def test_get_nonexistent_chat(self, client):
        """Test retrieving a chat that doesn't exist."""
        response = client.get("/chat/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_chat(self, client, db_session):
        """Test deleting a chat."""
        # Create test chat for demo-user
        chat = Chat(title="Test Chat", user_id="demo-user")
        db_session.add(chat)
        db_session.commit()
        chat_id = chat.id

        response = client.delete(f"/chat/{chat_id}")
        assert response.status_code == 200

        # Verify chat was deleted
        deleted_chat = db_session.query(Chat).filter(Chat.id == chat_id).first()
        assert deleted_chat is None

    def test_delete_nonexistent_chat(self, client):
        """Test deleting a chat that doesn't exist."""
        response = client.delete("/chat/99999")
        assert response.status_code == 404

    @patch("app.chat.router.handle_knowledge_base_query")
    def test_send_message_to_existing_chat(
        self, mock_kb_query, client, db_session, mock_bedrock_client
    ):
        """Test sending a message to an existing chat."""
        mock_kb_query.return_value = "This is a test response"

        # Create a chat first
        chat = Chat(title="Test Chat", user_id="demo-user")
        db_session.add(chat)
        db_session.commit()

        response = client.post(
            "/chat",
            json={
                "message": "Hello, how are you?",
                "chat_id": chat.id,
                "enable_tools": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["chat_id"] == chat.id
        assert "content" in data

    @patch("app.chat.router.handle_tool_calling")
    def test_send_message_with_tools(self, mock_tool_calling, client, db_session):
        """Test sending a message with tool calling enabled."""
        mock_tool_calling.return_value = "Response with tools"

        # Create a chat first
        chat = Chat(title="Test Chat", user_id="demo-user")
        db_session.add(chat)
        db_session.commit()

        response = client.post(
            "/chat",
            json={
                "message": "What cases do I have?",
                "chat_id": chat.id,
                "enable_tools": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["chat_id"] == chat.id

    def test_send_message_without_chat_id_creates_new_chat(
        self, client, db_session, mock_bedrock_client
    ):
        """Test that sending a message without chat_id creates a new chat."""
        with patch("app.chat.router.handle_knowledge_base_query") as mock_kb_query:
            mock_kb_query.return_value = "New chat response"

            response = client.post(
                "/chat",
                json={"message": "Hello", "enable_tools": False},
            )
            assert response.status_code == 200
            data = response.json()
            assert "chat_id" in data
            assert "content" in data

            # Verify chat was created
            chat = db_session.query(Chat).filter(Chat.id == data["chat_id"]).first()
            assert chat is not None
            assert chat.user_id == "demo-user"

    def test_send_message_with_empty_text(self, client):
        """Test sending a message with empty text."""
        response = client.post(
            "/chat",
            json={"message": "", "enable_tools": False},
        )
        assert response.status_code == 422  # Validation error

    def test_send_message_with_images(self, client, db_session, mock_bedrock_client):
        """Test sending a message with image content."""
        with patch("app.chat.router.handle_knowledge_base_query") as mock_kb_query:
            mock_kb_query.return_value = "Image processed response"

            chat = Chat(title="Test Chat", user_id="demo-user")
            db_session.add(chat)
            db_session.commit()

            response = client.post(
                "/chat",
                json={
                    "message": "What's in this image?",
                    "chat_id": chat.id,
                    "images": [
                        {
                            "type": "image",
                            "format": "jpeg",
                            "source": {"bytes": "base64encodedstring"},
                        }
                    ],
                    "enable_tools": False,
                },
            )
            assert response.status_code == 200

    def test_send_message_with_documents(self, client, db_session, mock_bedrock_client):
        """Test sending a message with document content."""
        with patch("app.chat.router.handle_knowledge_base_query") as mock_kb_query:
            mock_kb_query.return_value = "Document processed response"

            chat = Chat(title="Test Chat", user_id="demo-user")
            db_session.add(chat)
            db_session.commit()

            response = client.post(
                "/chat",
                json={
                    "message": "Summarize this document",
                    "chat_id": chat.id,
                    "documents": [
                        {
                            "type": "document",
                            "format": "pdf",
                            "name": "test.pdf",
                            "source": {"bytes": "base64encodedstring"},
                        }
                    ],
                    "enable_tools": False,
                },
            )
            assert response.status_code == 200


class TestChatService:
    """Test chat service methods."""

    def test_create_chat_service(self, db_session):
        """Test chat creation through service."""
        from app.chat.schemas import ChatCreate
        from app.chat.services import ChatService

        service = ChatService(db_session)
        chat_data = ChatCreate(title="Service Test Chat", user_id="test-user")
        chat = service.create_chat(chat_data)

        assert chat.title == "Service Test Chat"
        assert chat.user_id == "test-user"
        assert chat.id is not None

    def test_get_chat_service(self, db_session):
        """Test getting chat through service."""
        from app.chat.services import ChatService

        # Create test chat
        chat = Chat(title="Test Chat", user_id="test-user")
        db_session.add(chat)
        db_session.commit()

        service = ChatService(db_session)
        retrieved_chat = service.get_chat(chat.id, "test-user")

        assert retrieved_chat is not None
        assert retrieved_chat.id == chat.id
        assert retrieved_chat.title == "Test Chat"

    def test_get_chat_wrong_user(self, db_session):
        """Test getting chat with wrong user_id returns None."""
        from app.chat.services import ChatService

        chat = Chat(title="Test Chat", user_id="test-user")
        db_session.add(chat)
        db_session.commit()

        service = ChatService(db_session)
        retrieved_chat = service.get_chat(chat.id, "wrong-user")

        assert retrieved_chat is None

    def test_create_message_service(self, db_session):
        """Test message creation through service."""
        from app.chat.schemas import MessageCreate
        from app.chat.services import ChatService

        # Create test chat
        chat = Chat(title="Test Chat", user_id="test-user")
        db_session.add(chat)
        db_session.commit()

        service = ChatService(db_session)
        message_data = MessageCreate(
            chat_id=chat.id, role="user", content="Test message"
        )
        message = service.create_message(message_data)

        assert message.chat_id == chat.id
        assert message.role == "user"
        assert message.content == "Test message"
        assert message.id is not None
