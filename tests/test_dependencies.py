import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import async_db_session_dependency

@pytest.mark.asyncio
async def test_async_db_session_dependency():
    async for session in async_db_session_dependency:
        assert isinstance(session, AsyncSession)