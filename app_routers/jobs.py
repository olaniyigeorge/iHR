from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from dependencies import db_dependency
import schemas, crud

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)




@router.post("/", response_model=schemas.JobDetails, status_code=status.HTTP_201_CREATED)
def create_job(job: schemas.JobCreate, db: db_dependency):
    print("\n\n\n ", job, "\n\n\n")
    try:
        new_job = crud.create_job(db, job)
        return new_job
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating job: {str(e)}"
        )
    
@router.get("/", response_model=List[schemas.JobDetails])
def get_jobs(
    db: db_dependency, 
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None
):
    """
    Fetch a list of jobs with optional pagination and search.
    """
    return crud.get_jobs(db, skip=skip, limit=limit, search=search)


@router.get("/{job_id}", response_model=schemas.JobDetails)
def get_job(job_id: int, db: db_dependency):
    """
    Fetch a single job by ID using the CRUD function.
    """
    job = crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.patch("/{job_id}", response_model=schemas.JobDetails)
def update_job(
    job_id: int, 
    job_update: schemas.JobUpdate, 
    db: db_dependency
):
    """
    Update a job's details by its ID using the CRUD function.
    """
    updated_job = crud.update_job(db, job_id, job_update)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: db_dependency):
    """
    Delete a job by its ID using the CRUD function.
    """
    deleted = crud.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}
