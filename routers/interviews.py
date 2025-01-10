from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import utils.crud as crud
import utils.schemas as schemas
from utils.dependencies import async_db_session_dependency
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"]
)

@router.post("/", response_model=schemas.InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(interview: schemas.InterviewCreate, db: AsyncSession = Depends(async_db_session_dependency)):
    try:
        new_interview = await crud.create_interview(db, interview)
        return new_interview
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating interview: {str(e)}"
        )

@router.get("/", response_model=List[schemas.InterviewResponse])
async def get_interviews(db: AsyncSession = Depends(async_db_session_dependency), skip: int = 0, limit: int = 10):
    """
    Fetch a list of interviews with optional pagination.
    """
    return await crud.get_interviews(db, skip=skip, limit=limit)

@router.get("/{interview_id}", response_model=schemas.InterviewResponse)
async def get_interview(interview_id: str, db: AsyncSession = Depends(async_db_session_dependency)):
    """
    Fetch a single interview by ID.
    """
    interview = await crud.get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.get("/ctx/{interview_id}", response_model=schemas.InterviewContext)
async def get_interview_context(interview_id: str, db: AsyncSession = Depends(async_db_session_dependency)):
    """
    Fetch a single interview's context by ID.
    """
    interview = await crud.get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.patch("/{interview_id}", response_model=schemas.InterviewResponse)
async def update_interview(
    interview_id: str,
    interview_update: schemas.InterviewUpdate,
    db: AsyncSession = Depends(async_db_session_dependency)
):
    """
    Update an interview's details by its ID.
    """
    updated_interview = await crud.update_interview(db, interview_id, interview_update)
    if not updated_interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return updated_interview

@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(interview_id: str, db: AsyncSession = Depends(async_db_session_dependency)):
    """
    Delete an interview by its ID.
    """
    deleted = await crud.delete_interview(db, interview_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interview not found")
    return {"message": "Interview deleted successfully"}