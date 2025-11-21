import os
import sys
import pytest
import pytest_asyncio
import tempfile
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

from src.database import get_session


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a temporary SQLite database for testing"""
    # Create a temporary file for the test database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    
    # Create async engine for SQLite
    test_engine = create_async_engine(
        f"sqlite+aiosqlite:///{temp_db.name}",
        echo=False
    )
    
    # Create session maker
    test_async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield test_async_session
    
    # Cleanup: close engine and remove temp file
    await test_engine.dispose()
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)


@pytest_asyncio.fixture
async def test_session(test_db):
    """Create a test session"""
    async with test_db() as session:
        yield session


@pytest_asyncio.fixture
async def test_app(test_db):
    """Create a test FastAPI app with test database"""
    
    async def get_test_session():
        async with test_db() as session:
            yield session
    
    # Override the dependency
    app.dependency_overrides[get_session] = get_test_session
    
    yield app
    
    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_app):
    """Create an async HTTP client for testing"""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), 
        base_url="http://test"
    ) as ac:
        yield ac
