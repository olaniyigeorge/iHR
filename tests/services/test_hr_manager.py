from datetime import datetime
from io import BytesIO
import pytest
from unittest.mock import patch, AsyncMock
from services.hr_manager import HRManager, AIResponse
from utils.schemas import InterviewContext

@pytest.mark.asyncio
async def test_updateScoreInsights():
    interview = InterviewContext(
        title="Test Interview",
        statements=["Hello, how are you?"],
        start_time="2024-11-30T10:53:24.864000",
        end_time="2024-12-01T10:53:24.864000"
    )
    new_response = "I am fine, thank you."

    with patch('services.hr_manager.ChatOpenAI') as MockChatOpenAI:
        mock_model = MockChatOpenAI.return_value
        mock_model.invoke.return_value = AIResponse(score=8.5, insights={"strengths": ["good communication"], "weaknesses": ["none"]})

        response = await HRManager.updateScoreInsights(interview, new_response)

        assert response.score == 8.5
        assert response.insights["strengths"] == ["good communication"]
        assert response.insights["weaknesses"] == ["none"]

@pytest.mark.asyncio
async def test_update_interview():
    ai_response = AIResponse(score=5, insights={"strengths": ["good knowledge"], "weaknesses": ["needs improvement in coding"]})

    with patch('services.hr_manager.crud.get_interview_by_id', new_callable=AsyncMock) as mock_get_interview_by_id, \
         patch('services.hr_manager.crud.update_interview', new_callable=AsyncMock) as mock_update_interview:
        
        mock_get_interview_by_id.return_value = AsyncMock(
            id=1,
            status="Ongoing",
            start_time=datetime(2024, 11, 30, 10, 53, 24),
            end_time=datetime(2024, 12, 1, 10, 53, 24),
            current_score=50,
            insights={"strengths": [], "weaknesses": []}
        )

        response = await HRManager.update_interview(1, ai_response)

        assert response["status"] == "Updated"
        assert response["interview"].current_score == 55
        assert response["interview"].insights["strengths"] == ["good knowledge"]
        assert response["interview"].insights["weaknesses"] == ["needs improvement in coding"]

@pytest.mark.asyncio
async def test_get_conversation_context():
    interview_id = 1

    with patch('services.hr_manager.redis_client.get') as mock_redis_get, \
         patch('services.hr_manager.redis_client.set') as mock_redis_set:
        
        mock_redis_get.return_value = None

        context = await HRManager.get_conversation_context(interview_id)

        assert context["id"] == interview_id
        assert context["job"]["title"] == "Junior Python Developer"
        mock_redis_set.assert_called_once()

@pytest.mark.asyncio
async def test_get_ai_response():
    prompt = "What are my responsibilities for this role?"
    interview_ctx = InterviewContext(
        title="Test Interview",
        statements=["Hello, how are you?"],
        start_time="2024-11-30T10:53:24.864000",
        end_time="2024-12-01T10:53:24.864000"
    )

    with patch('services.hr_manager.HRManager.get_ai_response', return_value="You will be responsible for...") as mock_get_ai_response:
        response = await HRManager.get_ai_response(prompt, interview_ctx)
        assert response == "You will be responsible for..."

def test_convert_audio_to_text():
    audio_data = b"fake audio data"

    with patch('services.hr_manager.Recognizer') as MockRecognizer, \
         patch('services.hr_manager.AudioFile') as MockAudioFile:
        
        mock_recognizer_instance = MockRecognizer.return_value
        mock_recognizer_instance.recognize_google.return_value = "This is a test."

        text = HRManager.convert_audio_to_text(audio_data)
        assert text == "This is a test."

def test_convert_text_to_audio():
    text = "This is a test."

    with patch('services.hr_manager.gTTS') as MockGTTS:
        mock_gtts_instance = MockGTTS.return_value
        mock_audio_buffer = BytesIO()
        mock_gtts_instance.write_to_fp.return_value = mock_audio_buffer

        audio_data = HRManager.convert_text_to_audio(text)
        assert isinstance(audio_data, bytes)