"""Tests for database module."""

import contextlib
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDatabase:
    """Test database functionality."""

    def test_database_session_creation(self, db_session):
        """Test that database session can be created."""
        from sqlalchemy import text

        assert db_session is not None
        # Verify session can execute queries
        result = db_session.execute(text("SELECT 1"))
        assert result is not None

    def test_get_db_generator(self):
        """Test get_db generator function."""
        from app.db import get_db

        # Create a test database session
        test_engine = create_engine("sqlite:///:memory:")
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        with patch("app.db.SessionLocal", TestSessionLocal):
            db_gen = get_db()
            db = next(db_gen)
            assert db is not None
            # Clean up
            with contextlib.suppress(StopIteration):
                next(db_gen)

    def test_database_base_model(self):
        """Test that Base is properly configured."""
        from app.db import Base

        assert Base is not None
        assert hasattr(Base, "metadata")

    def test_database_engine_configuration(self):
        """Test that database engine is properly configured."""
        from app.db import engine

        assert engine is not None
        assert engine.url is not None

    def test_session_local_configuration(self):
        """Test that SessionLocal is properly configured."""
        from app.db import SessionLocal

        assert SessionLocal is not None
        session = SessionLocal()
        assert session is not None
        session.close()

    def test_database_transaction_rollback(self, db_session):
        """Test that database transactions can be rolled back."""
        from app.chat.models import Chat

        # Create a chat
        chat = Chat(title="Test Chat", user_id="test-user")
        db_session.add(chat)
        db_session.flush()

        # Verify chat exists in session
        assert chat in db_session

        # Rollback
        db_session.rollback()

        # Verify chat is no longer in session
        assert chat not in db_session

    def test_database_transaction_commit(self, db_session):
        """Test that database transactions can be committed."""
        from app.chat.models import Chat

        # Create and commit a chat
        chat = Chat(title="Test Chat", user_id="test-user")
        db_session.add(chat)
        db_session.commit()

        # Verify chat has an ID after commit
        assert chat.id is not None

        # Verify chat can be queried
        retrieved_chat = db_session.query(Chat).filter(Chat.id == chat.id).first()
        assert retrieved_chat is not None
        assert retrieved_chat.title == "Test Chat"
