from sqlalchemy import (
    Column, String, Integer, ForeignKey, DateTime, Interval, Enum, Boolean, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import enum

Base = declarative_base()

# Enum for User Roles
class UserRoles(enum.Enum):
    ADMIN = "Admin"
    USER = "User"

# Enum for Interview Status
class InterviewStatus(enum.Enum):
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# Enum for Interview Difficulty
class InterviewDifficulty(enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

# Enum for Job Role Levels (Difficulty)
class JobRoleLevels(enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10

#  --- User Model ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRoles), default=UserRoles.USER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    interviews = relationship("Interview", back_populates="user")

# --- Industry Model ---
class Industry(Base):
    __tablename__ = "industries"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    jobs = relationship("Job", back_populates="industry")

# --- Job Model ---
class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    level = Column(Enum(JobRoleLevels), nullable=False)
    industry_id = Column(String, ForeignKey("industries.id"), nullable=False)

    industry = relationship("Industry", back_populates="jobs")
    interviews = relationship("Interview", back_populates="job")

# --- Interview Model ---
class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, index=True)
    hr_ai = Column(String, default="iHR AI")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    difficulty = Column(Enum(InterviewDifficulty), default=InterviewDifficulty.BEGINNER)
    duration = Column(Interval, nullable=True, default=timedelta(minutes=30))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.ONGOING)

    user = relationship("User", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    statements = relationship("Statement", back_populates="interview")

# ---- Statement Model ---
class Statement(Base):
    __tablename__ = "statements"
    id = Column(String, primary_key=True, index=True)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    speaker = Column(String, nullable=False)  # "USER" or "AI"
    content = Column(Text, nullable=False)
    replies_to_id = Column(String, ForeignKey("statements.id"), nullable=True)
    is_question = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview", back_populates="statements")
    replies = relationship("Statement", remote_side=[id])
