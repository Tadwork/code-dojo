"""WebSocket routes for real-time collaboration."""

import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import AsyncSessionLocal
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Color palette for participants
PARTICIPANT_COLORS = [
    "#FF6B6B",  # Red
    "#4ECDC4",  # Teal
    "#45B7D1",  # Sky Blue
    "#96CEB4",  # Sage Green
    "#FFEAA7",  # Yellow
    "#DDA0DD",  # Plum
    "#98D8C8",  # Mint
    "#F7DC6F",  # Gold
    "#BB8FCE",  # Purple
    "#85C1E9",  # Light Blue
]


@dataclass
class Participant:
    """Represents a participant in a session."""

    user_id: str
    display_name: str
    color: str
    websocket: WebSocket
    cursor: Optional[Dict[str, int]] = None
    selection: Optional[Dict[str, Any]] = None


# Store active WebSocket connections per session
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.participants: Dict[
            str, Dict[str, Participant]
        ] = {}  # session_code -> user_id -> Participant
        self.websocket_to_user: Dict[
            WebSocket, tuple[str, str]
        ] = {}  # websocket -> (session_code, user_id)

    def _get_next_color(self, session_code: str) -> str:
        """Get the next available color for a session."""
        used_colors = set()
        if session_code in self.participants:
            used_colors = {p.color for p in self.participants[session_code].values()}
        for color in PARTICIPANT_COLORS:
            if color not in used_colors:
                return color
        # If all colors used, cycle through
        return PARTICIPANT_COLORS[
            len(self.participants.get(session_code, {})) % len(PARTICIPANT_COLORS)
        ]

    async def connect(
        self, websocket: WebSocket, session_code: str, user_id: str, display_name: str
    ) -> Participant:
        """Accept a WebSocket connection and register participant."""
        await websocket.accept()
        if session_code not in self.active_connections:
            self.active_connections[session_code] = set()
        self.active_connections[session_code].add(websocket)

        # Create participant
        if session_code not in self.participants:
            self.participants[session_code] = {}

        color = self._get_next_color(session_code)
        participant = Participant(
            user_id=user_id,
            display_name=display_name,
            color=color,
            websocket=websocket,
        )
        self.participants[session_code][user_id] = participant
        self.websocket_to_user[websocket] = (session_code, user_id)

        return participant

    def disconnect(self, websocket: WebSocket, session_code: str) -> Optional[Participant]:
        """Remove a WebSocket connection and return the participant info."""
        participant = None

        # Get participant info before removing
        if websocket in self.websocket_to_user:
            _, user_id = self.websocket_to_user[websocket]
            if session_code in self.participants and user_id in self.participants[session_code]:
                participant = self.participants[session_code].pop(user_id)
            del self.websocket_to_user[websocket]

            # Clean up empty sessions
            if session_code in self.participants and not self.participants[session_code]:
                del self.participants[session_code]

        if session_code in self.active_connections:
            self.active_connections[session_code].discard(websocket)
            if not self.active_connections[session_code]:
                del self.active_connections[session_code]

        return participant

    def get_participant(self, websocket: WebSocket) -> Optional[Participant]:
        """Get the participant associated with a websocket."""
        if websocket in self.websocket_to_user:
            session_code, user_id = self.websocket_to_user[websocket]
            return self.participants.get(session_code, {}).get(user_id)
        return None

    def get_all_participants(self, session_code: str) -> list[Dict[str, Any]]:
        """Get all participants in a session as serializable dicts."""
        if session_code not in self.participants:
            return []
        return [
            {
                "userId": p.user_id,
                "displayName": p.display_name,
                "color": p.color,
                "cursor": p.cursor,
                "selection": p.selection,
            }
            for p in self.participants[session_code].values()
        ]

    def update_cursor(self, websocket: WebSocket, cursor: Dict[str, int]) -> Optional[Participant]:
        """Update a participant's cursor position."""
        participant = self.get_participant(websocket)
        if participant:
            participant.cursor = cursor
        return participant

    def update_selection(
        self, websocket: WebSocket, selection: Dict[str, Any]
    ) -> Optional[Participant]:
        """Update a participant's selection."""
        participant = self.get_participant(websocket)
        if participant:
            participant.selection = selection
        return participant

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
    """
    WebSocket endpoint for real-time collaboration.

    Connect to this endpoint using a WebSocket client. The session_code must be a valid existing session.

    **Connection Protocol:**
    1. Connect to the WebSocket endpoint
    2. First message MUST be a `join` message with userId and displayName
    3. Server responds with `welcome` message containing participant info and existing participants

    **Message Types:**

    **Client to Server:**
    - `join`: Register as a participant (REQUIRED as first message)
      ```json
      {"type": "join", "userId": "uuid-here", "displayName": "User 1"}
      ```
    - `code_change`: Update the code in the session
      ```json
      {"type": "code_change", "code": "print('Hello, World!')", "language": "python"}
      ```
    - `language_change`: Change the programming language
      ```json
      {"type": "language_change", "language": "javascript"}
      ```
    - `cursor_position`: Update cursor position
      ```json
      {"type": "cursor_position", "position": {"lineNumber": 5, "column": 10}}
      ```
    - `selection_change`: Update text selection
      ```json
      {"type": "selection_change", "selection": {"startLineNumber": 1, "startColumn": 1, "endLineNumber": 1, "endColumn": 10}}
      ```

    **Server to Client:**
    - `welcome`: Sent after successful join with assigned color and participant list
    - `participant_join`: Broadcast when a new participant joins
    - `participant_leave`: Broadcast when a participant disconnects
    - `code_update`: Broadcast code changes to all connected clients
    - `language_update`: Broadcast language changes
    - `cursor_update`: Broadcast cursor position updates
    - `selection_update`: Broadcast selection updates
    - `error`: Error message with details

    **Error Handling:**
    The server will send error messages for invalid JSON, missing fields, unknown message types, or database failures.

    **Disconnection:**
    The connection will be closed if the session doesn't exist (code 1008), an internal error occurs (code 1011), or the client disconnects normally.

    - **session_code**: The unique 8-character session code (case-insensitive)
    """
    session_code = session_code.upper()
    participant = None

    # Verify session exists
    async with AsyncSessionLocal() as db:
        session = await SessionService.get_session_by_code(db, session_code)
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            return

    # Accept connection but don't register participant yet - wait for join message
    await websocket.accept()

    try:
        # Wait for join message first
        try:
            data = await websocket.receive_text()
            join_message = json.loads(data)
        except WebSocketDisconnect:
            logger.info(
                f"Client disconnected before sending join message for session {session_code}"
            )
            return
        except Exception as e:
            logger.error(f"Error receiving join message: {e}")
            try:
                await websocket.close(code=1008, reason="Failed to receive join message")
            except Exception:
                pass
            return

        if not isinstance(join_message, dict) or join_message.get("type") != "join":
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "First message must be a 'join' message with userId and displayName",
                }
            )
            await websocket.close(code=1008, reason="Invalid join message")
            return

        user_id = join_message.get("userId", str(uuid.uuid4()))
        display_name = join_message.get("displayName", f"User {user_id[:4]}")

        # Register participant (without calling accept again)
        if session_code not in manager.active_connections:
            manager.active_connections[session_code] = set()
        manager.active_connections[session_code].add(websocket)

        # Capture current participants before adding the new one so welcome payload excludes self
        existing_participants = manager.get_all_participants(session_code)

        if session_code not in manager.participants:
            manager.participants[session_code] = {}

        color = manager._get_next_color(session_code)
        participant = Participant(
            user_id=user_id,
            display_name=display_name,
            color=color,
            websocket=websocket,
        )
        manager.participants[session_code][user_id] = participant
        manager.websocket_to_user[websocket] = (session_code, user_id)

        # Get current session state
        async with AsyncSessionLocal() as db:
            session = await SessionService.get_session_by_code(db, session_code)

        # Send welcome message with participant info
        await websocket.send_json(
            {
                "type": "welcome",
                "userId": user_id,
                "displayName": display_name,
                "color": color,
                "code": session.code if session else "",
                "language": session.language if session else "python",
                "participants": existing_participants,
            }
        )

        # Broadcast participant join to others
        await manager.broadcast(
            session_code,
            {
                "type": "participant_join",
                "userId": user_id,
                "displayName": display_name,
                "color": color,
            },
            exclude=websocket,
        )

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
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                    }
                )
                continue

            # Validate message has required 'type' field
            if not isinstance(message, dict) or "type" not in message:
                logger.warning(f"Message missing 'type' field: {message}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Message must contain a 'type' field",
                    }
                )
                continue

            message_type = message["type"]

            try:
                if message_type == "code_change":
                    # Validate required fields
                    if "code" not in message:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "code_change message must contain 'code' field",
                            }
                        )
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
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "Failed to update code in database",
                            }
                        )
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
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "language_change message must contain 'language' field",
                            }
                        )
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
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "Failed to update language in database",
                            }
                        )
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
                    # Update and broadcast cursor position
                    position = message.get("position")
                    if not position:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "cursor_position message must contain 'position' field",
                            }
                        )
                        continue

                    updated_participant = manager.update_cursor(websocket, position)
                    if updated_participant:
                        await manager.broadcast(
                            session_code,
                            {
                                "type": "cursor_update",
                                "userId": updated_participant.user_id,
                                "displayName": updated_participant.display_name,
                                "color": updated_participant.color,
                                "position": position,
                            },
                            exclude=websocket,
                        )

                elif message_type == "selection_change":
                    # Update and broadcast selection
                    selection = message.get("selection")
                    if not selection:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "selection_change message must contain 'selection' field",
                            }
                        )
                        continue

                    updated_participant = manager.update_selection(websocket, selection)
                    if updated_participant:
                        await manager.broadcast(
                            session_code,
                            {
                                "type": "selection_update",
                                "userId": updated_participant.user_id,
                                "displayName": updated_participant.display_name,
                                "color": updated_participant.color,
                                "selection": selection,
                            },
                            exclude=websocket,
                        )

                else:
                    # Unknown message type
                    logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )

            except KeyError as e:
                logger.warning(f"Missing required field in message: {e}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": f"Missing required field: {e}",
                    }
                )
            except Exception as e:
                logger.error(f"Unexpected error processing message: {e}", exc_info=True)
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "An error occurred processing your message",
                    }
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_code}")
        disconnected_participant = manager.disconnect(websocket, session_code)
        if disconnected_participant:
            await manager.broadcast(
                session_code,
                {
                    "type": "participant_leave",
                    "userId": disconnected_participant.user_id,
                    "displayName": disconnected_participant.display_name,
                },
            )
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket handler: {e}", exc_info=True)
        disconnected_participant = manager.disconnect(websocket, session_code)
        if disconnected_participant:
            await manager.broadcast(
                session_code,
                {
                    "type": "participant_leave",
                    "userId": disconnected_participant.user_id,
                    "displayName": disconnected_participant.display_name,
                },
            )
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass
