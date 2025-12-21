import pytest
from unittest.mock import MagicMock, patch
from src.services.db_profiling_service import DBProfilingService, DataGovernanceConfig

def test_data_governance_config_defaults():
    config = DataGovernanceConfig()
    assert "password" in config.sensitive_keywords
    assert config.is_sensitive_column("user_password") is True
    assert config.is_sensitive_column("user_id") is False

@pytest.fixture
def mock_services():
    db_reader = MagicMock()
    mysql_service = MagicMock()
    light_llm = MagicMock()
    heavy_llm = MagicMock()
    return db_reader, mysql_service, light_llm, heavy_llm

def test_db_profiling_service_init(mock_services):
    db_reader, mysql_service, light_llm, heavy_llm = mock_services
    service = DBProfilingService(db_reader, mysql_service, light_llm, heavy_llm)
    assert service.db_reader == db_reader
    assert service.mysql_service == mysql_service

def test_db_profiling_service_get_table_stats(mock_services):
    db_reader, mysql_service, light_llm, heavy_llm = mock_services
    mysql_service.execute_query.return_value = [{"cnt": 100}]
    
    service = DBProfilingService(db_reader, mysql_service, light_llm, heavy_llm)
    count = service._get_row_count("ecommerce", "users")
    
    assert count == 100
    mysql_service.execute_query.assert_called_once()

def test_db_profiling_service_get_column_stats(mock_services):
    db_reader, mysql_service, light_llm, heavy_llm = mock_services
    # Mock for distinct count and null count
    mysql_service.execute_query.side_effect = [
        [{"cnt": 50}],
        [{"cnt": 5}]
    ]
    
    service = DBProfilingService(db_reader, mysql_service, light_llm, heavy_llm)
    distinct_count = service._get_distinct_count("ecommerce", "users", "status")
    null_percentage = service._get_null_percentage("ecommerce", "users", "status", 100)
    
    assert distinct_count == 50
    assert null_percentage == 5.0

def test_db_profiling_service_profile_table(mock_services):
    db_reader, mysql_service, light_llm, heavy_llm = mock_services
    
    db_reader.get_table_schema.return_value = [
        {"Field": "id", "Type": "int", "Comment": "PK"},
        {"Field": "name", "Type": "varchar(255)", "Comment": "User name"}
    ]
    mysql_service.execute_query.side_effect = [
        [{"cnt": 100}], # row count
        [{"cnt": 100}], # distinct id
        [{"cnt": 0}],   # null id
        [{"cnt": 90}],  # distinct name
        [{"cnt": 5}],   # null name
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}] # sample rows
    ]
    heavy_llm.get_structured_output.return_value = {
        "business_purpose": "User management",
        "description": "Stores user accounts"
    }
    light_llm.get_structured_output.return_value = {
        "id": {"description": "Unique ID"},
        "name": {"description": "Full name"}
    }
    
    service = DBProfilingService(db_reader, mysql_service, light_llm, heavy_llm)
    profile = service.profile_table("ecommerce", "users")
    
    assert profile["row_count"] == 100
    assert "columns" in profile
    assert profile["business_purpose"] == "User management"

def test_data_governance_config():
    from src.services.db_profiling_service import DataGovernanceConfig
    config = DataGovernanceConfig()
    assert config.is_sensitive_column("password") is True
    assert config.is_sensitive_column("user_id") is False
