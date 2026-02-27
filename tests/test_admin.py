"""Tests for admin API endpoints."""

from fastapi import HTTPException


class TestAdminEndpoints:
    """Test admin API endpoints."""

    def test_get_current_user_success(self, app, db_session):
        """Test getting current user information with valid JWT."""
        from fastapi.testclient import TestClient

        from app.auth import validate_jwt

        # Override validate_jwt dependency to return mock user
        def mock_validate_jwt():
            return {
                "sub": "user-123",
                "email": "test@example.com",
                "name": "Test User",
            }

        app.dependency_overrides[validate_jwt] = mock_validate_jwt

        with TestClient(app) as client:
            response = client.get(
                "/admin/current-user",
                headers={"Authorization": "Bearer valid-token"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "user" in data
            assert data["user"]["sub"] == "user-123"
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["name"] == "Test User"

    def test_get_current_user_without_token(self, client):
        """Test getting current user without authentication token."""
        response = client.get("/admin/current-user")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, app, db_session):
        """Test getting current user with invalid JWT."""
        from fastapi.testclient import TestClient

        from app.auth import validate_jwt

        def mock_validate_jwt():
            raise HTTPException(status_code=401, detail="Invalid JWT token")

        app.dependency_overrides[validate_jwt] = mock_validate_jwt

        with TestClient(app) as client:
            response = client.get(
                "/admin/current-user",
                headers={"Authorization": "Bearer invalid-token"},
            )

            assert response.status_code == 401

    def test_get_current_user_expired_token(self, app, db_session):
        """Test getting current user with expired JWT."""
        from fastapi.testclient import TestClient

        from app.auth import validate_jwt

        def mock_validate_jwt():
            raise HTTPException(status_code=401, detail="Token expired")

        app.dependency_overrides[validate_jwt] = mock_validate_jwt

        with TestClient(app) as client:
            response = client.get(
                "/admin/current-user",
                headers={"Authorization": "Bearer expired-token"},
            )

            assert response.status_code == 401

        assert response.status_code == 401

    def test_get_current_user_malformed_auth_header(self, client):
        """Test getting current user with malformed authorization header."""
        response = client.get(
            "/admin/current-user",
            headers={"Authorization": "InvalidFormat"},
        )
        assert response.status_code == 401

    def test_get_current_user_partial_claims(self, app, db_session):
        """Test getting current user with partial JWT claims."""
        from fastapi.testclient import TestClient

        from app.auth import validate_jwt

        def mock_validate_jwt():
            return {
                "sub": "user-456",
                # Missing email and name fields
            }

        app.dependency_overrides[validate_jwt] = mock_validate_jwt

        with TestClient(app) as client:
            response = client.get(
                "/admin/current-user",
                headers={"Authorization": "Bearer valid-token"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["user"]["sub"] == "user-456"
