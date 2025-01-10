import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from utils import crud, schemas

@pytest.mark.asyncio
async def test_create_user(async_db_session: AsyncSession):
    user = schemas.UserCreate(username="testuser", email="test@example.com", password="password")
    db_user = await crud.create_user(async_db_session, user)
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_job(async_db_session: AsyncSession):
    job = schemas.JobCreate(title="Developer", description="Develops software", requirements="Python", level=1, industry_id=1)
    db_job = await crud.create_job(async_db_session, job)
    assert db_job.title == "Developer"
    assert db_job.description == "Develops software"
    assert db_job.requirements == "Python"
    assert db_job.level == 1
    assert db_job.industry_id == 1

@pytest.mark.asyncio
async def test_create_statement(async_db_session: AsyncSession):
    statement = schemas.StatementCreate(interview_id=1, speaker="USER", content="What is your name?", is_question=True)
    db_statement = await crud.create_statement(async_db_session, statement)
    assert db_statement.interview_id == 1
    assert db_statement.speaker == "USER"
    assert db_statement.content == "What is your name?"
    assert db_statement.is_question is True

@pytest.mark.asyncio
async def test_create_interview(async_db_session: AsyncSession):
    interview = schemas.InterviewCreate(user_id=1, job_id=1, difficulty="Beginner", start_time="2024-12-01T10:53:24.864000")
    db_interview = await crud.create_interview(async_db_session, interview)
    assert db_interview.user_id == 1
    assert db_interview.job_id == 1
    assert db_interview.difficulty == "Beginner"
    assert db_interview.start_time == "2024-12-01T10:53:24.864000"

@pytest.mark.asyncio
async def test_create_industry(async_db_session: AsyncSession):
    industry = schemas.IndustryCreate(name="Tech", description="Technology industry")
    db_industry = await crud.create_industry(async_db_session, industry)
    assert db_industry.name == "Tech"
    assert db_industry.description == "Technology industry"