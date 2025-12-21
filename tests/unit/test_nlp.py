import pytest
from unittest.mock import MagicMock, AsyncMock
from src.services.nlp import NLQIntentAnalyzer

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.chat_completion.return_value = "Refined Query"
    model.chat_completion_async = AsyncMock(return_value="Refined Query Async")
    model.get_structured_output.return_value = {
        "start_node": "customers",
        "end_node": "orders",
        "condition": "customer_id = 1"
    }
    model.get_structured_output_async = AsyncMock(return_value={
        "start_node": "customers",
        "end_node": "orders",
        "condition": "customer_id = 1"
    })
    return model

@pytest.fixture
def mock_graph():
    graph = MagicMock()
    graph.get_node_details.return_value = {"node_type": "table", "properties": {}}
    return graph

def test_nlp_refine_intent(mock_model):
    analyzer = NLQIntentAnalyzer(model=mock_model)
    result = analyzer.refine_intent("test query")
    assert result == "Refined Query"
    mock_model.chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_nlp_refine_intent_async(mock_model):
    analyzer = NLQIntentAnalyzer(model=mock_model)
    result = await analyzer.refine_intent_async("test query")
    assert result == "Refined Query Async"
    mock_model.chat_completion_async.assert_called_once()

def test_nlp_analyze_intent(mock_model, mock_graph):
    analyzer = NLQIntentAnalyzer(model=mock_model)
    # Mock internal methods to avoid complex setup
    analyzer._get_context_nodes = MagicMock(return_value=["node1", "node2"])
    
    result = analyzer.analyze_intent("show orders for customer 1", mock_graph)
    
    assert result["start_node"] == ["customers"]
    assert result["end_node"] == ["orders"]
    assert result["condition"] == "customer_id = 1"

@pytest.mark.asyncio
async def test_nlp_analyze_intent_async(mock_model, mock_graph):
    analyzer = NLQIntentAnalyzer(model=mock_model)
    analyzer._get_context_nodes = MagicMock(return_value=["node1", "node2"])
    
    result = await analyzer.analyze_intent_async("show orders for customer 1", mock_graph)
    
    assert result["start_node"] == ["customers"]
    assert result["end_node"] == ["orders"]
    assert result["condition"] == "customer_id = 1"
    mock_model.get_structured_output_async.assert_called_once()

def test_nlp_get_context_nodes_with_vector(mock_model, mock_graph):
    mock_vector = MagicMock()
    mock_vector.search_nodes.return_value = ["customers", "orders"]
    
    analyzer = NLQIntentAnalyzer(model=mock_model, vector_service=mock_vector)
    nodes = analyzer._get_context_nodes("test query", mock_graph)
    
    assert len(nodes) == 2
    mock_vector.search_nodes.assert_called_once()

def test_nlp_format_node_context(mock_model, mock_graph):
    mock_graph.get_node_details.return_value = {
        "node_type": "table",
        "properties": {"description": "Table description", "business_purpose": "Purpose"}
    }
    
    analyzer = NLQIntentAnalyzer(model=mock_model)
    context = analyzer._format_node_context("customers", mock_graph)
    
    assert "customers (table)" in context
    assert "Table description" in context

def test_nlp_process_intent_result_invalid():
    analyzer = NLQIntentAnalyzer(model=MagicMock())
    assert analyzer._process_intent_result(None) is None
    assert analyzer._process_intent_result({}) is None
    assert analyzer._process_intent_result("invalid") is None

