"""Tests for TTS (Text-to-Speech) API endpoints."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_tts_client():
    """Mock Google Cloud TTS client."""
    with patch("app.tts.router.get_tts_client") as mock:
        client = MagicMock()
        # Mock the synthesize_speech response
        response = MagicMock()
        response.audio_content = b"mock_audio_content"
        client.synthesize_speech.return_value = response
        mock.return_value = client
        yield client


class TestTTSEndpoints:
    """Test TTS API endpoints."""

    def test_tts_basic_request(self, client, mock_tts_client):
        """Test basic text-to-speech conversion."""
        response = client.post(
            "/tts/",
            json={
                "text": "Hello world",
                "voice": "en-US-Neural2-D",
                "speed": 1.0,
                "pitch": 0.0,
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == b"mock_audio_content"

        # Verify TTS client was called
        mock_tts_client.synthesize_speech.assert_called_once()

    def test_tts_with_default_parameters(self, client, mock_tts_client):
        """Test TTS with default voice, speed, and pitch parameters."""
        response = client.post(
            "/tts/",
            json={"text": "Test message"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"

        # Verify default parameters were used
        call_args = mock_tts_client.synthesize_speech.call_args
        assert call_args is not None

    def test_tts_with_markdown_text(self, client, mock_tts_client):
        """Test TTS with markdown formatted text."""
        markdown_text = """
        # Hello World
        This is **bold** and *italic* text.
        - List item 1
        - List item 2
        
        ```python
        print("code block")
        ```
        
        [Link](https://example.com)
        """
        response = client.post(
            "/tts/",
            json={"text": markdown_text},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"

        # Verify markdown was stripped (text passed to TTS should not contain markdown)
        call_args = mock_tts_client.synthesize_speech.call_args
        if call_args and len(call_args[0]) > 0:
            synthesis_input = call_args[0][0].input
            # The text should be stripped of markdown
            assert "**" not in synthesis_input.text
            assert "```" not in synthesis_input.text
            assert "#" not in synthesis_input.text.split("\n")[0]

    def test_tts_empty_text(self, client):
        """Test TTS with empty text."""
        response = client.post(
            "/tts/",
            json={"text": ""},
        )
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()

    def test_tts_whitespace_only_text(self, client):
        """Test TTS with whitespace-only text."""
        response = client.post(
            "/tts/",
            json={"text": "   \n\t  "},
        )
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()

    def test_tts_speed_validation(self, client, mock_tts_client):
        """Test TTS with various speed values."""
        # Valid speed
        response = client.post(
            "/tts/",
            json={"text": "Test", "speed": 2.0},
        )
        assert response.status_code == 200

        # Speed too low
        response = client.post(
            "/tts/",
            json={"text": "Test", "speed": 0.1},
        )
        assert response.status_code == 422  # Validation error

        # Speed too high
        response = client.post(
            "/tts/",
            json={"text": "Test", "speed": 5.0},
        )
        assert response.status_code == 422  # Validation error

    def test_tts_pitch_validation(self, client, mock_tts_client):
        """Test TTS with various pitch values."""
        # Valid pitch
        response = client.post(
            "/tts/",
            json={"text": "Test", "pitch": 5.0},
        )
        assert response.status_code == 200

        # Pitch too low
        response = client.post(
            "/tts/",
            json={"text": "Test", "pitch": -25.0},
        )
        assert response.status_code == 422  # Validation error

        # Pitch too high
        response = client.post(
            "/tts/",
            json={"text": "Test", "pitch": 25.0},
        )
        assert response.status_code == 422  # Validation error

    def test_tts_different_voices(self, client, mock_tts_client):
        """Test TTS with different voice options."""
        voices = [
            "en-US-Neural2-D",
            "en-US-Neural2-A",
            "en-GB-Neural2-B",
            "es-ES-Neural2-A",
        ]
        for voice in voices:
            response = client.post(
                "/tts/",
                json={"text": "Hello", "voice": voice},
            )
            assert response.status_code == 200

    @patch("app.tts.router.get_tts_client")
    def test_tts_client_failure(self, mock_get_client, client):
        """Test TTS when client creation fails."""
        mock_get_client.return_value = None

        response = client.post(
            "/tts/",
            json={"text": "Test"},
        )
        assert response.status_code == 503
        assert "not available" in response.json()["detail"].lower()

    @patch("app.tts.router.get_tts_client")
    def test_tts_synthesis_error(self, mock_get_client, client):
        """Test TTS when synthesis fails."""
        mock_client = MagicMock()
        mock_client.synthesize_speech.side_effect = Exception("Synthesis failed")
        mock_get_client.return_value = mock_client

        response = client.post(
            "/tts/",
            json={"text": "Test"},
        )
        assert response.status_code == 500

    def test_tts_long_text(self, client, mock_tts_client):
        """Test TTS with long text."""
        long_text = "This is a test sentence. " * 100
        response = client.post(
            "/tts/",
            json={"text": long_text},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"

    def test_tts_special_characters(self, client, mock_tts_client):
        """Test TTS with special characters."""
        special_text = "Hello! How are you? I'm fine. #hashtag @mention $100"
        response = client.post(
            "/tts/",
            json={"text": special_text},
        )
        assert response.status_code == 200

    def test_tts_unicode_text(self, client, mock_tts_client):
        """Test TTS with unicode characters."""
        unicode_text = "Hello 世界 🌍 café résumé"
        response = client.post(
            "/tts/",
            json={"text": unicode_text},
        )
        assert response.status_code == 200


class TestMarkdownStripping:
    """Test markdown stripping functionality."""

    def test_strip_markdown_headers(self):
        """Test stripping markdown headers."""
        from app.tts.router import strip_markdown

        text = "# Header 1\n## Header 2\n### Header 3"
        result = strip_markdown(text)
        assert "#" not in result
        assert "Header 1" in result
        assert "Header 2" in result

    def test_strip_markdown_bold_italic(self):
        """Test stripping bold and italic."""
        from app.tts.router import strip_markdown

        text = "This is **bold** and *italic* and ***both***"
        result = strip_markdown(text)
        assert "**" not in result
        assert "*" not in result
        assert "bold" in result
        assert "italic" in result

    def test_strip_markdown_code_blocks(self):
        """Test stripping code blocks."""
        from app.tts.router import strip_markdown

        text = "Here's code:\n```python\nprint('hello')\n```\nEnd code"
        result = strip_markdown(text)
        assert "```" not in result
        assert "python" not in result or "print" not in result

    def test_strip_markdown_links(self):
        """Test stripping links but keeping link text."""
        from app.tts.router import strip_markdown

        text = "Check out [this link](https://example.com)"
        result = strip_markdown(text)
        assert "this link" in result
        assert "https://example.com" not in result
        assert "[" not in result
        assert "]" not in result

    def test_strip_markdown_lists(self):
        """Test stripping list markers."""
        from app.tts.router import strip_markdown

        text = "- Item 1\n- Item 2\n1. Numbered\n2. List"
        result = strip_markdown(text)
        assert "Item 1" in result
        assert "Item 2" in result
        # List markers should be removed
        lines = result.split("\n")
        for line in lines:
            if line.strip():
                assert not line.strip().startswith("-")
                assert not line.strip()[0].isdigit() or not line.strip()[1] == "."

    def test_strip_markdown_blockquotes(self):
        """Test stripping blockquotes."""
        from app.tts.router import strip_markdown

        text = "> This is a quote\n> Another line"
        result = strip_markdown(text)
        assert ">" not in result
        assert "This is a quote" in result

    def test_strip_markdown_html_tags(self):
        """Test stripping HTML tags."""
        from app.tts.router import strip_markdown

        text = "This is <strong>bold</strong> and <em>italic</em>"
        result = strip_markdown(text)
        assert "<" not in result
        assert ">" not in result
        assert "bold" in result
        assert "italic" in result

    def test_strip_markdown_complex(self):
        """Test stripping complex markdown."""
        from app.tts.router import strip_markdown

        text = """
# Title

This is **important** text with `code` and a [link](url).

- List item
- Another item

```python
def hello():
    print("world")
```

> Quote here
"""
        result = strip_markdown(text)
        assert "#" not in result
        assert "**" not in result
        assert "`" not in result
        assert "[" not in result
        assert "```" not in result
        assert ">" not in result
        assert "important" in result
        assert "Title" in result
