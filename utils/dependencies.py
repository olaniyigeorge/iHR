from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import database



db_session_dependency = Annotated[Session, Depends(database)]
async_db_session_dependency = Annotated[AsyncSession, Depends(database)]



