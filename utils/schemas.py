from typing import Dict, List, Optional
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

class UserPublic(UserBase):
    id: int 
    role: Optional[str] 
    
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

class JobCreate(JobBase):
    level: int = Field(..., description="Difficulty level of the job (1 to 10).")
    industry_id: int = Field(..., description="The ID of the industry the job belongs to.")

class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    level: Optional[int]
    industry_id: Optional[int]

class JobDetails(JobBase):
    id: int
    level: int
    industry_id: int
    model_config = ConfigDict(from_attributes=True)

# --- STATEMENT SCHEMAS ---
class StatementBase(BaseModel):
    speaker: str
    content: str
    is_question: bool

class StatementCreate(StatementBase):
    interview_id: int
    replies_id: Optional[int] = None

class StatementResponse(StatementBase):
    id: int
    timestamp: datetime
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

class InterviewBase(BaseModel):
    hr_ai: str = "iHR AI"
    status: InterviewStatus

class InterviewCreate(InterviewBase):
    user_id: int
    job_id: int
    difficulty: InterviewDifficulty
    duration: Optional[timedelta] = timedelta(minutes=30)
    start_time: datetime

class InterviewResponse(InterviewBase):
    id: int
    user_id: int
    job_id: int
    difficulty: str
    duration: Optional[timedelta]
    start_time: datetime
    end_time: Optional[datetime]
    current_score: int
    insights: dict
    model_config = ConfigDict(from_attributes=True)

class InterviewUpdate(InterviewBase):
    status: Optional[str]
    difficulty: Optional[str]
    duration: Optional[timedelta]
    end_time: Optional[datetime]
    current_score: Optional[int]
    insights: Optional[dict]

class InterviewContext(InterviewBase):
    id: int
    user_id: int
    user: UserPublic
    job_id: int
    job: JobDetails
    difficulty: str
    duration: Optional[timedelta]
    start_time: datetime
    end_time: Optional[datetime]
    current_score: int
    insights: dict
    statements: List[StatementResponse]

# --- INDUSTRY SCHEMAS ---
class IndustryBase(BaseModel):
    name: str
    description: Optional[str] = None

class IndustryCreate(IndustryBase):
    pass

class IndustryResponse(IndustryBase):
    id: int
    created_at: datetime = datetime.utcnow()
    model_config = ConfigDict(from_attributes=True)

class IndustryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
