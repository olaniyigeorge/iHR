from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import utils.crud as crud 
import utils.schemas as schemas 
from utils.dependencies import async_db_session_dependency

router = APIRouter(
    prefix="/industries",
    tags=["industries"]
)

@router.post("/", response_model=schemas.IndustryResponse, status_code=status.HTTP_201_CREATED)
async def create_industry(industry: schemas.IndustryCreate, db: AsyncSession = Depends(async_db_session_dependency)):
    """
    Create a new industry.
    """
    try:
        new_industry = await crud.create_industry(db, industry)
        return new_industry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating industry: {str(e)}"
        )

@router.get("/", response_model=List[schemas.IndustryResponse])
async def get_industries(db: AsyncSession = Depends(async_db_session_dependency), skip: int = 0, limit: int = 10):
    """
    Fetch a list of industries with optional pagination.
    """
    return await crud.get_industries(db, skip=skip, limit=limit)