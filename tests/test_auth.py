"""Tests for authentication module."""

from unittest.mock import MagicMock, patch

import pytest


class TestAuthentication:
    """Test authentication functions."""

    @patch("app.auth.requests.get")
    def test_get_keycloak_jwks_success(self, mock_get):
        """Test successful retrieval of Keycloak JWKS."""
        from app.auth import get_keycloak_jwks

        # Mock the well-known config response
        well_known_response = MagicMock()
        well_known_response.json.return_value = {
            "jwks_uri": "https://keycloak.example.com/jwks"
        }

        # Mock the JWKS response
        jwks_response = MagicMock()
        jwks_response.json.return_value = {
            "keys": [
                {
                    "kid": "test-key-id",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig",
                    "n": "test-modulus",
                    "e": "AQAB",
                }
            ]
        }

        mock_get.side_effect = [well_known_response, jwks_response]

        keys = get_keycloak_jwks()

        assert len(keys) == 1
        assert keys[0]["kid"] == "test-key-id"
        assert keys[0]["alg"] == "RS256"

    @patch("app.auth.requests.get")
    def test_get_keycloak_jwks_failure(self, mock_get):
        """Test JWKS retrieval when request fails."""
        from app.auth import get_keycloak_jwks

        mock_get.side_effect = Exception("Connection error")

        with pytest.raises(Exception):
            get_keycloak_jwks()

    @patch("app.auth.get_keycloak_jwks")
    @patch("app.auth.jwt.decode")
    @patch("app.auth.jwt.get_unverified_header")
    def test_validate_jwt_success(self, mock_get_header, mock_decode, mock_get_jwks):
        """Test successful JWT validation."""
        from app.auth import validate_jwt

        # Mock header
        mock_get_header.return_value = {"kid": "test-key-id", "alg": "RS256"}

        # Mock JWKS
        mock_get_jwks.return_value = [
            {
                "kid": "test-key-id",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "test-modulus",
                "e": "AQAB",
            }
        ]

        # Mock decode
        mock_decode.return_value = {
            "sub": "user-123",
            "email": "test@example.com",
            "exp": 9999999999,
        }

        payload = validate_jwt("test-token")

        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"

    @patch("app.auth.get_keycloak_jwks")
    @patch("app.auth.jwt.get_unverified_header")
    def test_validate_jwt_key_not_found(self, mock_get_header, mock_get_jwks):
        """Test JWT validation when key is not found in JWKS."""
        from fastapi import HTTPException

        from app.auth import validate_jwt

        # Mock header with different kid
        mock_get_header.return_value = {"kid": "wrong-key-id", "alg": "RS256"}

        # Mock JWKS with different key
        mock_get_jwks.return_value = [
            {
                "kid": "test-key-id",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "test-modulus",
                "e": "AQAB",
            }
        ]

        with pytest.raises(HTTPException) as exc_info:
            validate_jwt("test-token")

        assert exc_info.value.status_code == 401
        assert "not found" in exc_info.value.detail

    @patch("app.auth.get_keycloak_jwks")
    @patch("app.auth.jwt.decode")
    @patch("app.auth.jwt.get_unverified_header")
    def test_validate_jwt_invalid_token(
        self, mock_get_header, mock_decode, mock_get_jwks
    ):
        """Test JWT validation with invalid token."""
        from fastapi import HTTPException

        from app.auth import validate_jwt

        # Mock header
        mock_get_header.return_value = {"kid": "test-key-id", "alg": "RS256"}

        # Mock JWKS
        mock_get_jwks.return_value = [
            {
                "kid": "test-key-id",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "test-modulus",
                "e": "AQAB",
            }
        ]

        # Mock decode to raise exception
        mock_decode.side_effect = Exception("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            validate_jwt("invalid-token")

        assert exc_info.value.status_code == 401
        assert "Invalid" in exc_info.value.detail
