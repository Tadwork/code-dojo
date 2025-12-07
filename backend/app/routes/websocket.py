"""WebSocket routes for real-time collaboration."""

import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import AsyncSessionLocal
from app.services.session_service import SessionService

router = APIRouter()

# Store active WebSocket connections per session
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_code: str):
        """Accept a WebSocket connection."""
        await websocket.accept()
        if session_code not in self.active_connections:
            self.active_connections[session_code] = set()
        self.active_connections[session_code].add(websocket)

    def disconnect(self, websocket: WebSocket, session_code: str):
        """Remove a WebSocket connection."""
        if session_code in self.active_connections:
            self.active_connections[session_code].discard(websocket)
            if not self.active_connections[session_code]:
                del self.active_connections[session_code]

    async def broadcast(self, session_code: str, message: dict, exclude: WebSocket = None):
        """Broadcast a message to all connections in a session."""
        if session_code in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[session_code]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception:
                        disconnected.add(connection)

            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn, session_code)


manager = ConnectionManager()


@router.websocket("/ws/{session_code}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_code: str,
):
    """WebSocket endpoint for real-time collaboration."""
    session_code = session_code.upper()

    # Verify session exists
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        session = await SessionService.get_session_by_code(db, session_code)
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return

    await manager.connect(websocket, session_code)

    try:
        # Send current code to the new connection
        async with AsyncSessionLocal() as db:
            session = await SessionService.get_session_by_code(db, session_code)
            if session:
                await websocket.send_json({
                    "type": "code_update",
                    "code": session.code,
                    "language": session.language,
                })

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "code_change":
                # Update code in database
                async with AsyncSessionLocal() as db:
                    await SessionService.update_session_code(
                        db,
                        session_code,
                        message["code"],
                    )

                # Broadcast to all other connections
                await manager.broadcast(
                    session_code,
                    {
                        "type": "code_update",
                        "code": message["code"],
                        "language": message.get("language", "python"),
                    },
                    exclude=websocket,
                )

            elif message["type"] == "language_change":
                # Update language in database
                async with AsyncSessionLocal() as db:
                    await SessionService.update_session_language(
                        db,
                        session_code,
                        message["language"],
                    )

                # Broadcast to all connections
                await manager.broadcast(
                    session_code,
                    {
                        "type": "language_update",
                        "language": message["language"],
                    },
                )

            elif message["type"] == "cursor_position":
                # Broadcast cursor position (for future multi-cursor support)
                await manager.broadcast(
                    session_code,
                    {
                        "type": "cursor_update",
                        "userId": message.get("userId", "unknown"),
                        "position": message.get("position"),
                    },
                    exclude=websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_code)

