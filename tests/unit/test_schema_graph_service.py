import pytest
from unittest.mock import MagicMock, patch
from src.services.schema_graph_service import SchemaGraphService

@pytest.fixture
def mock_db_reader():
    reader = MagicMock()
    reader.get_tables.return_value = (["users"], ["user_view"])
    reader.get_table_schema.return_value = [{"Field": "id", "Type": "int", "Key": "PRI"}]
    reader.get_view_schema.return_value = [{"Field": "id", "Type": "int"}]
    reader.mysql_service.execute_query.return_value = []
    return reader

def test_schema_graph_service_init(mock_db_reader):
    service = SchemaGraphService(mock_db_reader, "ecommerce")
    assert service.dbname == "ecommerce"
    assert service.db_reader == mock_db_reader

def test_schema_graph_service_build_graph(mock_db_reader):
    service = SchemaGraphService(mock_db_reader, "ecommerce")
    graph = service.build_graph(enable_profiling=False)
    
    assert "users" in graph.node_properties
    assert "users.id" in graph.node_properties
    assert "user_view" in graph.node_properties
    
    # Check edges
    assert "users.id" in graph.graph["users"]
    assert "users" in graph.graph["users.id"]

@patch("src.services.schema_graph_service.SchemaGraphService.save")
def test_schema_graph_service_build_and_save(mock_save, mock_db_reader):
    service = SchemaGraphService(mock_db_reader, "ecommerce")
    service.build_and_save(enable_profiling=False)
    
    mock_save.assert_called_once()
