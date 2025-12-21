import pytest
from unittest.mock import MagicMock, patch
from src.services.vector_service import GraphVectorService

@pytest.fixture
def mock_chroma():
    with patch("chromadb.PersistentClient") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_collection = MagicMock()
        mock_instance.get_or_create_collection.return_value = mock_collection
        yield mock_instance, mock_collection

def test_vector_service_init(mock_chroma):
    mock_instance, mock_collection = mock_chroma
    service = GraphVectorService()
    assert service.client == mock_instance
    assert service.collection == mock_collection

def test_vector_service_create_rich_document():
    with patch("chromadb.PersistentClient"):
        service = GraphVectorService()
        
        # Test table document
        doc = service._create_rich_document("users", "table", {"description": "User table", "row_count": 100})
        assert "Table: users" in doc
        assert "Description: User table" in doc
        assert "Row Count: 100" in doc
        
        # Test column document
        doc = service._create_rich_document("users.email", "attribute", {"Type": "varchar", "description": "User email"})
        assert "Column: email in table users" in doc
        assert "Type: varchar" in doc
        assert "Description: User email" in doc

def test_vector_service_search(mock_chroma):
    mock_instance, mock_collection = mock_chroma
    mock_collection.query.return_value = {
        "ids": [["id1", "id2"]],
        "distances": [[0.1, 0.2]],
        "metadatas": [[{"node_id": "id1", "type": "table"}, {"node_id": "id2", "type": "attribute"}]]
    }
    
    service = GraphVectorService()
    results = service.search_nodes("find users", k=2)
    
    assert len(results) == 2
    assert results[0] == "id1"
    assert results[1] == "id2"
    mock_collection.query.assert_called_once()

def test_vector_service_format_documents():
    service = GraphVectorService()
    
    # Test table document
    table_doc = service._create_rich_document("users", "table", {"description": "User data", "business_purpose": "Auth"})
    assert "Table: users" in table_doc
    assert "Description: User data" in table_doc
    
    # Test column document
    col_doc = service._create_rich_document("users.id", "attribute", {"Type": "int", "description": "Primary key"})
    assert "Column: id in table users" in col_doc
    assert "Type: int" in col_doc
    
    # Test view document
    view_doc = service._create_rich_document("active_users", "view", {"description": "Active users view"})
    assert "View: active_users" in view_doc

def test_vector_service_index_graph(mock_chroma):
    mock_instance, mock_collection = mock_chroma
    service = GraphVectorService()
    
    mock_graph = MagicMock()
    mock_graph.node_properties = {
        "users": {"type": "table", "properties": {"description": "User table"}},
        "users.id": {"type": "attribute", "properties": {"Type": "int"}}
    }
    
    service.index_graph(mock_graph)
    
    assert mock_collection.upsert.called
    args, kwargs = mock_collection.upsert.call_args
    assert "users" in kwargs["ids"]
    assert "users.id" in kwargs["ids"]
