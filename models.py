from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Interval, Enum, Boolean
from sqlalchemy.orm import relationship, Mapped
from database import Base
from datetime import datetime, timezone
import enum

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Store hashed password
    interviews = relationship("Interview", back_populates="user")


class InterviewStatus(enum.Enum):
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hr_ai = Column(String, default="iHR AI")
    duration = Column(Interval, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.ONGOING)

    user = relationship("User", back_populates="interviews")
    statements = relationship("Statement", back_populates="interview")





class Statement(Base):
    __tablename__ = "statements"
    id = Column(String, primary_key=True, index=True)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    speaker = Column(String, nullable=False)  # "USER" or "AI"
    content = Column(String, nullable=False)
    replies_to_id = Column(String, ForeignKey("statements.id"), nullable=True)
    is_question = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    interview = relationship("Interview", back_populates="statements")
    replies = relationship("Statement", remote_side=[id])
