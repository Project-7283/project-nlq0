import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import os

# Mock environment variables before importing the module
os.environ["OPENAI_API_KEY"] = "test-key"

@pytest.fixture
def mock_container():
    with patch("src.flows.nl_to_sql.container") as mock:
        yield mock

@pytest.fixture
def mock_services():
    mock_graph = MagicMock()
    mock_model = AsyncMock()
    mock_intent_analyzer = AsyncMock()
    mock_sql_generator = AsyncMock()
    
    with patch("src.flows.nl_to_sql.graph", mock_graph), \
         patch("src.flows.nl_to_sql.model", mock_model), \
         patch("src.flows.nl_to_sql.intent_analyzer", mock_intent_analyzer), \
         patch("src.flows.nl_to_sql.sql_generator", mock_sql_generator):
        yield mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator

@pytest.mark.asyncio
async def test_extract_intent(mock_services):
    mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator = mock_services
    mock_intent_analyzer.analyze_intent_async.return_value = {
        "start_node": ["customers"],
        "end_node": ["orders"],
        "condition": "id=1"
    }
    
    from src.flows.nl_to_sql import extract_intent
    state = {"user_query": "find orders for customer 1"}
    result = await extract_intent(state)
    
    assert result["start_node"] == ["customers"]
    assert result["condition"] == "id=1"
    mock_intent_analyzer.analyze_intent_async.assert_called_once()

@pytest.mark.asyncio
async def test_refine_query_as_analyst(mock_services):
    mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator = mock_services
    mock_graph.node_properties = {
        "customers": {"type": "table", "properties": {"description": "Customer data"}}
    }
    mock_model.chat_completion_async.return_value = "CLARIFIED QUERY: Show all orders for customer 1\nTABLES NEEDED: customers, orders\nNOTES: None"
    
    from src.flows.nl_to_sql import refine_query_as_analyst
    state = {"user_query": "orders for cust 1"}
    result = await refine_query_as_analyst(state)
    
    assert result["refined_query"] == "Show all orders for customer 1"
    assert "analyst_guidance" in result

def test_find_path(mock_services):
    mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator = mock_services
    mock_graph.find_path.return_value = (10, ["customers", "orders"], "walk")
    
    from src.flows.nl_to_sql import find_path
    state = {"start_node": ["customers"], "end_node": ["orders"]}
    result = find_path(state)
    
    assert result["path"] == ["customers", "orders"]

@pytest.mark.asyncio
async def test_generate_sql(mock_services):
    mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator = mock_services
    mock_sql_generator.generate_sql_async.return_value = "SELECT * FROM orders WHERE customer_id = 1"
    
    from src.flows.nl_to_sql import generate_sql
    state = {
        "user_query": "orders for customer 1",
        "path": ["customers", "orders"],
        "condition": "customer_id = 1"
    }
    result = await generate_sql(state)
    
    assert result["sql"] == "SELECT * FROM orders WHERE customer_id = 1"
    assert result["retries"] == 0
