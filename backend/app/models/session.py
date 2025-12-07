"""Session model for coding interview sessions."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Session(Base):
    """Coding interview session model."""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_code = Column(String(8), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=True)
    language = Column(String(50), default="python", server_default="python")
    code = Column(Text, default="", server_default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    active_users = Column(Integer, default=0, server_default="0")

    def __init__(self, **kwargs):
        """Initialize Session with defaults."""
        # Set defaults if not provided
        if "language" not in kwargs:
            kwargs["language"] = "python"
        if "code" not in kwargs:
            kwargs["code"] = ""
        if "active_users" not in kwargs:
            kwargs["active_users"] = 0
        if "created_at" not in kwargs:
            kwargs["created_at"] = datetime.utcnow()
        if "updated_at" not in kwargs:
            kwargs["updated_at"] = datetime.utcnow()
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Session {self.session_code}>"

