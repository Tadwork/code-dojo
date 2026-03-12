"""Unit tests for WebSocket routes."""

import pytest
from unittest.mock import AsyncMock
from fastapi import WebSocket

import app.routes.websocket as websocket_module
from app.routes.websocket import ConnectionManager, Participant


def reset_manager_state():
    """Reset global connection manager state between tests."""
    websocket_module.manager.active_connections.clear()
    websocket_module.manager.participants.clear()
    websocket_module.manager.websocket_to_user.clear()


class TestConnectionManager:
    """Test ConnectionManager class."""

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting a WebSocket with participant registration."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()

        participant = await cm.connect(mock_websocket, "TEST1234", "user-123", "Test User")

        assert "TEST1234" in cm.active_connections
        assert mock_websocket in cm.active_connections["TEST1234"]
        assert mock_websocket.accept.called
        assert participant.user_id == "user-123"
        assert participant.display_name == "Test User"
        assert participant.color is not None

    @pytest.mark.asyncio
    async def test_connect_assigns_different_colors(self):
        """Test that different participants get different colors."""
        cm = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws2.accept = AsyncMock()

        p1 = await cm.connect(mock_ws1, "TEST1234", "user-1", "User 1")
        p2 = await cm.connect(mock_ws2, "TEST1234", "user-2", "User 2")

        assert p1.color != p2.color

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting a WebSocket."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        cm.active_connections["TEST1234"] = {mock_websocket}
        cm.participants["TEST1234"] = {
            "user-1": Participant(
                user_id="user-1",
                display_name="Test User",
                color="#FF6B6B",
                websocket=mock_websocket,
            )
        }
        cm.websocket_to_user[mock_websocket] = ("TEST1234", "user-1")

        disconnected = cm.disconnect(mock_websocket, "TEST1234")

        assert "TEST1234" not in cm.active_connections
        assert disconnected is not None
        assert disconnected.user_id == "user-1"

    @pytest.mark.asyncio
    async def test_disconnect_last_connection(self):
        """Test disconnecting the last connection removes session."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        cm.active_connections["TEST1234"] = {mock_websocket}

        cm.disconnect(mock_websocket, "TEST1234")

        assert "TEST1234" not in cm.active_connections

    @pytest.mark.asyncio
    async def test_get_participant(self):
        """Test getting participant by websocket."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()

        await cm.connect(mock_websocket, "TEST1234", "user-1", "Test User")

        participant = cm.get_participant(mock_websocket)
        assert participant is not None
        assert participant.user_id == "user-1"

    @pytest.mark.asyncio
    async def test_get_all_participants(self):
        """Test getting all participants in a session."""
        cm = ConnectionManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)
        mock_ws1.accept = AsyncMock()
        mock_ws2.accept = AsyncMock()

        await cm.connect(mock_ws1, "TEST1234", "user-1", "User 1")
        await cm.connect(mock_ws2, "TEST1234", "user-2", "User 2")

        participants = cm.get_all_participants("TEST1234")
        assert len(participants) == 2
        user_ids = {p["userId"] for p in participants}
        assert "user-1" in user_ids
        assert "user-2" in user_ids

    @pytest.mark.asyncio
    async def test_update_cursor(self):
        """Test updating participant cursor position."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()

        await cm.connect(mock_websocket, "TEST1234", "user-1", "Test User")
        cursor = {"lineNumber": 5, "column": 10}

        participant = cm.update_cursor(mock_websocket, cursor)

        assert participant is not None
        assert participant.cursor == cursor

    @pytest.mark.asyncio
    async def test_update_selection(self):
        """Test updating participant selection."""
        cm = ConnectionManager()
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()

        await cm.connect(mock_websocket, "TEST1234", "user-1", "Test User")
        selection = {
            "startLineNumber": 1,
            "startColumn": 1,
            "endLineNumber": 1,
            "endColumn": 10,
        }

        participant = cm.update_selection(mock_websocket, selection)

        assert participant is not None
        assert participant.selection == selection

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


def test_welcome_message_excludes_self(client, monkeypatch):
    """Ensure the welcome payload does not include the joining user."""
    reset_manager_state()

    class DummySession:
        code = "TEST1234"
        language = "python"

    async def fake_get_session_by_code(db, session_code):
        return DummySession()

    monkeypatch.setattr(
        websocket_module.SessionService,
        "get_session_by_code",
        AsyncMock(side_effect=fake_get_session_by_code),
    )

    class DummySessionCtx:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(websocket_module, "AsyncSessionLocal", lambda: DummySessionCtx())

    with client.websocket_connect("/ws/TEST1234") as ws1:
        ws1.send_json({"type": "join", "userId": "user-1", "displayName": "User 1"})
        welcome1 = ws1.receive_json()

        assert welcome1["participants"] == []

        with client.websocket_connect("/ws/TEST1234") as ws2:
            ws2.send_json({"type": "join", "userId": "user-2", "displayName": "User 2"})
            welcome2 = ws2.receive_json()

            participant_ids = {p["userId"] for p in welcome2["participants"]}
            assert participant_ids == {"user-1"}

            join_notice = ws1.receive_json()
            assert join_notice["type"] == "participant_join"
            assert join_notice["userId"] == "user-2"

    reset_manager_state()
