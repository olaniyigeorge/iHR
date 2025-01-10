from utils.schemas import UserCreate, JobCreate, StatementCreate, InterviewCreate, IndustryCreate

def test_user_create_schema():
    user = UserCreate(username="testuser", email="test@example.com", password="password")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password"

def test_job_create_schema():
    job = JobCreate(title="Developer", description="Develops software", requirements="Python", level=1, industry_id=1)
    assert job.title == "Developer"
    assert job.description == "Develops software"
    assert job.requirements == "Python"
    assert job.level == 1
    assert job.industry_id == 1

def test_statement_create_schema():
    statement = StatementCreate(interview_id=1, speaker="USER", content="What is your name?", is_question=True)
    assert statement.interview_id == 1
    assert statement.speaker == "USER"
    assert statement.content == "What is your name?"
    assert statement.is_question is True

def test_interview_create_schema():
    interview = InterviewCreate(user_id=1, job_id=1, difficulty="Beginner", start_time="2024-12-01T10:53:24.864000")
    assert interview.user_id == 1
    assert interview.job_id == 1
    assert interview.difficulty == "Beginner"
    assert interview.start_time == "2024-12-01T10:53:24.864000"

def test_industry_create_schema():
    industry = IndustryCreate(name="Tech", description="Technology industry")
    assert industry.name == "Tech"
    assert industry.description == "Technology industry"