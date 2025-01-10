from datetime import datetime
import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

import utils.crud as crud
from utils.dependencies import async_db_session_dependency
from sqlalchemy.ext.asyncio import AsyncSession
import utils.schemas as schemas
from services import hr_manager


router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)


@router.websocket("/simulate-interview/{interview_id}")
async def interview_simulate(websocket: WebSocket, interview_id: int, mode: str = "text"):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            input_type = message.get("type")
            role = message.get("role")
            content = message.get("content")
            
            if input_type not in ["text", "audio", "video", "transcript"]:
                await websocket.send_text(json.dumps({"error": "Invalid input type"}))
                continue

            interview_ctx = await hr_manager.get_conversation_context(interview_id)

            if input_type == "text":
                response = await process_text_input(content, interview_ctx)
            elif input_type == "audio":
                response = await process_audio_input(content, interview_ctx)
            elif input_type == "video":
                response = await process_video_input(content, interview_ctx)
            elif input_type == "transcript":
                response = await process_transcript_input(content, interview_ctx)
            else:
                response = {"error": "Invalid input type"}

            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print("Client disconnected")


async def process_text_input(content: str, interview_ctx: dict) -> dict:
    try:
        await crud.create_statement(
            statement_body=content,
            speaker=f"USER-{interview_ctx['user_id']}",
            interview_id=interview_ctx["id"],
            db=async_db_session_dependency
        )
        ai_response = await hr_manager.get_ai_response(content, interview_ctx)
        await hr_manager.create_statement(
            statement_body=ai_response,
            speaker=interview_ctx["hr_ai"],
            interview_id=interview_ctx["id"],
            db=async_db_session_dependency
        )
        await hr_manager.update_interview(interview_ctx["id"], ai_response)
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


async def process_audio_input(content: str, interview_ctx: dict) -> dict:
    try:
        transcript = hr_manager.convert_audio_to_text(content)
        ai_response = await hr_manager.get_ai_response(transcript, interview_ctx)
        return {
            "type": "audio",
            "role": interview_ctx["hr_ai"],
            "interview_ctx": interview_ctx,
            "content": hr_manager.convert_text_to_audio(ai_response),
        }
    except Exception as e:
        return {
            "type": "audio",
            "role": interview_ctx["hr_ai"],
            "interview_ctx": interview_ctx,
            "content": f"An error occurred: {str(e)}",
        }


async def process_video_input(content: str, interview_ctx: dict) -> dict:
    try:
        transcript = hr_manager.convert_video_to_text(content)
        ai_response = await hr_manager.get_ai_response(transcript, interview_ctx)
        return {
            "type": "video",
            "role": interview_ctx["hr_ai"],
            "interview_ctx": interview_ctx,
            "content": hr_manager.convert_text_to_video(ai_response),
        }
    except Exception as e:
        return {
            "type": "video",
            "role": interview_ctx["hr_ai"],
            "interview_ctx": interview_ctx,
            "content": f"An error occurred: {str(e)}",
        }


async def process_transcript_input(content: str, interview_ctx: dict) -> dict:
    try:
        ai_response = await hr_manager.get_ai_response(content, interview_ctx)
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
