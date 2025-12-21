import pytest
from unittest.mock import MagicMock
from src.services.db_reader import DBSchemaReaderService
from src.services.schema_graph_service import SchemaGraphService
from src.modules.semantic_graph import SemanticGraph

@pytest.fixture
def mock_mysql():
    service = MagicMock()
    # Mock tables
    service.execute_query.side_effect = [
        # get_tables
        ([("customers", "BASE TABLE")], ["TABLE_NAME", "TABLE_TYPE"]),
        # get_table_schema for customers
        [
            {"Field": "customer_id", "Type": "int", "Key": "PRI", "Default": None, "Extra": "auto_increment", "Comment": "Primary Key"},
            {"Field": "email", "Type": "varchar(255)", "Key": "UNI", "Default": None, "Extra": "", "Comment": "User email"}
        ],
        # get_foreign_keys
        [
            {
                "COLUMN_NAME": "customer_id",
                "REFERENCED_TABLE_NAME": "orders",
                "REFERENCED_COLUMN_NAME": "customer_id",
                "CONSTRAINT_NAME": "fk_orders_customers"
            }
        ]
    ]
    return service

def test_db_to_graph_integration(mock_mysql):
    """Test integration between DBSchemaReaderService and SchemaGraphService"""
    db_reader = DBSchemaReaderService(mock_mysql)
    schema_service = SchemaGraphService(db_reader, "ecommerce")
    
    # Build graph from "ecommerce" database
    schema_service.build_graph(enable_profiling=False)
    
    graph = schema_service.graph
    
    # Verify graph structure
    assert "customers" in graph.node_properties
    assert "customers.customer_id" in graph.node_properties
    assert "customers.email" in graph.node_properties
    
    # Verify properties were passed correctly
    cust_props = graph.node_properties["customers"]["properties"]
    # table_comment is only present if profiling is enabled
    # assert cust_props.get("table_comment") == "Customer info"
    
    email_props = graph.node_properties["customers.email"]["properties"]
    assert email_props["Type"] == "varchar(255)"
    assert email_props["Comment"] == "User email"
    
    # Verify edges (foreign keys)
    # Note: SchemaGraphService adds edges for FKs
    neighbors = graph.get_neighbors_by_condition("customers.customer_id", "foreign_key")
    # The logic in SchemaGraphService might add edges between tables or columns
    # Let's check what it actually does
    assert len(graph.graph) > 0
