"""Tests for the E2B-backed code execution service."""

import logging
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.services.code_execution import (
    execute_source,
    ensure_execution_service_ready,
    SUPPORTED_LANGUAGES,
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


class TestEnsureExecutionServiceReady:
    """Tests for ensure_execution_service_ready."""

    @pytest.mark.asyncio
    async def test_logs_when_key_configured(self, caplog):
        """Test readiness logging when E2B is configured."""
        caplog.set_level(logging.INFO)
        with patch("app.services.code_execution.settings.e2b_api_key", "test-key"):
            await ensure_execution_service_ready()

        assert "E2B execution service configured" in caplog.text

    @pytest.mark.asyncio
    async def test_warns_when_key_missing(self, caplog):
        """Test readiness warning when E2B is not configured."""
        with patch("app.services.code_execution.settings.e2b_api_key", ""):
            await ensure_execution_service_ready()

        assert "E2B_API_KEY is not configured" in caplog.text


class TestExecuteSource:
    """Tests for execute_source function."""

    @pytest.mark.asyncio
    async def test_execute_python_success(self):
        """Test successful Python execution."""
        mock_execution = SimpleNamespace(
            logs=SimpleNamespace(stdout=["Hello\n"], stderr=[]),
            error=None,
            text=None,
        )
        mock_sandbox = AsyncMock()
        mock_sandbox.run_code.return_value = mock_execution

        with (
            patch("app.services.code_execution.settings.e2b_api_key", "test-key"),
            patch(
                "app.services.code_execution.AsyncSandbox.create",
                new=AsyncMock(return_value=mock_sandbox),
            ),
        ):
            result = await execute_source("python", "print('Hello')")

            assert result["output"] == "Hello\n"
            assert result["error"] == ""
            mock_sandbox.run_code.assert_awaited_once()
            mock_sandbox.kill.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_with_stderr(self):
        """Test execution with stderr output."""
        mock_execution = SimpleNamespace(
            logs=SimpleNamespace(stdout=[], stderr=["Error occurred"]),
            error=None,
            text=None,
        )
        mock_sandbox = AsyncMock()
        mock_sandbox.run_code.return_value = mock_execution

        with (
            patch("app.services.code_execution.settings.e2b_api_key", "test-key"),
            patch(
                "app.services.code_execution.AsyncSandbox.create",
                new=AsyncMock(return_value=mock_sandbox),
            ),
        ):
            result = await execute_source("python", "raise Exception()")

            assert result["error"] == "Error occurred"

    @pytest.mark.asyncio
    async def test_execute_returns_expression_text(self):
        """Test returning expression text when stdout is empty."""
        mock_execution = SimpleNamespace(
            logs=SimpleNamespace(stdout=[], stderr=[]),
            error=None,
            text="2",
        )
        mock_sandbox = AsyncMock()
        mock_sandbox.run_code.return_value = mock_execution

        with (
            patch("app.services.code_execution.settings.e2b_api_key", "test-key"),
            patch(
                "app.services.code_execution.AsyncSandbox.create",
                new=AsyncMock(return_value=mock_sandbox),
            ),
        ):
            result = await execute_source("python", "1 + 1")

            assert result["output"] == "2"

    @pytest.mark.asyncio
    async def test_execute_handles_execution_error(self):
        """Test returning structured execution errors from E2B."""
        mock_execution = SimpleNamespace(
            logs=SimpleNamespace(stdout=[], stderr=[]),
            error=SimpleNamespace(
                traceback="Traceback...",
                value="name 'x' is not defined",
                name="NameError",
            ),
            text=None,
        )
        mock_sandbox = AsyncMock()
        mock_sandbox.run_code.return_value = mock_execution

        with (
            patch("app.services.code_execution.settings.e2b_api_key", "test-key"),
            patch(
                "app.services.code_execution.AsyncSandbox.create",
                new=AsyncMock(return_value=mock_sandbox),
            ),
        ):
            result = await execute_source("python", "print('test')")

            assert result["error"] == "Traceback..."

    @pytest.mark.asyncio
    async def test_execute_missing_api_key(self):
        """Test handling of missing E2B API key."""
        with patch("app.services.code_execution.settings.e2b_api_key", ""):
            result = await execute_source("python", "print('test')")

            assert "E2B_API_KEY is not set" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_general_exception(self):
        """Test handling of general exceptions."""
        mock_sandbox = AsyncMock()
        mock_sandbox.run_code.side_effect = Exception("Unexpected error")

        with (
            patch("app.services.code_execution.settings.e2b_api_key", "test-key"),
            patch(
                "app.services.code_execution.AsyncSandbox.create",
                new=AsyncMock(return_value=mock_sandbox),
            ),
        ):
            result = await execute_source("python", "print('test')")

            assert "Execution failed: Unexpected error" == result["error"]
            mock_sandbox.kill.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_passes_requested_language(self):
        """Test that the selected language is passed to E2B."""
        mock_execution = SimpleNamespace(
            logs=SimpleNamespace(stdout=["hello\n"], stderr=[]),
            error=None,
            text=None,
        )
        mock_sandbox = AsyncMock()
        mock_sandbox.run_code.return_value = mock_execution

        with (
            patch("app.services.code_execution.settings.e2b_api_key", "test-key"),
            patch(
                "app.services.code_execution.AsyncSandbox.create",
                new=AsyncMock(return_value=mock_sandbox),
            ),
        ):
            await execute_source("javascript", "console.log('hello')")

            assert mock_sandbox.run_code.await_args.kwargs["language"] == "javascript"
