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
DEFAULT_LANGUAGE = "python"

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

    def to_payload(self) -> Dict[str, Any]:
        """Return a serializable participant payload."""
        return {
            "userId": self.user_id,
            "displayName": self.display_name,
            "color": self.color,
            "cursor": self.cursor,
            "selection": self.selection,
        }


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

    def _ensure_session_state(self, session_code: str) -> None:
        """Ensure the session has connection and participant containers."""
        if session_code not in self.active_connections:
            self.active_connections[session_code] = set()
        if session_code not in self.participants:
            self.participants[session_code] = {}

    async def connect(
        self, websocket: WebSocket, session_code: str, user_id: str, display_name: str
    ) -> Participant:
        """Accept a WebSocket connection and register participant."""
        await websocket.accept()
        return self.register(websocket, session_code, user_id, display_name)

    def register(
        self, websocket: WebSocket, session_code: str, user_id: str, display_name: str
    ) -> Participant:
        """Register a participant on an already accepted WebSocket."""
        self._ensure_session_state(session_code)
        self.active_connections[session_code].add(websocket)

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
        return [participant.to_payload() for participant in self.participants[session_code].values()]

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


async def close_websocket(websocket: WebSocket, code: int, reason: str) -> None:
    """Close a websocket and ignore follow-up close failures."""
    try:
        await websocket.close(code=code, reason=reason)
    except Exception:
        pass


async def send_error(websocket: WebSocket, message: str) -> None:
    """Send a standard websocket error payload."""
    await websocket.send_json({"type": "error", "message": message})


async def get_session(session_code: str):
    """Load a session by code from the database."""
    async with AsyncSessionLocal() as db:
        return await SessionService.get_session_by_code(db, session_code)


def validate_join_message(join_message: Any) -> tuple[str, str]:
    """Validate the initial join payload and return participant identity."""
    if not isinstance(join_message, dict) or join_message.get("type") != "join":
        raise ValueError("First message must be a 'join' message with userId and displayName")

    user_id = join_message.get("userId", str(uuid.uuid4()))
    display_name = join_message.get("displayName", f"User {user_id[:4]}")
    return user_id, display_name


async def receive_join_message(websocket: WebSocket, session_code: str) -> tuple[str, str]:
    """Receive and validate the first join message from a client."""
    try:
        payload = await websocket.receive_text()
        join_message = json.loads(payload)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected before sending join message for session {session_code}")
        raise
    except json.JSONDecodeError as exc:
        logger.warning(f"Invalid join JSON for session {session_code}: {exc}")
        raise ValueError("Failed to receive join message") from exc
    except Exception as exc:
        logger.error(f"Error receiving join message: {exc}")
        raise ValueError("Failed to receive join message") from exc

    return validate_join_message(join_message)


async def register_participant(
    websocket: WebSocket, session_code: str, user_id: str, display_name: str
) -> tuple[Participant, list[Dict[str, Any]]]:
    """Register a participant and return their info plus existing peers."""
    existing_participants = manager.get_all_participants(session_code)
    participant = manager.register(websocket, session_code, user_id, display_name)
    return participant, existing_participants


async def send_welcome_message(
    websocket: WebSocket,
    participant: Participant,
    existing_participants: list[Dict[str, Any]],
    session_code: str,
) -> None:
    """Send the initial session snapshot to a newly joined participant."""
    session = await get_session(session_code)
    await websocket.send_json(
        {
            "type": "welcome",
            "userId": participant.user_id,
            "displayName": participant.display_name,
            "color": participant.color,
            "code": session.code if session else "",
            "language": session.language if session else DEFAULT_LANGUAGE,
            "participants": existing_participants,
        }
    )


async def broadcast_participant_join(session_code: str, participant: Participant) -> None:
    """Notify other clients that a participant joined."""
    await manager.broadcast(
        session_code,
        {
            "type": "participant_join",
            "userId": participant.user_id,
            "displayName": participant.display_name,
            "color": participant.color,
        },
        exclude=participant.websocket,
    )


async def broadcast_participant_leave(session_code: str, participant: Optional[Participant]) -> None:
    """Notify remaining clients that a participant left."""
    if not participant:
        return

    await manager.broadcast(
        session_code,
        {
            "type": "participant_leave",
            "userId": participant.user_id,
            "displayName": participant.display_name,
        },
    )


def validate_position(position: Any) -> None:
    """Validate a cursor position payload."""
    if not position:
        raise ValueError("cursor_position message must contain 'position' field")
    if not isinstance(position, dict):
        raise ValueError("position must be a dictionary")
    if not all(key in position for key in ["lineNumber", "column"]):
        raise ValueError("position must contain lineNumber and column")
    if not all(isinstance(position[key], int) and position[key] > 0 for key in ["lineNumber", "column"]):
        raise ValueError("lineNumber and column must be positive integers")


