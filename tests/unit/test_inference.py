import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from src.services.inference import GeminiService, OpenAIService, OllamaService

# --- GeminiService Tests ---

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_gemini_service_async_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'candidates': [{'content': {'parts': [{'text': 'test response'}]}}]
    }
    mock_post.return_value = mock_response
    
    service = GeminiService(api_key="test_key")
    result = await service.chat_completion_async("hello")
    
    assert result == "test response"
    mock_post.assert_called_once()

@patch("requests.post")
def test_gemini_service_sync_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'candidates': [{'content': {'parts': [{'text': 'sync response'}]}}]
    }
    mock_post.return_value = mock_response
    
    service = GeminiService(api_key="test_key")
    result = service.chat_completion("hello")
    
    assert result == "sync response"

# --- OpenAIService Tests ---

@pytest.mark.asyncio
async def test_openai_service_async_success():
    mock_async_client = MagicMock()
    mock_async_client.chat.completions.create = AsyncMock()
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "openai response"
    mock_async_client.chat.completions.create.return_value = mock_response
    
    with patch("src.services.inference.AsyncOpenAI", return_value=mock_async_client):
        service = OpenAIService(api_key="test_key")
        result = await service.chat_completion_async("hello")
        
        assert result == "openai response"

# --- OllamaService Tests ---

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_ollama_service_async_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": {"content": "ollama response"}}
    mock_post.return_value = mock_response
    
    # Need to import OllamaService if it's defined in the file
    from src.services.inference import OllamaService
    service = OllamaService(model="llama2")
    result = await service.chat_completion_async("hello")
    
    assert result == "ollama response"
