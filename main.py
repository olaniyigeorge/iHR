from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException
import models, schemas, crud
from sqlalchemy.orm import Session
from services import hr_manager
from services.database import SessionLocal, engine
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
import os
from decouple import config as decouple_config
import nltk
nltk.download('punkt_tab')


import app_routers.auth as auth
from dependencies import db_dependency
from app_routers.auth import get_current_user
from middleware import app_middleware 
from services.logger import logger
from app_routers import interviews, interviews, jobs, statements, industries, ws_interview




app = FastAPI()

# Register Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(interviews.router)
app.include_router(ws_interview.router)
app.include_router(statements.router)
app.include_router(industries.router)
# Add Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=app_middleware)

models.Base.metadata.create_all(bind=engine)

user_dependency = Annotated[dict, Depends(get_current_user)]

# --- Basic Endpoints ---
@app.get("/")
async def home():
    base_url = decouple_config('DOMAIN', cast=str , default="http://localhost:8000")
    
    web_socket_links = [f"{base_url}/ws/{endpoint}" for endpoint in ["simulate-interview/{interview_id}"]]
    
    # w = "my name is Abeleje Olaniyi George. I am a software developer"
    # response = nltk.word_tokenize(w)
    # print(response)
    content = "I am a web dev"
    interview_ctx = {
        "user_id": 1,
        "id": 1
    }

    st = await hr_manager.create_statement(
        statement_body=content, 
        speaker=f"USER-{interview_ctx["user_id"]}", 
        interview_id=interview_ctx["id"], 
        replies_id=0,
        db=db_dependency
    )

    print("STATMENT: ", st)


    return {
        "name": "iHr",
        "details": "iHr home",
        "docs": f"{base_url}/docs",
        "web-socket endpoints": web_socket_links
    }
    

#  ---- User CRUD ------
@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: db_dependency):
    db_user = crud.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return db_user

@app.get("/users/", response_model=list[schemas.UserDetail])
def list_user(db: db_dependency):
    users = crud.get_users(db)
    if not users:
        raise HTTPException(status_code=400, detail="Error getting users")
    return [schemas.UserDetail.model_validate(user) for user in users]

@app.get("/users/{user_id}", response_model=schemas.UserDetail)
def get_user(user_id: int, db: db_dependency):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Convert ORM object to Pydantic model
    return schemas.UserDetail.model_validate(user)

@app.get("/user/me")
async def home(user: user_dependency, db:  db_dependency):
    if user is None:
        raise HTTPException({"name": ""}, status_code=403, detail="Authentication Failed")
    return {"User": user}
    
