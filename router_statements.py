from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import crud
import schemas
from dependencies import db_dependency

router = APIRouter(
    prefix="/statements",
    tags=["statements"]
)

@router.post("/", response_model=schemas.StatementResponse, status_code=status.HTTP_201_CREATED)
def create_statement(statement: schemas.StatementCreate, db: db_dependency):
    try:
        new_statement = crud.create_statement(db, statement)
        return new_statement
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating statement: {str(e)}"
        )


@router.get("/", response_model=List[schemas.StatementResponse])
def get_statements(db: db_dependency, skip: int = 0, limit: int = 10):
    """
    Fetch a list of statements with optional pagination.
    """
    return crud.get_statements(db, skip=skip, limit=limit)


@router.get("/{statement_id}", response_model=schemas.StatementResponse)
def get_statement(statement_id: str, db: db_dependency):
    """
    Fetch a single statement by ID.
    """
    statement = crud.get_statement_by_id(db, statement_id)
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return statement


@router.patch("/{statement_id}", response_model=schemas.StatementResponse)
def update_statement(
    statement_id: str,
    statement_update: schemas.StatementUpdate,
    db: db_dependency
):
    """
    Update a statement's details by its ID.
    """
    updated_statement = crud.update_statement(db, statement_id, statement_update)
    if not updated_statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return updated_statement


@router.delete("/{statement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_statement(statement_id: str, db: db_dependency):
    """
    Delete a statement by its ID.
    """
    deleted = crud.delete_statement(db, statement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Statement not found")
    return {"message": "Statement deleted successfully"}