async def handle_code_change(session_code: str, message: dict, websocket: WebSocket) -> None:
    """Persist and broadcast a code change."""
    code = message.get("code")
    if code is None:
        raise ValueError("code_change message must contain 'code' field")

    try:
        async with AsyncSessionLocal() as db:
            await SessionService.update_session_code(db, session_code, code)
    except Exception as exc:
        logger.error(f"Error updating session code: {exc}")
        raise RuntimeError("Failed to update code in database") from exc

    await manager.broadcast(
        session_code,
        {
            "type": "code_update",
            "code": code,
            "language": message.get("language", DEFAULT_LANGUAGE),
        },
        exclude=websocket,
    )


async def handle_language_change(session_code: str, message: dict) -> None:
    """Persist and broadcast a language change."""
    language = message.get("language")
    if not language:
        raise ValueError("language_change message must contain 'language' field")

    try:
        async with AsyncSessionLocal() as db:
            await SessionService.update_session_language(db, session_code, language)
    except Exception as exc:
        logger.error(f"Error updating session language: {exc}")
        raise RuntimeError("Failed to update language in database") from exc

    await manager.broadcast(
        session_code,
        {
            "type": "language_update",
            "language": language,
        },
    )


async def handle_cursor_position(session_code: str, message: dict, websocket: WebSocket) -> None:
    """Update a participant cursor and broadcast it."""
    position = message.get("position")
    validate_position(position)

    updated_participant = manager.update_cursor(websocket, position)
    if not updated_participant:
        return

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


async def handle_selection_change(session_code: str, message: dict, websocket: WebSocket) -> None:
    """Update a participant selection and broadcast it."""
    selection = message.get("selection")
    if not selection:
        raise ValueError("selection_change message must contain 'selection' field")

    updated_participant = manager.update_selection(websocket, selection)
    if not updated_participant:
        return

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


async def process_message(session_code: str, websocket: WebSocket, message: Any) -> None:
    """Validate and process a single client websocket message."""
    if not isinstance(message, dict) or "type" not in message:
        logger.warning(f"Message missing 'type' field: {message}")
        raise ValueError("Message must contain a 'type' field")

    handlers = {
        "code_change": lambda: handle_code_change(session_code, message, websocket),
        "language_change": lambda: handle_language_change(session_code, message),
        "cursor_position": lambda: handle_cursor_position(session_code, message, websocket),
        "selection_change": lambda: handle_selection_change(session_code, message, websocket),
    }
    handler = handlers.get(message["type"])
    if not handler:
        logger.warning(f"Unknown message type: {message['type']}")
        raise ValueError(f"Unknown message type: {message['type']}")

    await handler()


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
    # Verify session exists
    if not await get_session(session_code):
        await close_websocket(websocket, code=1008, reason="Session not found")
        return

    # Accept connection but don't register participant yet - wait for join message
    await websocket.accept()

    try:
        try:
            user_id, display_name = await receive_join_message(websocket, session_code)
        except WebSocketDisconnect:
            return
        except ValueError as exc:
            await send_error(websocket, str(exc))
            await close_websocket(websocket, code=1008, reason=str(exc))
            return

        participant, existing_participants = await register_participant(
            websocket, session_code, user_id, display_name
        )
        await send_welcome_message(websocket, participant, existing_participants, session_code)
        await broadcast_participant_join(session_code, participant)

        while True:
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                raise
            except Exception as exc:
                logger.error(f"Error receiving WebSocket message: {exc}")
                break

            try:
                message = json.loads(data)
            except json.JSONDecodeError as exc:
                logger.warning(f"Invalid JSON received from client: {exc}")
                await send_error(websocket, "Invalid JSON format")
                continue

            try:
                await process_message(session_code, websocket, message)
            except ValueError as exc:
                await send_error(websocket, str(exc))
            except RuntimeError as exc:
                await send_error(websocket, str(exc))
            except Exception as exc:
                logger.error(f"Unexpected error processing message: {exc}", exc_info=True)
                await send_error(websocket, "An error occurred processing your message")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_code}")
        disconnected_participant = manager.disconnect(websocket, session_code)
        await broadcast_participant_leave(session_code, disconnected_participant)
    except Exception as exc:
        logger.error(f"Unexpected error in WebSocket handler: {exc}", exc_info=True)
        disconnected_participant = manager.disconnect(websocket, session_code)
        await broadcast_participant_leave(session_code, disconnected_participant)
        await close_websocket(websocket, code=1011, reason="Internal server error")
