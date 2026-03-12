"""Session model for coding interview sessions."""

import uuid
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Session(Base):
    """Coding interview session model."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(50), default="python", server_default="python")
    code: Mapped[str] = mapped_column(Text, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    active_users: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    def __init__(self, **kwargs: object) -> None:
        """Apply Python-side defaults so fresh instances match persisted behavior."""
        kwargs.setdefault("language", "python")
        kwargs.setdefault("code", "")
        kwargs.setdefault("active_users", 0)
        kwargs.setdefault("created_at", datetime.utcnow())
        kwargs.setdefault("updated_at", datetime.utcnow())
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Session {self.session_code}>"
