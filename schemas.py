from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict, Field
import enum 

# ---- AUTH SCHEMAS ---
class AuthSignIn(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str



# ---  USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserDetail(UserBase):
    id: int 
    password: str
    role: Optional[str] 

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)



# --- JOB SCHEMAS ---
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

class JobBase(BaseModel):
    title: str
    description: Optional[str] = Field(None, description="A brief description of the job role.")
    requirements: Optional[str] = Field(None, description="The qualifications or requirements for the job.")

# --- Create Schema ---
class JobCreate(JobBase):
    level: int = Field(..., description="Difficulty level of the job (1 to 10).") # JobRoleLevels = Field(..., description="Difficulty level of the job (1 to 10).")
    industry_id: str = Field(..., description="The ID of the industry the job belongs to.")

# --- Update Schema ---
class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    level: Optional[int]
    industry_id: Optional[str]

# --- Details Schema ---
class JobDetails(JobBase):
    id: int
    level: int
    industry_id: str

    model_config = ConfigDict(from_attributes=True)



# --- INTERVIEWS SCHEMAS ---
class InterviewDifficulty(enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class InterviewStatus(enum.Enum):
    SCHEDULED = "Scheduled"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

# Base schema for interviews, common fields
class InterviewBase(BaseModel):
    hr_ai: str = "iHR AI"
    status: InterviewStatus

# Schema for creating an interview
class InterviewCreate(InterviewBase):
    user_id: int
    job_id: int
    difficulty: InterviewDifficulty
    duration: Optional[timedelta] = timedelta(minutes=30)
    start_time: datetime

# Schema for responding with interview details
class InterviewResponse(InterviewBase):
    id: int
    user_id: int
    job_id: int
    difficulty: str  # InterviewDifficulty
    duration: Optional[timedelta]
    start_time: datetime
    end_time: Optional[datetime]
    current_score: int
    insights: dict  # {"strengths": [], "weaknesses": []}

    model_config = ConfigDict(from_attributes=True)

# Schema for updating an interview
class InterviewUpdate(InterviewBase):
    status: Optional[str]   # Optional[InterviewStatus]
    difficulty: Optional[str]   # Optional[InterviewDifficulty]
    duration: Optional[timedelta]
    end_time: Optional[datetime]
    current_score: Optional[int]
    insights: Optional[dict]  # {"strengths": [], "weaknesses": []}






# --- STATEMENT SCHEMAS ---
class StatementBase(BaseModel):
    speaker: str
    content: str
    is_question: bool

class StatementCreate(StatementBase):
    interview_id: str
    replies_to_id: Optional[str] = None

class StatementResponse(StatementBase):
    id: str
    timestamp: datetime
    class Config:
        orm_mode = True
