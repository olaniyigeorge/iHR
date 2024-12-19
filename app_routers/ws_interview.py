from datetime import datetime
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict


import crud
from dependencies import db_dependency
# from services.hr_manager import convert_audio_to_text, convert_text_to_audio, create_statement, get_ai_response, get_conversation_context, update_interview
import schemas
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
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            input_type = message.get("type") # "text", "audio", or "transcript"
            role = message.get("role")  
            content = message.get("content")  # Input content
            
            if input_type not in ["text", "audio", "video", "transcript"]:
                await websocket.send_text(json.dumps({"error": "Invalid input type"}))
                continue

            # Fetch interview context
            interview_ctx = await hr_manager.get_conversation_context(interview_id)

            # If statements in interview_ctx is empty 
                # Welcome and introduce user to the interview
            # Else if last statement speaker is ihr-ai, 
                # Re-echo statement 
            
            # Process user input
            if input_type == "text":
                try:
                    print("creating user statement... \n\n")
                    await create_statement(
                        statement_body=content, 
                        speaker=f"USER-{interview_ctx["user_id"]}", 
                        interview_id=interview_ctx["id"], 
                        db=db_dependency
                    )
                    print("getting ai response... \n\n")
                    ai_response = await hr_manager.get_ai_response(content, interview_ctx)
                    print("creating ai statement...\n\n")
                    await hr_manager.create_statement(
                        statement_body=ai_response, 
                        speaker=interview_ctx["ihr-ai"],  # ihr-ai
                        interview_id=interview_ctx["id"], 
                        db=db_dependency
                    )
                    print("updating interview score and insights... \n\n")
                    await hr_manager.update_interview(interview_ctx["id"], ai_response)
                    response = {
                        "type": "text",
                        "role": interview_ctx["hr_ai"],
                        "interview_ctx": interview_ctx, 
                        "content": ai_response,
                    }
                except:
                    response = {
                    "type": "text",
                    "role": interview_ctx["hr_ai"],
                    "interview_ctx": interview_ctx, 
                    "content": "An error occurred",
                    }   

                
            elif input_type == "audio":
                transcript = hr_manager.convert_audio_to_text(content)
                ai_response = await hr_manager.get_ai_response(transcript, interview_ctx)
                response = {
                    "type": "audio",
                    "role": interview_ctx["hr_ai"],
                    "interview_ctx": interview_ctx, 
                    "content": hr_manager.convert_text_to_audio(ai_response),
                }
            else:
                response = {"error": "Invalid input type"}

            # Send response back to client
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print("Client disconnected")




async def create_statement(statement_body: str, speaker: str, interview_id: int, replies: int, db: db_dependency):
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
