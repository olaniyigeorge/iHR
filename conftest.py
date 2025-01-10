import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from main import app
from services.database import Base, get_async_db_session

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create a new async engine for testing
test_engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Override the get_async_db_session dependency
async def override_get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_db_session] = override_get_async_db_session

@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()

@pytest.fixture(scope="function")
async def async_db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c