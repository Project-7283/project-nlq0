import pytest
import time
import asyncio
from unittest.mock import MagicMock, patch
from src.utils.circuit_breaker import CircuitBreaker, CircuitState
from src.utils.container import Container
from src.utils.logging import setup_logger

# --- CircuitBreaker Tests ---

def test_circuit_breaker_sync_success():
    cb = CircuitBreaker(name="test_sync", failure_threshold=2)
    mock_func = MagicMock(return_value="success")
    
    result = cb.call_sync(mock_func)
    
    assert result == "success"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

def test_circuit_breaker_sync_failure():
    cb = CircuitBreaker(name="test_sync_fail", failure_threshold=2)
    mock_func = MagicMock(side_effect=ValueError("fail"))
    
    with pytest.raises(ValueError):
        cb.call_sync(mock_func)
    
    assert cb.failure_count == 1
    assert cb.state == CircuitState.CLOSED

    with pytest.raises(ValueError):
        cb.call_sync(mock_func)
    
    assert cb.failure_count == 2
    assert cb.state == CircuitState.OPEN

def test_circuit_breaker_open_rejection():
    cb = CircuitBreaker(name="test_open", failure_threshold=1)
    cb.state = CircuitState.OPEN
    cb.last_failure_time = time.time()
    
    mock_func = MagicMock()
    
    with pytest.raises(Exception) as excinfo:
        cb.call_sync(mock_func)
    
    assert "is OPEN" in str(excinfo.value)
    mock_func.assert_not_called()

@pytest.mark.asyncio
async def test_circuit_breaker_async_success():
    cb = CircuitBreaker(name="test_async", failure_threshold=2)
    
    async def mock_async_func():
        return "async_success"
    
    result = await cb.call_async(mock_async_func)
    
    assert result == "async_success"
    assert cb.state == CircuitState.CLOSED

# --- Container Tests ---

def test_container_singleton():
    c1 = Container.get_instance()
    c2 = Container.get_instance()
    assert c1 is c2

@patch.dict("os.environ", {"MYSQL_HOST": "localhost", "LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test"})
def test_container_config_loading():
    # Reset singleton for test
    Container._instance = None
    container = Container.get_instance()
    assert container.config["mysql_host"] == "localhost"
    assert container.config["llm_provider"] == "openai"

@patch.dict("os.environ", {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test"})
def test_container_inference_service_gemini():
    Container._instance = None
    container = Container.get_instance()
    with patch("src.services.inference.GeminiService") as mock_gemini:
        svc = container.get_inference_service()
        assert "inference" in container.services

@patch.dict("os.environ", {"LLM_PROVIDER": "ollama"})
def test_container_inference_service_ollama():
    Container._instance = None
    container = Container.get_instance()
    with patch("src.services.inference.OllamaService") as mock_ollama:
        svc = container.get_inference_service()
        assert "inference" in container.services

def test_container_get_services():
    Container._instance = None
    container = Container.get_instance()
    
    with patch("src.services.mysql_service.mysql.connector.connect"):
        with patch("src.modules.semantic_graph.SemanticGraph.load_from_json"):
            assert container.get_governance_service() is not None
            assert container.get_mysql_service() is not None
            assert container.get_semantic_graph() is not None
            assert container.get_vector_service() is not None
            
            with patch.object(container, 'get_inference_service'):
                assert container.get_intent_analyzer() is not None
                assert container.get_sql_generator() is not None

# --- Logging Tests ---

def test_setup_logger(tmp_path):
    log_file = tmp_path / "test.log"
    logger = setup_logger("test_logger", log_file=str(log_file))
    
    assert logger.name == "test_logger"
    assert len(logger.handlers) >= 1
    
    logger.info("test message")
    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "test message" in content
