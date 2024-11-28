from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException
import models, schemas, crud
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

import auth
from utils import get_db
from auth import get_current_user
from middleware import app_middleware 
from logger import logger

app = FastAPI()
app.include_router(auth.router)
app.add_middleware(BaseHTTPMiddleware, dispatch=app_middleware)

models.Base.metadata.create_all(bind=engine)

user_dependency = Annotated[dict, Depends(get_current_user)]


# --- Basic Endpoints ---
@app.get("/")
def home():    
    return {
            "name": "iHr",
            "details": "iHr home " 
        }
    

#  ---- User CRUD ------
@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return db_user

@app.get("/users/", response_model=list[schemas.UserDetail])
def list_user(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    if not users:
        raise HTTPException(status_code=400, detail="Error getting users")
    return [schemas.UserDetail.model_validate(user) for user in users]

@app.get("/users/{user_id}", response_model=schemas.UserDetail)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Convert ORM object to Pydantic model
    return schemas.UserDetail.model_validate(user)

@app.get("/user/me")
async def home(user: user_dependency, db:  Session = Depends(get_db)):
    if user is None:
        raise HTTPException({"name": ""}, status_code=403, detail="Authentication Failed")
    return {"User": user}
    


# --- Interviews ---

@app.post("/interviews/", response_model=schemas.InterviewResponse)
def create_interview(interview: schemas.InterviewCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_interview(db, user_id, interview)

@app.post("/statements/", response_model=schemas.StatementResponse)
def create_statement(statement: schemas.StatementCreate, db: Session = Depends(get_db)):
    return crud.create_statement(db, statement)