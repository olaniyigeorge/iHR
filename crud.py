from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from dependencies import db_dependency
from utils import hash_password


# --- CRUD FOR USERS ---
def create_user(db: Session, user: schemas.UserCreate):
    try:
        hashed_password = hash_password(user.password)
        db_user = models.User(username=user.username, email=user.email, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print("Error-: ", e)
        return None
    return db_user

def get_users(db: Session) -> list[models.User]:
    """
    Retrieve all users from the database.
    :param db: SQLAlchemy database session
    :return: List of User objects
    """
    try: 
        db_users = db.query(models.User).all() 
    except Exception as e:
        print("Error: ", e)
        return None
    return db_users

def get_user(db: Session, user_id: int) -> models.User:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    return db_user




# --- CRUD FOR JOBS ---
def create_job(db: db_dependency, job: schemas.JobCreate) -> models.Job:
    """
    Create a new job in the database.
    """
    new_job = models.Job(
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        level=job.level,
        industry_id=job.industry_id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)  
    return new_job

def get_jobs(
    db: db_dependency, 
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None
) -> List[models.Job]:
    """
    Get a list of jobs with optional filters for pagination and search.
    """
    query = db.query(models.Job)
    if search:
        query = query.filter(models.Job.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def get_job_by_id(db: db_dependency, job_id: int) -> Optional[models.Job]:
    """
    Get a single job by ID.
    """
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def update_job(
    db: db_dependency, 
    job_id: int, 
    job_update: schemas.JobUpdate
) -> Optional[models.Job]:
    """
    Update a job's details by its ID.
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        return None

    if job_update.title:
        job.title = job_update.title
    if job_update.description:
        job.description = job_update.description
    if job_update.requirements:
        job.requirements = job_update.requirements
    if job_update.level:
        job.level = job_update.level
    if job_update.industry_id:
        job.industry_id = job_update.industry_id

    db.commit()
    db.refresh(job)
    return job

def delete_job(db: db_dependency, job_id: int) -> bool:
    """
    Delete a job by its ID.
    """
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        return False

    db.delete(job)
    db.commit()
    return True



# --- CRUD FOR INTERVIEWS ---
def create_interview(db: db_dependency, interview: schemas.InterviewCreate) -> models.Interview:
    db_interview = models.Interview(
        user_id=interview.user_id,
        job_id=interview.job_id,
        difficulty=interview.difficulty.value if isinstance(interview.difficulty, schemas.InterviewDifficulty) else interview.difficulty,
        duration=interview.duration,
        start_time=interview.start_time,
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview


def get_interviews(db: db_dependency, skip: int = 0, limit: int = 10):
    return db.query(models.Interview).offset(skip).limit(limit).all()


def get_interview_by_id(db: db_dependency, interview_id: str) -> models.Interview:
    return db.query(models.Interview).filter(models.Interview.id == interview_id).first()


def update_interview(db: db_dependency, interview_id: str, interview_update: schemas.InterviewUpdate) -> models.Interview:
    db_interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if db_interview:
        for var, value in vars(interview_update).items():
            setattr(db_interview, var, value) if value is not None else None
        db.commit()
        db.refresh(db_interview)
    return db_interview


def delete_interview(db: db_dependency, interview_id: str):
    db_interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if db_interview:
        db.delete(db_interview)
        db.commit()
        return True
    return False






# --- CRUD FOR STATEMENTS ---
def create_statement(db: db_dependency, statement: schemas.StatementCreate):
    db_statement = models.Statement(
        speaker=statement.speaker,
        content=statement.content,
        is_question=statement.is_question,
        interview_id=statement.interview_id,
        replies_to_id=statement.replies_to_id
    )
    db.add(db_statement)
    db.commit()
    db.refresh(db_statement)
    return db_statement
