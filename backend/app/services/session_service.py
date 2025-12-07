"""Session management service."""

import secrets
import string
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.session import Session


class SessionService:
    """Service for managing coding sessions."""

    @staticmethod
    def generate_session_code() -> str:
        """Generate a unique 8-character session code."""
        alphabet = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(8))

    @staticmethod
    async def create_session(
        db: AsyncSession,
        title: Optional[str] = None,
        language: str = "python",
    ) -> Session:
        """Create a new coding session."""
        session_code = SessionService.generate_session_code()

        # Ensure uniqueness
        while await SessionService.get_session_by_code(db, session_code):
            session_code = SessionService.generate_session_code()

        session = Session(
            session_code=session_code,
            title=title,
            language=language,
            code="",
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return session

    @staticmethod
    async def get_session_by_code(
        db: AsyncSession,
        session_code: str,
    ) -> Optional[Session]:
        """Get a session by its code."""
        result = await db.execute(select(Session).where(Session.session_code == session_code))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_session_code(
        db: AsyncSession,
        session_code: str,
        code: str,
    ) -> Optional[Session]:
        """Update the code in a session."""
        session = await SessionService.get_session_by_code(db, session_code)
        if session:
            session.code = code
            await db.commit()
            await db.refresh(session)
        return session

    @staticmethod
    async def update_session_language(
        db: AsyncSession,
        session_code: str,
        language: str,
    ) -> Optional[Session]:
        """Update the language in a session."""
        session = await SessionService.get_session_by_code(db, session_code)
        if session:
            session.language = language
            await db.commit()
            await db.refresh(session)
        return session
