"""Tests for AI assistant service."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from app.services.ai_assistant import generate_code, clean_code_response


class TestCleanCodeResponse:
    """Tests for clean_code_response function."""
    
    def test_clean_plain_code(self):
        """Test that plain code is returned unchanged."""
        code = "def hello():\n    print('Hello')"
        result = clean_code_response(code, "python")
        assert result == code
    
    def test_clean_code_with_language_fence(self):
        """Test removal of code fence with language."""
        code = "```python\ndef hello():\n    print('Hello')\n```"
        result = clean_code_response(code, "python")
        assert result == "def hello():\n    print('Hello')"
    
    def test_clean_code_with_generic_fence(self):
        """Test removal of generic code fence."""
        code = "```\ndef hello():\n    print('Hello')\n```"
        result = clean_code_response(code, "python")
        assert result == "def hello():\n    print('Hello')"
    
    def test_clean_code_strips_whitespace(self):
        """Test that whitespace is stripped."""
        code = "  \n  def hello():\n    print('Hello')  \n  "
        result = clean_code_response(code, "python")
        assert result == "def hello():\n    print('Hello')"


class TestGenerateCode:
    """Tests for generate_code function."""
    
    @pytest.mark.asyncio
    async def test_generate_code_success(self):
        """Test successful code generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "def add(a, b):\n    return a + b"}}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            result = await generate_code("Add two numbers", "", "python")
            
            assert result["code"] == "def add(a, b):\n    return a + b"
            assert result["error"] == ""
    
    @pytest.mark.asyncio
    async def test_generate_code_with_existing_code(self):
        """Test code modification."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "def add(a, b):\n    # Modified\n    return a + b"}}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            result = await generate_code(
                "Add a comment",
                "def add(a, b):\n    return a + b",
                "python"
            )
            
            assert "Modified" in result["code"]
            assert result["error"] == ""
    
    @pytest.mark.asyncio
    async def test_generate_code_empty_response(self):
        """Test handling of empty AI response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            result = await generate_code("Create something", "", "python")
            
            assert result["code"] == ""
            assert result["error"] == "No response from AI"
    
    @pytest.mark.asyncio
    async def test_generate_code_http_error(self):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.HTTPStatusError(
                "Server error",
                request=MagicMock(),
                response=mock_response
            )
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            result = await generate_code("Create something", "", "python")
            
            assert result["code"] == ""
            assert "AI service error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_generate_code_connection_error(self):
        """Test handling of connection errors."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.RequestError("Connection failed")
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance
            
            result = await generate_code("Create something", "", "python")
            
            assert result["code"] == ""
            assert result["error"] == "AI service unavailable"
