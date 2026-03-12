"""Code execution service backed by E2B sandboxes."""

from __future__ import annotations

import logging
from typing import Any

from e2b_code_interpreter import AsyncSandbox  # type: ignore[import-untyped]

from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "python",
    "javascript",
    "typescript",
}


def _format_logs(lines: list[str]) -> str:
    """Join streamed log lines into a single string."""
    return "".join(lines)


def _format_error(execution: Any) -> str:
    """Extract a useful error string from an E2B execution result."""
    stderr = _format_logs(execution.logs.stderr)
    if stderr:
        return stderr

    if execution.error:
        return execution.error.traceback or execution.error.value or execution.error.name

    return ""


def _format_output(execution: Any) -> str:
    """Extract stdout or expression result text from an E2B execution result."""
    stdout = _format_logs(execution.logs.stdout)
    if stdout:
        return stdout
    return execution.text or ""


async def ensure_execution_service_ready() -> None:
    """Log whether the E2B execution service is configured."""
    if not settings.e2b_api_key:
        logger.warning("E2B_API_KEY is not configured. Code execution requests will fail.")
        return

    logger.info(
        "E2B execution service configured for languages: %s",
        ", ".join(sorted(SUPPORTED_LANGUAGES)),
    )


async def execute_source(language: str, code: str) -> dict[str, str]:
    """Execute code in an ephemeral E2B sandbox."""
    if not settings.e2b_api_key:
        return {"output": "", "error": "Execution service unavailable: E2B_API_KEY is not set"}

    sandbox = None
    try:
        sandbox = await AsyncSandbox.create(api_key=settings.e2b_api_key)
        execution = await sandbox.run_code(
            code,
            language=language,
            timeout=settings.execution_timeout_seconds,
            request_timeout=settings.execution_request_timeout_seconds,
        )
        return {
            "output": _format_output(execution),
            "error": _format_error(execution),
        }
    except Exception as exc:
        logger.error("E2B execution error: %s", exc)
        return {"output": "", "error": f"Execution failed: {exc}"}
    finally:
        if sandbox is not None:
            try:
                await sandbox.kill(request_timeout=settings.execution_request_timeout_seconds)
            except Exception:
                logger.error("Failed to kill E2B sandbox during cleanup", exc_info=True)
