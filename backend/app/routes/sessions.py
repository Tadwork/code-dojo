"""Session API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class SessionCreate(BaseModel):
    """Session creation request."""

    title: str | None = None
    language: str = "python"

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "title": "Interview with John Doe",
                "language": "python"
            }
        }


class SessionResponse(BaseModel):
    """Session response model."""

    id: str
    session_code: str
    title: str | None
    language: str
    code: str
    created_at: str
    active_users: int

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_code": "ABC12345",
                "title": "Interview with John Doe",
                "language": "python",
                "code": "print('Hello, World!')",
                "created_at": "2024-01-15T10:30:00",
                "active_users": 2
            }
        }


@router.post(
    "",
    response_model=SessionResponse,
    status_code=200,
    summary="Create a new coding session",
    description="""
    Create a new coding interview session.
    
    This endpoint generates a unique 8-character session code that can be shared with candidates.
    The session will be initialized with the specified language and optional title.
    """,
    responses={
        200: {
            "description": "Session created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "session_code": "ABC12345",
                        "title": "Interview with John Doe",
                        "language": "python",
                        "code": "",
                        "created_at": "2024-01-15T10:30:00",
                        "active_users": 0
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
        }
    }
)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new coding session.
    
    - **title**: Optional title for the session (e.g., "Interview with John Doe")
    - **language**: Programming language for the session (default: "python")
    
    Returns a session object with a unique session_code that can be shared.
    """
    session = await SessionService.create_session(
        db,
        title=session_data.title,
        language=session_data.language,
    )
    return SessionResponse(
        id=str(session.id),
        session_code=session.session_code,
        title=session.title,
        language=session.language,
        code=session.code,
        created_at=session.created_at.isoformat(),
        active_users=session.active_users,
    )


@router.get(
    "/{session_code}",
    response_model=SessionResponse,
    summary="Get a session by code",
    description="""
    Retrieve a coding session by its unique session code.
    
    The session_code is case-insensitive and will be automatically converted to uppercase.
    """,
    responses={
        200: {
            "description": "Session found",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "session_code": "ABC12345",
                        "title": "Interview with John Doe",
                        "language": "python",
                        "code": "print('Hello, World!')",
                        "created_at": "2024-01-15T10:30:00",
                        "active_users": 2
                    }
                }
            }
        },
        404: {
            "description": "Session not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Session not found"
                    }
                }
            }
        }
    }
)
async def get_session(
    session_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a session by code.
    
    - **session_code**: The unique 8-character session code (case-insensitive)
    
    Returns the session details including current code, language, and active user count.
    """
    session = await SessionService.get_session_by_code(db, session_code.upper())
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=str(session.id),
        session_code=session.session_code,
        title=session.title,
        language=session.language,
        code=session.code,
        created_at=session.created_at.isoformat(),
        active_users=session.active_users,
    )

