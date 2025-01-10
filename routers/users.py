from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from utils import crud, schemas
from utils.dependencies import async_db_session_dependency, user_dependency

router = APIRouter(
    prefix="/users",
    tags=["users"]
)
#  ---- User CRUD ------
@router.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: async_db_session_dependency):
    db_user = await crud.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return db_user

@router.get("/users/", response_model=list[schemas.UserDetail])
async def list_user(db: async_db_session_dependency):
    users = await crud.get_users(db)
    if not users:
        raise HTTPException(status_code=400, detail="Error getting users")
    return [schemas.UserDetail.model_validate(user) for user in users]

@router.get("/users/{user_id}", response_model=schemas.UserDetail)
async def get_user(user_id: int, db: async_db_session_dependency):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserDetail.model_validate(user)

@router.get("/user/me")
async def get_current_user_info(user: user_dependency, db: async_db_session_dependency):
    if user is None:
        raise HTTPException(status_code=403, detail="Authentication Failed")
    return {"User": user}

