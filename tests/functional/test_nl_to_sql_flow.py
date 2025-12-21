import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import os

# Mock environment variables before importing the module
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["GEMINI_API_KEY"] = "test-key"

from src.flows.nl_to_sql import extract_intent, refine_query_as_analyst, find_path, generate_sql
from src.modules.semantic_graph import SemanticGraph

@pytest.fixture
def mock_services():
    mock_graph = SemanticGraph()
    # Add some nodes to the graph
    mock_graph.add_node("customers", node_type="table", properties={"description": "Customer table"})
    mock_graph.add_node("orders", node_type="table", properties={"description": "Orders table"})
    mock_graph.add_edge("customers", "orders", condition="foreign_key")
    
    mock_model = AsyncMock()
    mock_intent_analyzer = AsyncMock()
    mock_sql_generator = AsyncMock()
    
    with patch("src.flows.nl_to_sql.graph", mock_graph), \
         patch("src.flows.nl_to_sql.model", mock_model), \
         patch("src.flows.nl_to_sql.intent_analyzer", mock_intent_analyzer), \
         patch("src.flows.nl_to_sql.sql_generator", mock_sql_generator):
        yield mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator

@pytest.mark.asyncio
async def test_full_nl_to_sql_logic_flow(mock_services):
    """
    Functional test for the core logic flow of NL to SQL conversion.
    This tests the sequence of steps: Intent Extraction -> Refinement -> Path Finding -> SQL Generation.
    """
    mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator = mock_services
    
    # 1. Mock Intent Extraction
    mock_intent_analyzer.analyze_intent_async.return_value = {
        "start_node": ["customers"],
        "end_node": ["orders"],
        "condition": "customer email is 'test@example.com'"
    }
    
    # 2. Mock Analyst Refinement
    mock_model.chat_completion_async.return_value = "CLARIFIED QUERY: Find all orders for customer with email test@example.com\nTABLES NEEDED: customers, orders\nNOTES: Join on customer_id"
    
    # 3. Mock SQL Generation
    mock_sql_generator.generate_sql_async.return_value = "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE customers.email = 'test@example.com'"
    
    # Execute Flow
    state = {"user_query": "show me orders for test@example.com"}
    
    # Step 1: Refine
    state = await refine_query_as_analyst(state)
    assert state["refined_query"] == "Find all orders for customer with email test@example.com"
    
    # Step 2: Extract Intent
    state = await extract_intent(state)
    assert state["start_node"] == ["customers"]
    
    # Step 3: Find Path
    state = find_path(state)
    assert "customers" in state["path"]
    assert "orders" in state["path"]
    
    # Step 4: Generate SQL
    state = await generate_sql(state)
    assert "SELECT" in state["sql"]
    assert "orders" in state["sql"]
    assert "customers" in state["sql"]

@pytest.mark.asyncio
async def test_flow_with_no_path(mock_services):
    """Test flow when no path is found between nodes"""
    mock_graph, mock_model, mock_intent_analyzer, mock_sql_generator = mock_services
    
    # Add an isolated node
    mock_graph.add_node("products", node_type="table")
    
    mock_intent_analyzer.analyze_intent_async.return_value = {
        "start_node": ["customers"],
        "end_node": ["products"],
        "condition": ""
    }
    
    state = {
        "user_query": "customers and products",
        "start_node": ["customers"],
        "end_node": ["products"]
    }
    
    state = find_path(state)
    # Should fallback to just the start node or some default
    assert state["path"] == ["customers", "customers"]
