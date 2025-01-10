from datetime import datetime
import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

import utils.crud as crud
from utils.dependencies import async_db_session_dependency
from sqlalchemy.ext.asyncio import AsyncSession
from services.hr_manager import HRManager

router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

hr_manager = HRManager()

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
                response = await hr_manager.process_text_input(content, interview_ctx)
            elif input_type == "audio":
                response = await hr_manager.process_audio_input(content, interview_ctx)
            elif input_type == "video":
                response = await hr_manager.process_video_input(content, interview_ctx)
            elif input_type == "transcript":
                response = await hr_manager.process_transcript_input(content, interview_ctx)
            else:
                response = {"error": "Invalid input type"}

            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print("Client disconnected")
