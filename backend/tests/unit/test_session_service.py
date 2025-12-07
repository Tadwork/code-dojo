"""Unit tests for session service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.session_service import SessionService
from app.models.session import Session


class TestSessionService:
    """Test SessionService class."""

    def test_generate_session_code(self):
        """Test session code generation."""
        code = SessionService.generate_session_code()
        assert len(code) == 8
        assert code.isupper()
        # token_urlsafe can generate codes with hyphens, so check alphanumeric or hyphen
        assert all(c.isalnum() or c == "-" for c in code)

    def test_generate_session_code_uniqueness(self):
        """Test that generated codes are likely unique."""
        codes = {SessionService.generate_session_code() for _ in range(100)}
        # With 100 attempts, we should have high uniqueness
        assert len(codes) > 90

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test creating a session."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_session = MagicMock(spec=Session)
        mock_session.session_code = "TEST1234"
        mock_session.title = "Test Session"
        mock_session.language = "python"
        mock_session.code = ""
        mock_session.id = "test-id"
        mock_session.created_at = None
        mock_session.active_users = 0

        with (
            patch.object(SessionService, "get_session_by_code", return_value=None),
            patch.object(Session, "__init__", return_value=None) as mock_init,
        ):
            mock_init.return_value = None
            mock_db.add = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await SessionService.create_session(
                mock_db, title="Test Session", language="python"
            )

            assert mock_db.add.called
            assert mock_db.commit.called
            assert mock_db.refresh.called
            assert result.title == "Test Session"
            assert result.language == "python"

    @pytest.mark.asyncio
    async def test_get_session_by_code_found(self):
        """Test getting a session by code when it exists."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_session = MagicMock(spec=Session)
        mock_session.session_code = "TEST1234"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session

        with patch("app.services.session_service.select"):
            mock_db.execute = AsyncMock(return_value=mock_result)

            result = await SessionService.get_session_by_code(mock_db, "TEST1234")

            assert result == mock_session
            assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_get_session_by_code_not_found(self):
        """Test getting a session by code when it doesn't exist."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        with patch("app.services.session_service.select"):
            mock_db.execute = AsyncMock(return_value=mock_result)

            result = await SessionService.get_session_by_code(mock_db, "NONEXIST")

            assert result is None

    @pytest.mark.asyncio
    async def test_update_session_code(self):
        """Test updating session code."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_session = MagicMock(spec=Session)
        mock_session.code = "old code"

        with patch.object(SessionService, "get_session_by_code", return_value=mock_session):
            result = await SessionService.update_session_code(mock_db, "TEST1234", "new code")

            assert mock_session.code == "new code"
            assert mock_db.commit.called
            assert mock_db.refresh.called
            assert result == mock_session

    @pytest.mark.asyncio
    async def test_update_session_code_not_found(self):
        """Test updating code for non-existent session."""
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(SessionService, "get_session_by_code", return_value=None):
            result = await SessionService.update_session_code(mock_db, "NONEXIST", "new code")

            assert result is None
            assert not mock_db.commit.called

    @pytest.mark.asyncio
    async def test_update_session_language(self):
        """Test updating session language."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_session = MagicMock(spec=Session)
        mock_session.language = "python"

        with patch.object(SessionService, "get_session_by_code", return_value=mock_session):
            result = await SessionService.update_session_language(mock_db, "TEST1234", "javascript")

            assert mock_session.language == "javascript"
            assert mock_db.commit.called
            assert mock_db.refresh.called
            assert result == mock_session

    @pytest.mark.asyncio
    async def test_update_session_language_not_found(self):
        """Test updating language for non-existent session."""
        mock_db = AsyncMock(spec=AsyncSession)

        with patch.object(SessionService, "get_session_by_code", return_value=None):
            result = await SessionService.update_session_language(mock_db, "NONEXIST", "javascript")

            assert result is None
            assert not mock_db.commit.called
