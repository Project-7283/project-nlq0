import pytest
import os
from unittest.mock import MagicMock
from src.services.data_governance_service import DataGovernanceService
from src.services.db_profiling_service import DBProfilingService

@pytest.fixture(autouse=True)
def setup_governance_env():
    """Ensure governance is enabled for security tests"""
    os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
    os.environ["DATA_GOVERNANCE_STRICT_MODE"] = "true"
    yield

def test_sql_injection_detection():
    """Test that the governance service detects common SQL injection patterns"""
    service = DataGovernanceService()
    
    # Test blocking of sensitive columns
    sql = "SELECT password, username FROM users"
    is_valid, error = service.validate_query(sql)
    assert is_valid is False
    assert "blocked" in error.lower()
    assert "password" in error

    # Test blocking of SELECT * in strict mode
    sql = "SELECT * FROM users"
    # We need schema context for this to trigger in the current implementation
    schema_context = {"users": {"columns": ["id", "username", "password"]}}
    is_valid, error = service.validate_query(sql, schema_context)
    assert is_valid is False
    assert "SELECT *" in error

def test_sql_sanitization():
    """Test that SQL is correctly sanitized by masking sensitive columns"""
    service = DataGovernanceService()
    
    sql = "SELECT username, password, email FROM users"
    sanitized = service.sanitize_sql(sql)
    
    assert "username" in sanitized
    assert "'***MASKED***' AS password" in sanitized
    # email is a partial mask column, so it shouldn't be fully masked by sanitize_sql 
    # (based on current implementation of is_sensitive_column)
    assert "email" in sanitized 

def test_result_masking():
    """Test that query results are masked correctly"""
    service = DataGovernanceService()
    
    results = [
        {"username": "admin", "password": "123", "email": "admin@example.com", "phone": "555-1234"}
    ]
    
    masked = service.mask_results(results)
    
    assert masked[0]["username"] == "admin"
    assert masked[0]["password"] == "***MASKED***"
    assert masked[0]["email"] == "a***@example.com"
    assert "555" in masked[0]["phone"] # Partial mask keeps some info
    assert "***" in masked[0]["phone"]

def test_governance_masking_in_profiling():
    """Test that DBProfilingService masks sensitive data in sample rows"""
    db_reader = MagicMock()
    mysql_service = MagicMock()
    llm = MagicMock()
    governance = DataGovernanceService()
    
    # Mock columns where one is sensitive
    columns = [
        {"Field": "username", "Type": "varchar"},
        {"Field": "password", "Type": "varchar"}
    ]
    
    # Mock real data - if governance works, it will generate SQL that returns masked values
    def side_effect(query, params=None):
        if "'***MASKED***' AS `password`" in query:
            return [{"username": "admin", "password": "***MASKED***"}]
        return [{"username": "admin", "password": "supersecret123"}]
        
    mysql_service.execute_query.side_effect = side_effect
    
    service = DBProfilingService(db_reader, mysql_service, llm, governance)
    
    # Call internal _get_sample_rows
    samples = service._get_sample_rows("db", "users", columns, limit=1)
    
    assert len(samples) == 1
    assert samples[0]["username"] == "admin"
    assert samples[0]["password"] == "***MASKED***"
    
    # Verify the query actually contained the mask
    args, _ = mysql_service.execute_query.call_args
    query = args[0]
    assert "'***MASKED***' AS `password`" in query
