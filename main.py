from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException
import models, schemas, crud
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from services import hr_manager
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
import os
from decouple import config as decouple_config
import nltk
import app_routers.auth as auth
from dependencies import async_db_session_dependency
from app_routers.auth import get_current_user
from middleware import app_middleware 
from services.database import get_async_db_session
from services.logger import logger
from app_routers import interviews, jobs, statements, industries, ws_interview
import uvicorn
import logging
import sys
from contextlib import asynccontextmanager
from settings import settings

# Database setup
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"
# engine = create_async_engine(DATABASE_URL, echo=True)
# async_session = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

app = FastAPI(title=settings.project_name, docs_url="/api/docs")

# Register Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(interviews.router)
app.include_router(ws_interview.router)
app.include_router(statements.router)
app.include_router(industries.router)

# Add Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=app_middleware)

# Create all tables
@app.on_event("startup")
async def on_startup():
    async with get_async_db_session as conn:
        await conn.run_sync(models.Base.metadata.create_all)

user_dependency = Annotated[dict, Depends(get_current_user)]

# --- Basic Endpoints ---
@app.get("/")
async def home(db: AsyncSession = Depends(async_db_session_dependency), args: str = None, kwargs: str = None):
    base_url = decouple_config('DOMAIN', cast=str, default="http://localhost:8000")
    
    web_socket_links = [f"{base_url}/ws/{endpoint}" for endpoint in ["simulate-interview/{interview_id}"]]
    
    content = "I am a web dev"
    interview_ctx = {
        "user_id": 1,
        "id": 1
    }

    # print("\ncreating statement \n ")
    # st = await hr_manager.create_statement(
    #     statement_body=content, 
    #     speaker=f"USER-{interview_ctx['user_id']}", 
    #     interview_id=interview_ctx["id"], 
    #     replies_id=0,
    #     db=db
    # )

    # print("ST: ", st)

    return {
        "name": "iHr",
        "details": "iHr home",
        "docs": f"{base_url}/docs",
        "web-socket endpoints": web_socket_links
    }

#  ---- User CRUD ------
@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(async_db_session_dependency)):
    db_user = await crud.create_user(db, user)
    if not db_user:
 
        raise HTTPException(status_code=400, detail="User already exists")
    return db_user

@app.get("/users/", response_model=list[schemas.UserDetail])
async def list_user(db: AsyncSession = Depends(async_db_session_dependency)):
    users = await crud.get_users(db)
    if not users:
        raise HTTPException(status_code=400, detail="Error getting users")
    return [schemas.UserDetail.model_validate(user) for user in users]

@app.get("/users/{user_id}", response_model=schemas.UserDetail)
async def get_user(user_id: int, db: AsyncSession = Depends(async_db_session_dependency)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserDetail.model_validate(user)

@app.get("/user/me")
async def get_current_user_info(user: user_dependency, db: AsyncSession = Depends(async_db_session_dependency)):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication Failed")
    return {"User": user}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)


# main