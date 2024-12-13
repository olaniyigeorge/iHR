from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from openai import OpenAI
import json
from io import BytesIO
from pydub import AudioSegment
import os
import time
from decouple import config as decouple_config

import crud
from schemas import InterviewContext
from dependencies import db_dependency
import schemas

open_api_key = decouple_config('OPENAI_API_KEY', cast=str)

import redis

# Configure Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, protocol=3)
CACHE_TTL = 180  # Cache Time-To-Live in seconds (3 minutes)





router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)



@router.websocket("/simulate-interview/{interview_id}")
async def interview_simulate(websocket: WebSocket, interview_id: int, mode: str = "text"):
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            input_type = message.get("type") 
            role = message.get("role")  # "text", "audio", or "transcript"
            content = message.get("content")  # Input content
            
            if input_type not in ["text", "audio", "video", "transcript"]:
                await websocket.send_text(json.dumps({"error": "Invalid input type"}))
                continue

            # Fetch interview context
            interview_ctx = await get_conversation_context(interview_id)
            
            # Process user input
            if input_type == "text":
                await create_statement(
                    statement_body=content, 
                    user_id=interview_ctx["user_id"], 
                    interview_id=interview_ctx["id"], 
                    db=db_dependency
                )
                ai_response = await get_ai_response(content, interview_ctx)
                response = {
                    "type": "text",
                    "role": interview_ctx["hr_ai"],
                    "interview_ctx": interview_ctx, 
                    "content": ai_response,
                }
            elif input_type == "audio":
                transcript = convert_audio_to_text(content)
                ai_response = await get_ai_response(transcript, interview_ctx)
                response = {
                    "type": "audio",
                    "role": interview_ctx["hr_ai"],
                    "interview_ctx": interview_ctx, 
                    "content": convert_text_to_audio(ai_response),
                }
            else:
                response = {"error": "Invalid input type"}

            # Send response back to client
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print("Client disconnected")

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
                        # {"role": "system", "content": f"You are an HR interviewer interviewng for a {interview_ctx['job']['title']} role."}, 
                        # {"role": "system", "content": f"The interview difficulty level is set to{interview_ctx['difficulty']}."}, 
                        # {"role": "system", "content": f"The history of this conversation is; {interview_ctx['statements']}"}, 
                        # # {"role": "system", "content": f"The history of this conversation is; {interview_ctx.statements}"}, 

                        {"role": "user", "content": prompt[:20]}
                ],
        )
        print(response.choices[0].message)
        ai_response = response["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error: ", e)
        ai_response = response = f"You are doing well. {time.time()}"

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


async def create_statement(statement_body: str, user_id: int, interview_id: int, db: db_dependency):
    statement = schemas.StatementCreate(
        interview_id=interview_id,
        speaker=f"USER-{user_id}",
        content=statement_body,
        is_question=False,
        timestamp=datetime.utcnow(),
        replies_id=None
    )
    print("STATEMENT: ", statement, "\n", type(statement))
    try:
        new_statement = crud.create_statement(db, statement)
        print("Statement created successfully.")
        return new_statement
    except Exception as e:
        # Retry
        # raise HTTPException(
        #     status_code=400,
        #     detail=f"Error creating statement: {str(e)}"
        # )
        print(f"Error creating statement: {str(e)}")
