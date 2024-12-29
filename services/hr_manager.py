from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI
from datetime import datetime
from decouple import config as decouple_config
import json
import os
from io import BytesIO
from pydub import AudioSegment
from dotenv import load_dotenv
import redis

import crud, models, schemas
from schemas import InterviewContext
from dependencies import async_db_session_dependency
from sqlalchemy.ext.asyncio import AsyncSession
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
open_api_key = decouple_config('OPENAI_API_KEY', cast=str)

# Configure Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, protocol=3)
CACHE_TTL = 180  # Cache Time-To-Live in seconds (3 minutes)


# update_interview

import json
from typing import Dict

from schemas import InterviewContext


class AIResponse():
    score: float
    insights: Dict[str, list[str]]  # e.g., {"strengths": [...], "weaknesses": [...]} 

async def updateScoreInsights(interview: InterviewContext, new_response: str) -> AIResponse:
    from langchain_openai.chat_models import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser


    model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
    
    parser = StrOutputParser()

    chain = model | parser

    response: AIResponse = chain.invoke(
        """
        Based on the conversation {interview.statements}, in the interview{interview.title} and the response{response}, 
        award a score between 0 and 10 to the user's last statement and extract insights to show the user's strenghts and weaknesses in the format(AIResponse)
        """
    )

    return response


async def update_interview(id: int, ai_response: str):

    # update socre ad insights
    await updateScoreInsights(interview, ai_response)


    # Fetch interview
    interview: models.Interview = await crud.get_interview_by_id(id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Status constants
    SCHEDULED = "Scheduled"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

    # Handle already finalized interviews
    if interview.status in [CANCELLED, COMPLETED]:
        return {"status": interview.status, "message": "Interview is already finalized."}

    # Get the current time
    current_time = datetime.now()

    # Update status and details
    if current_time < interview.start_time:
        interview.status = SCHEDULED  # Ensure status remains Scheduled if before start_time
    elif interview.start_time <= current_time <= interview.end_time:
        interview.status = ONGOING

        # Update current score
        interview.current_score = min(100, interview.current_score + ai_response.score)

        # Update insights
        interview.insights["strengths"].extend(ai_response.insights.get("strengths", []))
        interview.insights["weaknesses"].extend(ai_response.insights.get("weaknesses", []))
    elif current_time > interview.end_time:
        interview.status = COMPLETED

    # Save changes (assumes a save or update method in CRUD)
    await crud.update_interview(interview)

    return {"status": "Updated", "interview": interview}
 

# Get conversation context 
async def get_conversation_context(interview_id: int) -> InterviewContext:
    # Check Redis for cached context
    cached_ctx = redis_client.get(f"interview_ctx:{interview_id}")
    
    if cached_ctx:
        print("Cache hit for interview context.")
        return json.loads(cached_ctx)
    
    print("Cache miss for interview context. Fetching from DB.")
    # Fallback to database or hardcoded context
    ctx = {
        "hr_ai": "iHR AI",
        "status": "Scheduled",
        "id": interview_id,
        "user_id": 1,
        "job_id": 1,
        "job": {
            "title": "Junior Python Developer",
            "description": "A python developer proficient in the python programming language and any of its frameworks e.g Django, FastAPI",
            "requirements": "Python, Django, FastAPI",
            "id": 1,
            "level": 1,
            "industry_id": 1
        },
        "difficulty": "Beginner",
        "duration": "PT30M",
        "start_time": "2024-11-30T10:53:24.864000",
        "end_time": "2024-12-01T10:53:24.864000",
        "current_score": 30,
        "insights": {
            "strengths": [
                "understands best practices",
                "proof with projects"
            ],
            "weaknesses": [
                "poor communication"
            ]
        },
        "statements": [
            {"speaker": "user", "body": "What are my responsibilities for this role?"},
            {"speaker": "user", "body": "How much will I be paid?"},
            {"speaker": "ihr-ai-0", "body": "You will be paid $2000 per month"},
        ]
    }
    
    # Cache the context for future use
    redis_client.set(f"interview_ctx:{interview_id}", json.dumps(ctx), ex=CACHE_TTL)
    return ctx


# Function to process text with AI
async def get_ai_response(prompt: str, interview_ctx: InterviewContext) -> str:
    try:
        client = OpenAI(
                api_key=open_api_key,
                max_retries=2,
            )
        response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                        {"role": "system", "content": f"You are an HR interviewer interviewng for a {interview_ctx['job']['title']} role."}, 
                        {"role": "system", "content": f"The interview difficulty level is set to{interview_ctx['difficulty']}."}, 
                        {"role": "system", "content": f"The history of this conversation is; {interview_ctx['statements']}"}, 
                        {"role": "system", "content": f"The history of this conversation is; {interview_ctx['statements']}"}, 
                        
                        {"role": "user", "content": f"{interview_ctx["user"]["username"]} said {prompt}"}
                ],
        )
        print(response.choices[0].message)
        ai_response = response["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error: ", e)
        ai_response = response = f"You are doing well. {datetime.now()}"

    return ai_response 



# Function to convert audio to text (example with SpeechRecognition)
def convert_audio_to_text(audio_data: bytes) -> str:
    from speech_recognition import Recognizer, AudioFile

    recognizer = Recognizer()
    audio = AudioFile(BytesIO(audio_data))
    with audio as source:
        audio_content = recognizer.record(source)
    return recognizer.recognize_google(audio_content)



# Function to convert text to audio (using gTTS as an example)
def convert_text_to_audio(text: str) -> bytes:
    from gtts import gTTS

    tts = gTTS(text)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()


async def create_statement(
        statement_body: str, 
        speaker: str, 
        interview_id: int, 
        replies_id: int, 
        db: AsyncSession
    ):
    statement = schemas.StatementCreate(
        interview_id=interview_id,
        speaker=speaker,
        content=statement_body,
        is_question=False,
        timestamp=datetime.now(),
        replies_id=0
    )

    print("STATEMENT: ", statement, "\n", type(statement))
    try:
        new_statement = await crud.async_create_statement(db, statement)
        print("Statement created successfully.")
        return new_statement
    except Exception as e:
        # Retry
        # raise HTTPException(
        #     status_code=400,
        #     detail=f"Error creating statement: {str(e)}"
        # )
        print(f"Error creating statement: {str(e)}")


# def create_statement(statement: schemas.StatementCreate, db: async_db_session_dependency):
#     try:
#         new_statement = crud.create_statement(db, statement)
#         return new_statement
#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Error creating statement: {str(e)}"
#         )