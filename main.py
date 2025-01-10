from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from services import hr_manager
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
import os
from decouple import config as decouple_config
import nltk
from utils.dependencies import async_db_session_dependency
from middleware import app_middleware 
from services.database import async_engine
from services.logger import logger
from config import config
from routers import auth, interviews, jobs, statements, industries, ws_interview, users
import uvicorn
import logging
import sys
from contextlib import asynccontextmanager
from services.database import database
import utils.models as models, utils.schemas as schemas, utils.crud as crud


@asynccontextmanager
async def lifeespan(app: FastAPI):
    await database.connect()
    yield 
    await database.disconnect()


app = FastAPI(title=config.PROJECT_NAME, docs_url="/api/docs")


# Register Routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(interviews.router)
app.include_router(ws_interview.router)
app.include_router(statements.router)
app.include_router(industries.router)

# Add Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=app_middleware)


# --- Basic Endpoints ---
@app.get("/", response_model=None)
async def home(db: AsyncSession = Depends(async_db_session_dependency)):
    base_url = decouple_config('DOMAIN', cast=str, default="http://localhost:8000")
    
    web_socket_links = [f"{base_url}/ws/{endpoint}" for endpoint in ["simulate-interview/{interview_id}"]]
    
    return {
        "name": "iHr",
        "details": "iHr home",
        "docs": f"{base_url}/api/docs",
        "web-socket endpoints": web_socket_links
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
