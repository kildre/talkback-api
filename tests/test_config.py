"""Tests for configuration module."""

import os
from unittest.mock import patch


class TestConfiguration:
    """Test configuration settings."""

    def test_default_settings(self):
        """Test default configuration values."""
        from app.config import Settings

        settings = Settings()
        assert settings.API_PREFIX == ""
        assert settings.DATABASE_URL == "sqlite:///./db.sqlite3"
        assert settings.ENABLE_TOOLS is True

    def test_settings_from_environment(self):
        """Test loading settings from environment variables."""
        from app.config import Settings

        with patch.dict(
            os.environ,
            {
                "API_PREFIX": "/api/v2",
                "DATABASE_URL": "postgresql://localhost/testdb",
                "ENABLE_TOOLS": "false",
                "AWS_DEFAULT_REGION": "us-west-2",
            },
        ):
            settings = Settings()
            assert settings.API_PREFIX == "/api/v2"
            assert settings.DATABASE_URL == "postgresql://localhost/testdb"
            assert settings.ENABLE_TOOLS is False
            assert settings.AWS_DEFAULT_REGION == "us-west-2"

    def test_aws_credentials_configuration(self):
        """Test AWS credentials configuration."""
        from app.config import Settings

        with patch.dict(
            os.environ,
            {
                "AWS_ACCESS_KEY_ID": "test-key-id",
                "AWS_SECRET_ACCESS_KEY": "test-secret",
                "AWS_DEFAULT_REGION": "us-east-1",
                "AWS_BEDROCK_KNOWLEDGE_BASE_ID": "test-kb-id",
                "AWS_BEDROCK_MODEL_ARN": "arn:aws:bedrock:us-east-1:model/test",
            },
        ):
            settings = Settings()
            assert settings.AWS_ACCESS_KEY_ID == "test-key-id"
            assert settings.AWS_SECRET_ACCESS_KEY == "test-secret"
            assert settings.AWS_DEFAULT_REGION == "us-east-1"
            assert settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID == "test-kb-id"
            assert settings.AWS_BEDROCK_MODEL_ARN == "arn:aws:bedrock:us-east-1:model/test"

    def test_tool_configuration(self):
        """Test tool calling configuration."""
        from app.config import Settings

        with patch.dict(
            os.environ,
            {
                "ENABLE_TOOLS": "true",
                "ENABLED_TOOLS": "get_current_time,calculate,search",
            },
        ):
            settings = Settings()
            assert settings.ENABLE_TOOLS is True
            assert settings.ENABLED_TOOLS == "get_current_time,calculate,search"

    def test_google_tts_configuration(self):
        """Test Google TTS configuration."""
        from app.config import Settings

        with patch.dict(
            os.environ,
            {
                "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
            },
        ):
            settings = Settings()
            assert settings.GOOGLE_APPLICATION_CREDENTIALS == "/path/to/credentials.json"

    def test_oidc_configuration(self):
        """Test OIDC configuration."""
        from app.config import Settings

        with patch.dict(
            os.environ,
            {
                "OIDC_CONFIG_URL": "https://auth.example.com/.well-known/openid-configuration",
            },
        ):
            settings = Settings()
            assert (
                settings.OIDC_CONFIG_URL
                == "https://auth.example.com/.well-known/openid-configuration"
            )

    def test_optional_settings_none_by_default(self):
        """Test that optional settings can be None when environment is cleared."""
        from app.config import Settings

        # Clear environment to test defaults
        env_vars_to_clear = [
            "OIDC_CONFIG_URL",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_DEFAULT_REGION",
            "AWS_BEDROCK_KNOWLEDGE_BASE_ID",
            "AWS_BEDROCK_MODEL_ARN",
            "ENABLED_TOOLS",
            "GOOGLE_APPLICATION_CREDENTIALS",
        ]
        with patch.dict(os.environ, dict.fromkeys(env_vars_to_clear, ""), clear=False):
            settings = Settings()
            # These should be None or empty when explicitly cleared
            assert settings.OIDC_CONFIG_URL in (None, "")
            assert settings.ENABLED_TOOLS in (None, "")
