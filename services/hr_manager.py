from fastapi import HTTPException
from datetime import datetime
from decouple import config as decouple_config
import json
import os
from io import BytesIO
from dotenv import load_dotenv
import redis

import utils.crud as crud, utils.models as models, utils.schemas as schemas
from utils.schemas import InterviewContext
from utils.dependencies import async_db_session_dependency
from config import config
load_dotenv()

OPENAI_API_KEY = config.OPENAI_API_KEY

# Configure Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
CACHE_TTL = 180  # Cache Time-To-Live in seconds (3 minutes)

class AIResponse:
    score: float
    insights: dict[str, list[str]]  # e.g., {"strengths": [...], "weaknesses": [...]}



class HRManager:
    @staticmethod
    async def updateScoreInsights(interview: InterviewContext, new_response: str) -> AIResponse:
        from langchain_openai.chat_models import ChatOpenAI
        from langchain_core.output_parsers import StrOutputParser

        model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")
        parser = StrOutputParser()
        chain = model | parser

        response: AIResponse = chain.invoke(
            f"""
            Based on the conversation {interview.statements}, in the interview {interview.title} and the response {new_response}, 
            award a score between 0 and 10 to the user's last statement and extract insights to show the user's strengths and weaknesses in the format(AIResponse)
            """
        )

        return response

    @staticmethod
    async def update_interview(id: int, ai_response: str):
        interview: models.Interview = await crud.get_interview_by_id(id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        # Status constants
        SCHEDULED = "Scheduled"
        ONGOING = "Ongoing"
        COMPLETED = "Completed"
        CANCELLED = "Cancelled"

        if interview.status in [CANCELLED, COMPLETED]:
            return {"status": interview.status, "message": "Interview is already finalized."}

        current_time = datetime.now()

        if current_time < interview.start_time:
            interview.status = SCHEDULED
        elif interview.start_time <= current_time <= interview.end_time:
            interview.status = ONGOING
            interview.current_score = min(100, interview.current_score + ai_response.score)
            interview.insights["strengths"].extend(ai_response.insights.get("strengths", []))
            interview.insights["weaknesses"].extend(ai_response.insights.get("weaknesses", []))
        elif current_time > interview.end_time:
            interview.status = COMPLETED

        await crud.update_interview(interview)
        return {"status": "Updated", "interview": interview}

    @staticmethod
    async def get_conversation_context(interview_id: int) -> InterviewContext:
        cached_ctx = redis_client.get(f"interview_ctx:{interview_id}")
        
        if cached_ctx:
            print("Cache hit for interview context.")
            return json.loads(cached_ctx)
        
        print("Cache miss for interview context. Fetching from DB.")
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
        
        redis_client.set(f"interview_ctx:{interview_id}", json.dumps(ctx), ex=CACHE_TTL)
        return ctx

    @staticmethod
    async def get_ai_response(prompt: str, interview_ctx: InterviewContext) -> str:
        try:
            # TODO: Send prompt to model using interview_ctx as conversation context  
            ai_response = "ai response"
        except Exception as e:
            # log_dict = {
            #     "method": "get_ai_response",
            #     "error details": e,
            # }
            # logger.logger.error(log_dict, extra=log_dict)
            #TODO: Log error
            ai_response = "I'm sorry, I couldn't understand that. Could you please rephrase"

        return ai_response

    @staticmethod
    def convert_audio_to_text(audio_data: bytes) -> str:
        from speech_recognition import Recognizer, AudioFile

        recognizer = Recognizer()
        audio = AudioFile(BytesIO(audio_data))
        with audio as source:
            audio_content = recognizer.record(source)
        return recognizer.recognize_google(audio_content)

    @staticmethod
    def convert_text_to_audio(text: str) -> bytes:
        from gtts import gTTS

        tts = gTTS(text)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()

    @staticmethod
    async def create_statement(
            statement_body: str, 
            speaker: str, 
            interview_id: int, 
            replies_id: int, 
            db: async_db_session_dependency
        ):
        statement = schemas.StatementCreate(
            interview_id=interview_id,
            speaker=speaker,
            content=statement_body,
            is_question=False,
            timestamp=datetime.now(),
            replies_id=0
        )

        try:
            new_statement = await crud.async_create_statement(db, statement)
            print("Statement created successfully.")
            return new_statement
        except Exception as e:
            print(f"Error creating statement: {str(e)}")

    @staticmethod
    async def process_text_input(content: str, interview_ctx: dict) -> dict:
        try:
            await crud.create_statement(
                statement_body=content,
                speaker=f"USER-{interview_ctx['user_id']}",
                interview_id=interview_ctx["id"],
                db=async_db_session_dependency
            )
            ai_response = await HRManager.get_ai_response(content, interview_ctx)
            await HRManager.create_statement(
                statement_body=ai_response,
                speaker=interview_ctx["hr_ai"],
                interview_id=interview_ctx["id"],
                db=async_db_session_dependency
            )
            await update_interview(interview_ctx["id"], ai_response)
            return {
                "type": "text",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": ai_response,
            }
        except Exception as e:
            return {
                "type": "text",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": f"An error occurred: {str(e)}",
            }

    @staticmethod
    async def process_audio_input(content: str, interview_ctx: dict) -> dict:
        try:
            transcript = HRManager.convert_audio_to_text(content)
            ai_response = await HRManager.get_ai_response(transcript, interview_ctx)
            return {
                "type": "audio",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": HRManager.convert_text_to_audio(ai_response),
            }
        except Exception as e:
            return {
                "type": "audio",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": f"An error occurred: {str(e)}",
            }

    @staticmethod
    async def process_video_input(content: str, interview_ctx: dict) -> dict:
        try:
            transcript = HRManager.convert_video_to_text(content)
            ai_response = await HRManager.get_ai_response(transcript, interview_ctx)
            return {
                "type": "video",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": HRManager.convert_text_to_video(ai_response),
            }
        except Exception as e:
            return {
                "type": "video",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": f"An error occurred: {str(e)}",
            }

    @staticmethod
    async def process_transcript_input(content: str, interview_ctx: dict) -> dict:
        try:
            ai_response = await HRManager.get_ai_response(content, interview_ctx)
            return {
                "type": "transcript",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": ai_response,
            }
        except Exception as e:
            return {
                "type": "transcript",
                "role": interview_ctx["hr_ai"],
                "interview_ctx": interview_ctx,
                "content": f"An error occurred: {str(e)}",
            }
