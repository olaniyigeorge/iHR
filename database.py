from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import os



if os.getenv("ENVT") == "prod": 
    DATABASE_URL = os.getenv("postgres_db_url")  
else:
    DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"

# Create Synchronous Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create Async Engine
async_engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=True,
    future=True
)


# Synchronous Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Session Factory
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)



# Base class for SQLAlchemy models
Base = declarative_base()











