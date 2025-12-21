import pytest
from unittest.mock import MagicMock, patch
from src.services.mysql_service import MySQLService, SecurityError

@pytest.fixture
def mock_mysql_conn():
    with patch("mysql.connector.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn

def test_mysql_service_init(mock_mysql_conn):
    service = MySQLService(host="h", user="u", password="p", database="d")
    assert service.db_config["host"] == "h"
    mock_mysql_conn.cursor.assert_not_called()

def test_mysql_service_execute_sync_success(mock_mysql_conn):
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
    
    service = MySQLService(host="h", user="u", password="p", database="d")
    # Disable governance for simple test
    service.governance_enabled = False
    
    result = service.execute_query("SELECT * FROM users")
    
    assert result == [{"id": 1, "name": "test"}]
    mock_cursor.execute.assert_called_with("SELECT * FROM users")

def test_mysql_service_governance_block(mock_mysql_conn):
    mock_gov = MagicMock()
    mock_gov.validate_query.return_value = (False, "Blocked by policy")
    
    service = MySQLService(host="h", user="u", password="p", database="d", governance_service=mock_gov)
    service.governance_enabled = True
    
    with pytest.raises(SecurityError) as excinfo:
        service.execute_query("DROP TABLE users")
    
    assert "Blocked by policy" in str(excinfo.value)

@pytest.mark.asyncio
async def test_mysql_service_execute_async(mock_mysql_conn):
    mock_cursor = MagicMock()
    mock_mysql_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{"id": 1}]
    
    service = MySQLService(host="h", user="u", password="p", database="d")
    service.governance_enabled = False
    
    result = await service.execute_query_async("SELECT 1")
    assert result == [{"id": 1}]
