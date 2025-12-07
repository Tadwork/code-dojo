"""WebSocket routes for real-time collaboration."""

import json
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import AsyncSessionLocal
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)

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
            try:
                data = await websocket.receive_text()
            except Exception as e:
                logger.error(f"Error receiving WebSocket message: {e}")
                break

            try:
                message = json.loads(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON received from client: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })
                continue

            # Validate message has required 'type' field
            if not isinstance(message, dict) or "type" not in message:
                logger.warning(f"Message missing 'type' field: {message}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Message must contain a 'type' field",
                })
                continue

            message_type = message["type"]

            try:
                if message_type == "code_change":
                    # Validate required fields
                    if "code" not in message:
                        await websocket.send_json({
                            "type": "error",
                            "message": "code_change message must contain 'code' field",
                        })
                        continue

                    # Update code in database
                    try:
                        async with AsyncSessionLocal() as db:
                            await SessionService.update_session_code(
                                db,
                                session_code,
                                message["code"],
                            )
                    except Exception as e:
                        logger.error(f"Error updating session code: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to update code in database",
                        })
                        continue

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

                elif message_type == "language_change":
                    # Validate required fields
                    if "language" not in message:
                        await websocket.send_json({
                            "type": "error",
                            "message": "language_change message must contain 'language' field",
                        })
                        continue

                    # Update language in database
                    try:
                        async with AsyncSessionLocal() as db:
                            await SessionService.update_session_language(
                                db,
                                session_code,
                                message["language"],
                            )
                    except Exception as e:
                        logger.error(f"Error updating session language: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to update language in database",
                        })
                        continue

                    # Broadcast to all connections
                    await manager.broadcast(
                        session_code,
                        {
                            "type": "language_update",
                            "language": message["language"],
                        },
                    )

                elif message_type == "cursor_position":
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

                else:
                    # Unknown message type
                    logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    })

            except KeyError as e:
                logger.warning(f"Missing required field in message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Missing required field: {e}",
                })
            except Exception as e:
                logger.error(f"Unexpected error processing message: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "message": "An error occurred processing your message",
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_code}")
        manager.disconnect(websocket, session_code)
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket handler: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass
        manager.disconnect(websocket, session_code)

