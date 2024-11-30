from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from database import SessionLocal #,  async_session
from sqlalchemy.ext.asyncio import AsyncSession


# Synchronous Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# # Asynchronous Dependency
# async def get_async_db():
#     async with async_session() as session:
#         yield session

# db_dependency = Annotated[AsyncSession, Depends(get_async_db)]