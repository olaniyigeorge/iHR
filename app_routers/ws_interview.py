from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import openai
import json
from io import BytesIO
from pydub import AudioSegment
import os
import time

from schemas import InterviewContext



# OpenAI Configuration (replace with your API key)
openai.api_key = os.getenv("OPENAI_API_KEY")


router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)



@router.websocket("/simulate-interview/{interview_id}")
async def interview_simulate(websocket: WebSocket, interview_id: int, mode: str="text"):
    # get inteview from a cache with ttl set to 3 mins 
    interview = {
        "hr_ai": "iHR AI",
        "status": "Scheduled",
        "id": 1,
        "user_id": 1,
        "job_id": 1,
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
        }
        }
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            input_type = message.get("type") 
            role = message.get("role")  # "text", "audio", or "transcript"
            content = message.get("content")  # Input content
            mode = mode # text, code, audio, board, video
            interview = interview_id

            if input_type not in ["text", "audio", "video", "transcript"]:
                {"error": "Invalid input type"}

            conversation_trigger = {}
            interview_ctx: InterviewContext = await get_conversation_context(interview_id=interview)
            
            # Process user input
            if input_type == "audio":
                transcript = convert_audio_to_text(content)
                ai_response = await get_ai_response(transcript, interview_ctx)
                audio_response = convert_text_to_audio(ai_response)
                response = {
                    "type": "audio",
                    "role": role,
                    "interview_ctx": interview_ctx, 
                    "content": audio_response,
                }
            elif input_type == "text":
                ai_response = await get_ai_response(content, interview_ctx)
                response = {
                    "type": "text",
                    "role": role,
                    "interview_ctx": interview_ctx, 
                    "content": ai_response,
                }
            elif input_type == "transcript":
                ai_response = await get_ai_response(content, interview_ctx)
                response = {
                    "type": "transcript",
                    "role": role,
                    "interview_ctx": interview_ctx,
                    "content": ai_response,
                }
            else:
                response = {"error": "Invalid input type"}

            # Send response back to client
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print("Client disconnected")

# Get conversation context -- TODO Cache 
async def get_conversation_context(interview_id: int) -> InterviewContext: 
    ctx = {
        "hr_ai": "iHR AI",
        "status": "Scheduled",
        "id": 1,
        "user_id": 1,
        "job_id": 1,
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
        ]
    }
    
    return ctx

# Function to process text with AI
async def get_ai_response(prompt: str, interview_ctx: InterviewContext) -> str:

    # response = await openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #             {"role": "system", "content": f"You are an HR interviewer interviewng for a {interview_ctx.job.model_dump("title")} role."}, 
    #             {"role": "system", "content": f"The interview difficulty level is set to{interview_ctx.difficulty}."}, 
    #             {"role": "system", "content": f"The history of this conversation is; {interview_ctx.statements}"}, 
    #             # {"role": "system", "content": f"The history of this conversation is; {interview_ctx.statements}"}, 

    #             {"role": "user", "content": prompt}
    #     ],
    # )

    response = f"You are doing well. {time.time()}"

    return response # response["choices"][0]["message"]["content"]



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
