import pytest
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from services.database import metadata, database

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="module")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="module")
async def async_db_session(async_engine):
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_database_connection(async_db_session: AsyncSession):
    result = await async_db_session.execute(sqlalchemy.text("SELECT 1"))
    assert result.scalar() == 1