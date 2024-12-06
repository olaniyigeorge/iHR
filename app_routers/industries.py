from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import crud  # Assumes CRUD operations for Industry are implemented in this module
import schemas  # Assumes schemas for Industry are defined here
from dependencies import db_dependency

router = APIRouter(
    prefix="/industries",
    tags=["industries"]
)

@router.post("/", response_model=schemas.IndustryResponse, status_code=status.HTTP_201_CREATED)
def create_industry(industry: schemas.IndustryCreate, db: db_dependency):
    """
    Create a new industry.
    """
    try:
        new_industry = crud.create_industry(db, industry)
        return new_industry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating industry: {str(e)}"
        )

@router.get("/", response_model=List[schemas.IndustryResponse])
def get_industries(db: db_dependency, skip: int = 0, limit: int = 10):
    """
    Fetch a list of industries with optional pagination.
    """
    return crud.get_industries(db, skip=skip, limit=limit)

@router.get("/{industry_id}", response_model=schemas.IndustryResponse)
def get_industry(industry_id: int, db: db_dependency):
    """
    Fetch a single industry by ID.
    """
    industry = crud.get_industry_by_id(db, industry_id)
    if not industry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industry not found")
    return industry

@router.patch("/{industry_id}", response_model=schemas.IndustryResponse)
def update_industry(
    industry_id: int,
    industry_update: schemas.IndustryUpdate,
    db: db_dependency
):
    """
    Update an industry's details by its ID.
    """
    updated_industry = crud.update_industry(db, industry_id, industry_update)
    if not updated_industry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industry not found")
    return updated_industry

@router.delete("/{industry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_industry(industry_id: int, db: db_dependency):
    """
    Delete an industry by its ID.
    """
    deleted = crud.delete_industry(db, industry_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Industry not found")
    return {"message": "Industry deleted successfully"}
