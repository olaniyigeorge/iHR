from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from decouple import config as decouple_config


ENVT = decouple_config('ENVT', default="dev", cast=str)

if ENVT == "prod":
    DATABASE_URL = decouple_config('DATABASE_URL', default="sqlite:///db.sqlite3", cast=str) # "sqlite+aiosqlite:///db.sqlite3"
else:
    DATABASE_URL = "sqlite:///db.sqlite3"

print("ENVT", ENVT)
print(DATABASE_URL)  


# Create Synchronous Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Synchronous Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# # Create Async Engine
# async_engine = create_async_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
#     echo=True,
#     future=True
# )

# # Async Session Factory
# async_session = sessionmaker(
#     engine, expire_on_commit=False, class_=AsyncSession
# )



# Base class for SQLAlchemy models
Base = declarative_base()











