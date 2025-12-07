"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.main import app
from app.config import settings

# Test database engine
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

TestBase = declarative_base()


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }


@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

