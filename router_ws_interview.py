from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import openai
import json
from io import BytesIO
from pydub import AudioSegment
import os
from router_interviews import router
from main import app

# OpenAI Configuration (replace with your API key)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.websocket("/ws/simulate-interview") # @router.websocket("/ws/simulate-interview")
async def interview_simulate(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            input_type = message.get("type")  # "text", "audio", or "transcript"
            content = message.get("content")  # Input content
            
            # Process user input
            if input_type == "audio":
                transcript = convert_audio_to_text(content)
                ai_response = get_ai_response(transcript)
                audio_response = convert_text_to_audio(ai_response)
                response = {
                    "type": "audio",
                    "content": audio_response,
                }
            elif input_type == "text":
                ai_response = get_ai_response(content)
                response = {
                    "type": "text",
                    "content": ai_response,
                }
            elif input_type == "transcript":
                ai_response = get_ai_response(content)
                response = {
                    "type": "transcript",
                    "content": ai_response,
                }
            else:
                response = {"error": "Invalid input type"}

            # Send response back to client
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        print("Client disconnected")

# Function to process text with AI
def get_ai_response(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are an HR interviewer."}, {"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"]



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
