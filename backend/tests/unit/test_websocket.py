"""Unit tests for WebSocket routes."""

import pytest
from unittest.mock import AsyncMock
from fastapi import WebSocket

from app.routes.websocket import ConnectionManager


class TestConnectionManager:
    """Test ConnectionManager class."""

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting a WebSocket."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()

        await cm.connect(mock_websocket, "TEST1234")

        assert "TEST1234" in cm.active_connections
        assert mock_websocket in cm.active_connections["TEST1234"]
        assert mock_websocket.accept.called

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting a WebSocket."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        cm.active_connections["TEST1234"] = {mock_websocket}

        cm.disconnect(mock_websocket, "TEST1234")

        assert "TEST1234" not in cm.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_last_connection(self):
        """Test disconnecting the last connection removes session."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        cm.active_connections["TEST1234"] = {mock_websocket}

        cm.disconnect(mock_websocket, "TEST1234")

        assert "TEST1234" not in cm.active_connections

    @pytest.mark.asyncio
    async def test_broadcast(self):
        """Test broadcasting a message."""
        cm = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws1.send_json = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        cm.active_connections["TEST1234"] = {mock_ws1, mock_ws2}

        message = {"type": "test", "data": "hello"}
        await cm.broadcast("TEST1234", message, exclude=mock_ws1)

        # Only ws2 should receive the message
        assert mock_ws2.send_json.called
        mock_ws2.send_json.assert_called_once_with(message)
        assert not mock_ws1.send_json.called

    @pytest.mark.asyncio
    async def test_broadcast_removes_disconnected(self):
        """Test that disconnected connections are removed during broadcast."""
        cm = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws1.send_json = AsyncMock(side_effect=Exception("Disconnected"))
        mock_ws2.send_json = AsyncMock()

        cm.active_connections["TEST1234"] = {mock_ws1, mock_ws2}

        message = {"type": "test", "data": "hello"}
        await cm.broadcast("TEST1234", message)

        # ws1 should be removed due to error
        assert mock_ws2 in cm.active_connections.get("TEST1234", set())
        assert mock_ws1 not in cm.active_connections.get("TEST1234", set())

