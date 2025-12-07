"""Unit tests for Session model."""

from datetime import datetime
from app.models.session import Session


class TestSessionModel:
    """Test Session model."""

    def test_session_creation(self):
        """Test creating a session instance."""
        session = Session(
            session_code="TEST1234",
            title="Test Session",
            language="python",
            code="print('hello')",
        )
        
        assert session.session_code == "TEST1234"
        assert session.title == "Test Session"
        assert session.language == "python"
        assert session.code == "print('hello')"
        assert session.active_users == 0

    def test_session_defaults(self):
        """Test session default values."""
        session = Session(session_code="TEST1234")
        
        assert session.language == "python"
        assert session.code == ""
        assert session.active_users == 0
        assert session.title is None

    def test_session_repr(self):
        """Test session string representation."""
        session = Session(session_code="TEST1234")
        repr_str = repr(session)
        
        assert "TEST1234" in repr_str
        assert "Session" in repr_str

    def test_session_created_at(self):
        """Test session created_at timestamp."""
        session = Session(session_code="TEST1234")
        session.created_at = datetime.utcnow()
        
        assert session.created_at is not None
        assert isinstance(session.created_at, datetime)

