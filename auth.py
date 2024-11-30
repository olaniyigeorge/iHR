from datetime import datetime, timezone, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status 

import crud
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer 
from jose import jwt, JWTError
from schemas import Token, UserCreate, UserDetail, UserResponse
from dependencies import db_dependency


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "beiey13r2ur24h42342424r2524524uirr2lr242rb23br2rl2uiryh2blev23te2x3e2rxe2tec23"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")



# --- User Registeration ---
@router.post("/register/", response_model=UserDetail, status_code=status.HTTP_201_CREATED, name="user_registeration")
async def create_user(user: UserCreate, db: db_dependency):
    try:
        db_user = User(
        username=user.username, 
        email=user.email, 
        password=bcrypt_context.hash(user.password)
    )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e: # (sqlite3.IntegrityError) UNIQUE constraint failed: users.email
        print("Exception-------- ", e)
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Could not create user"
            )
    return db_user


# --- Login for JWT ---
@router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )
    token = create_access_token(user.username, user.id, timedelta(minutes=30))

    return {
        "access_token": token,
        "token_type": "Bearer"
    }


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.email==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        print("Payload  ", payload)
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Could not validate user"
            )
        return {
            "username": username,
            "id": user_id
        }

    except JWTError:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Could not validate user"
            )