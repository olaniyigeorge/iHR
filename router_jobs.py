from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from dependencies import db_dependency
import schemas, crud

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)




@router.post("/", response_model=schemas.JobDetails, status_code=status.HTTP_201_CREATED)
async def create_job(job: schemas.JobCreate, db: db_dependency):
    print("\n\n\n ", job, "\n\n\n")
    try:
        new_job = await crud.create_job(db, job)
        return new_job
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating job: {str(e)}"
        )