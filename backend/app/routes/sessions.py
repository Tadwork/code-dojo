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


@router.post("", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new coding session."""
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


@router.get("/{session_code}", response_model=SessionResponse)
async def get_session(
    session_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a session by code."""
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

