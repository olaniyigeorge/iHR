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
from utils import get_db



router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "beiey13r2ur24h42342424r2524524uirr2lr242rb23br2rl2uiryh2blev23te2x3e2rxe2tec23"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

db_dependency = Annotated[Session, Depends(get_db)]



@router.post("/", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        username=user.username, 
        email=user.email, 
        password=bcrypt_context.hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 db: db_dependency):
    print("\n\n\n FormData: ", form_data, "\n\n")
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
    print("Authenticating user.............\n\n\n\n")
    user = db.query(User).filter(User.email==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    print("Authentication complete.............\n\n\n\n")
    return user


