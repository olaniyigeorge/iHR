from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import crud
import schemas
from dependencies import get_async_db_session

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

@router.post("/", response_model=schemas.JobDetails, status_code=status.HTTP_201_CREATED)
async def create_job(job: schemas.JobCreate, db: AsyncSession = Depends(get_async_db_session)):
    try:
        new_job = await crud.create_job(db, job)
        return new_job
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating job: {str(e)}"
        )

@router.get("/", response_model=List[schemas.JobDetails])
async def get_jobs(
    db: AsyncSession = Depends(get_async_db_session),
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None
):
    """
    Fetch a list of jobs with optional pagination and search.
    """
    return await crud.get_jobs(db, skip=skip, limit=limit, search=search)

@router.get("/{job_id}", response_model=schemas.JobDetails)
async def get_job(job_id: int, db: AsyncSession = Depends(get_async_db_session)):
    """
    Fetch a single job by ID using the CRUD function.
    """
    job = await crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.patch("/{job_id}", response_model=schemas.JobDetails)
async def update_job(
    job_id: int, 
    job_update: schemas.JobUpdate, 
    db: AsyncSession = Depends(get_async_db_session)
):
    """
    Update a job's details by its ID using the CRUD function.
    """
    updated_job = await crud.update_job(db, job_id, job_update)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int, db: AsyncSession = Depends(get_async_db_session)):
    """
    Delete a job by its ID using the CRUD function.
    """
    deleted = await crud.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}