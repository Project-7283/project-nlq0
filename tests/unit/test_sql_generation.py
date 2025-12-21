import pytest
from unittest.mock import MagicMock, AsyncMock
from src.services.sql_generation_service import SQLGenerationService

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.chat_completion.return_value = "SELECT * FROM customers"
    model.chat_completion_async = AsyncMock(return_value="SELECT * FROM customers")
    model.get_structured_output.return_value = {"sql": "SELECT * FROM customers"}
    model.get_structured_output_async = AsyncMock(return_value={"sql": "SELECT * FROM customers"})
    return model

@pytest.fixture
def mock_sql_service():
    service = MagicMock()
    service.execute_query.return_value = [{"id": 1}]
    service.execute_query_async = AsyncMock(return_value=[{"id": 1}])
    return service

@pytest.fixture
def mock_graph():
    graph = MagicMock()
    graph.get_node_details.return_value = {"node_type": "table", "properties": {}}
    graph.get_edge_details.return_value = {"condition": "id=id"}
    graph.get_neighbors_by_condition.return_value = {}
    return graph

def test_sql_gen_generate_sql(mock_model, mock_sql_service, mock_graph):
    service = SQLGenerationService(model=mock_model, sql_service=mock_sql_service)
    
    # Mock internal prompt generation
    service.path_to_sql_prompt = MagicMock(return_value="Prompt")
    
    sql = service.generate_sql(["customers", "orders"], mock_graph, "show orders")
    
    assert sql == "SELECT * FROM customers"
    mock_model.get_structured_output.assert_called_once()

@pytest.mark.asyncio
async def test_sql_gen_generate_sql_async(mock_model, mock_sql_service, mock_graph):
    service = SQLGenerationService(model=mock_model, sql_service=mock_sql_service)
    service.path_to_sql_prompt = MagicMock(return_value="Prompt")
    
    sql = await service.generate_sql_async(["customers", "orders"], mock_graph, "show orders")
    
    assert sql == "SELECT * FROM customers"
    mock_model.get_structured_output_async.assert_called_once()

def test_sql_gen_run_sql(mock_sql_service):
    service = SQLGenerationService(model=MagicMock(), sql_service=mock_sql_service)
    result = service.run_sql("SELECT * FROM customers")
    assert result == [{"id": 1}]
    mock_sql_service.execute_query.assert_called_once()

@pytest.mark.asyncio
async def test_sql_gen_run_sql_async(mock_sql_service):
    service = SQLGenerationService(model=MagicMock(), sql_service=mock_sql_service)
    result = await service.run_sql_async("SELECT * FROM customers")
    assert result == [{"id": 1}]
    mock_sql_service.execute_query_async.assert_called_once()

def test_sql_gen_path_to_sql_prompt(mock_graph):
    service = SQLGenerationService(model=MagicMock(), sql_service=MagicMock())
    mock_graph.get_node_details.side_effect = [
        {"node_type": "table", "properties": {"description": "Customers"}},
        {"node_type": "table", "properties": {"description": "Orders"}}
    ]
    mock_graph.get_edge_details.return_value = {"condition": "c.id = o.customer_id", "properties": {}}
    mock_graph.get_neighbors_by_condition.return_value = {}
    
    prompt = service.path_to_sql_prompt(["customers", "orders"], mock_graph)
    
    assert "customers" in prompt
    assert "orders" in prompt
    assert "c.id = o.customer_id" in prompt

def test_sql_gen_format_properties():
    service = SQLGenerationService(model=MagicMock(), sql_service=MagicMock())
    props = {
        "description": "Test desc",
        "Type": "int",
        "is_categorical": True,
        "sample_values": [1, 2, 3],
        "nested": {"a": 1, "b": 2}
    }
    formatted = service._format_properties(props)
    assert "Test desc" in formatted
    assert "int" in formatted
    assert "1, 2, 3" in formatted
    assert "nested" in formatted
