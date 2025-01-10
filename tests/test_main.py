import pytest
from sqlalchemy.ext.asyncio import AsyncSession


from utils import crud, schemas
from utils.models import User

@pytest.mark.asyncio
async def test_create_user(async_db_session: AsyncSession):
    user = schemas.UserCreate(username="testuser", email="test@example.com", password="password")
    db_user = await crud.create_user(async_db_session, user)
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"