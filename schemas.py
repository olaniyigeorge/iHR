from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

# ---- Auth Schemas---

class AuthSignIn(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- User Schemas ---
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

# --- Job Schema ---
#  --- Enum for Job Levels ---
class JobRoleLevels(int, Enum):
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
    level: JobRoleLevels = Field(..., description="Difficulty level of the job (1 to 10).")
    industry_id: str = Field(..., description="The ID of the industry the job belongs to.")

# --- Update Schema ---
class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    level: Optional[JobRoleLevels]
    industry_id: Optional[str]

# --- Details Schema ---
class JobDetails(JobBase):
    id: int
    level: int
    industry_id: str

    model_config = ConfigDict(from_attributes=True)











# --- Interviews Schemas ---

class InterviewBase(BaseModel):
    hr_ai: str = "iHR AI"
    status: str

class InterviewCreate(InterviewBase):
    pass

class InterviewResponse(InterviewBase):
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    class Config:
        orm_mode = True



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
