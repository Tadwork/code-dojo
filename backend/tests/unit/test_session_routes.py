"""Unit tests for session API routes."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.session import Session


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_session():
    """Create a mock session."""
    session = MagicMock(spec=Session)
    session.id = "test-id-123"
    session.session_code = "TEST1234"
    session.title = "Test Session"
    session.language = "python"
    session.code = ""
    session.created_at = MagicMock()
    session.created_at.isoformat.return_value = "2024-01-01T00:00:00"
    session.active_users = 0
    return session


class TestSessionRoutes:
    """Test session API routes."""

    def test_create_session_success(self, client, mock_session):
        """Test successful session creation."""
        with patch(
            "app.routes.sessions.SessionService.create_session",
            new_callable=AsyncMock,
            return_value=mock_session,
        ):
            response = client.post(
                "/api/sessions",
                json={"title": "Test Session", "language": "python"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_code"] == "TEST1234"
            assert data["title"] == "Test Session"
            assert data["language"] == "python"

    def test_create_session_default_language(self, client, mock_session):
        """Test session creation with default language."""
        with patch(
            "app.routes.sessions.SessionService.create_session",
            new_callable=AsyncMock,
            return_value=mock_session,
        ):
            response = client.post("/api/sessions", json={})

            assert response.status_code == 200
            data = response.json()
            assert data["language"] == "python"

    def test_get_session_success(self, client, mock_session):
        """Test successful session retrieval."""
        with patch(
            "app.routes.sessions.SessionService.get_session_by_code",
            new_callable=AsyncMock,
            return_value=mock_session,
        ):
            response = client.get("/api/sessions/TEST1234")

            assert response.status_code == 200
            data = response.json()
            assert data["session_code"] == "TEST1234"
            assert data["title"] == "Test Session"

    def test_get_session_not_found(self, client):
        """Test session retrieval when session doesn't exist."""
        with patch(
            "app.routes.sessions.SessionService.get_session_by_code",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = client.get("/api/sessions/NONEXIST")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    def test_get_session_case_insensitive(self, client, mock_session):
        """Test that session code lookup is case-insensitive."""
        with patch(
            "app.routes.sessions.SessionService.get_session_by_code",
            new_callable=AsyncMock,
            return_value=mock_session,
        ) as mock_get:
            response = client.get("/api/sessions/test1234")

            assert response.status_code == 200
            # Verify it was called with uppercase
            mock_get.assert_called_once()
            call_args = mock_get.call_args[0]
            assert call_args[1] == "TEST1234"

