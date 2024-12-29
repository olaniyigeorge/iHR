from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker
from decouple import config as decouple_config

# Asynchronous database setup
DATABASE_URL = decouple_config('DATABASE_URI', default="sqlite:///dev.db", cast=str) # "sqlite+aiosqlite:///db.sqlite3"
async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    autoflush=False, 
    expire_on_commit=False
)

# Synchronous database setup
sync_DATABASE_URL = decouple_config('DATABASE_URI', default="sqlite:///dev.db", cast=str) # "sqlite+aiosqlite:///db.sqlite3"
sync_DATABASE_URL = decouple_config('DATABASE_URI', default="sqlite:///./test.db")
sync_engine = create_engine(sync_DATABASE_URL, echo=True, future=True)
SessionLocal = sync_sessionmaker(
    bind=sync_engine, 
    autoflush=False, 
    expire_on_commit=False
)

# Base class for SQLAlchemy models
Base = declarative_base()

async def get_async_db_session():
    async with AsyncSessionLocal() as session:
        yield session

def get_db_session():
    with SessionLocal() as session:
        yield session