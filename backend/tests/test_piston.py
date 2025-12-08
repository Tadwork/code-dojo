"""Tests for Piston service."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from app.services.piston import (
    execute_source,
    ensure_languages_installed,
    SUPPORTED_LANGUAGES,
    LANG_MAP,
)


class TestSupportedLanguages:
    """Tests for language configuration."""

    def test_supported_languages_not_empty(self):
        """Test that supported languages set is populated."""
        assert len(SUPPORTED_LANGUAGES) > 0

    def test_python_in_supported(self):
        """Test that Python is supported."""
        assert "python" in SUPPORTED_LANGUAGES

    def test_javascript_in_supported(self):
        """Test that JavaScript is supported."""
        assert "javascript" in SUPPORTED_LANGUAGES

    def test_lang_map_matches_supported(self):
        """Test that LANG_MAP keys match SUPPORTED_LANGUAGES."""
        assert set(LANG_MAP.keys()) == SUPPORTED_LANGUAGES


class TestEnsureLanguagesInstalled:
    """Tests for ensure_languages_installed function."""

    @pytest.mark.asyncio
    async def test_ensure_languages_success(self):
        """Test successful connection to Piston API."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"language": "python", "version": "3.10.0"},
            {"language": "javascript", "version": "18.0.0"},
        ]
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            # Should not raise
            await ensure_languages_installed()

    @pytest.mark.asyncio
    async def test_ensure_languages_connection_error(self):
        """Test handling of connection errors."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = Exception("Connection failed")
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            # Should not raise, just log error
            await ensure_languages_installed()


class TestExecuteSource:
    """Tests for execute_source function."""

    @pytest.mark.asyncio
    async def test_execute_python_success(self):
        """Test successful Python execution."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "run": {"stdout": "Hello\n", "stderr": "", "code": 0}
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await execute_source("python", "print('Hello')")

            assert result["output"] == "Hello\n"
            assert result["error"] == ""

    @pytest.mark.asyncio
    async def test_execute_with_stderr(self):
        """Test execution with stderr output."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "run": {"stdout": "", "stderr": "Error occurred", "code": 1}
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await execute_source("python", "raise Exception()")

            assert result["error"] == "Error occurred"

    @pytest.mark.asyncio
    async def test_execute_invalid_response(self):
        """Test handling of invalid API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}  # Missing 'run' key
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await execute_source("python", "print('test')")

            assert result["error"] == "Invalid response from execution engine"

    @pytest.mark.asyncio
    async def test_execute_http_error(self):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.HTTPStatusError(
                "Server error", request=MagicMock(), response=mock_response
            )
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await execute_source("python", "print('test')")

            assert "Execution failed" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_connection_error(self):
        """Test handling of connection errors."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.RequestError("Connection failed")
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await execute_source("python", "print('test')")

            assert result["error"] == "Execution service unavailable"

    @pytest.mark.asyncio
    async def test_execute_general_exception(self):
        """Test handling of general exceptions."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = Exception("Unexpected error")
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            result = await execute_source("python", "print('test')")

            assert "Unexpected error" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_language_mapping(self):
        """Test that language mapping works correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "run": {"stdout": "test", "stderr": "", "code": 0}
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            # cpp should be mapped to c++
            await execute_source("cpp", "int main() {}")

            # Check that the correct language was sent
            call_args = mock_instance.post.call_args
            payload = call_args.kwargs.get("json") or call_args[1].get("json")
            assert payload["language"] == "c++"
