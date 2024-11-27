from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import User, Interview
from schemas import UserCreate, InterviewCreate, UserDetail
from utils import hash_password



def  create_user(db: Session, user: UserCreate):
    try:
        hashed_password = hash_password(user.password)
        db_user = User(username=user.username, email=user.email, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print("Error-: ", e)
        return None
    return db_user

def get_users(db: Session) -> list[User]:
    """
    Retrieve all users from the database.
    :param db: SQLAlchemy database session
    :return: List of User objects
    """
    try: 
        db_users = db.query(User).all() 
    except Exception as e:
        print("Error: ", e)
        return None
    
    print("returing usersssss..............")
    return db_users


def get_user(db: Session, user_id: int) -> User:
    db_user = db.query(User).filter(User.id == user_id).first()
    return db_user

def create_interview(db: Session, user_id: int, interview: InterviewCreate):
    db_interview = Interview(user_id=user_id, hr_ai=interview.hr_ai)
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview





from models import Statement
from schemas import StatementCreate
from sqlalchemy.orm import Session

def create_statement(db: Session, statement: StatementCreate):
    db_statement = Statement(
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
