from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from services.database import get_async_db_session, get_db_session # SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

# from services.database import sessionmanager

db_session_dependency = Annotated[Session, Depends(get_db_session)]

async_db_session_dependency = Annotated[AsyncSession, Depends(get_async_db_session)]
