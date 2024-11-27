from typing import Union
from fastapi import Depends, FastAPI, HTTPException
import models, schemas, crud
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import auth
from utils import get_db
from starlette import status

app = FastAPI()
app.include_router(auth.router)



models.Base.metadata.create_all(bind=engine)


# --- Basic Endpoints ---
@app.get("/")
def read_root():
    return {
            "Name": "iHr",
            "Description": "",
            "docs": "/docs"
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



# --- Interviews ---

@app.post("/interviews/", response_model=schemas.InterviewResponse)
def create_interview(interview: schemas.InterviewCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_interview(db, user_id, interview)

@app.post("/statements/", response_model=schemas.StatementResponse)
def create_statement(statement: schemas.StatementCreate, db: Session = Depends(get_db)):
    return crud.create_statement(db, statement)