from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ConfigDict

# ---- AuthModels ---

class AuthSignIn(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


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
