import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os

# Mock environment variables before importing app
os.environ["OPENAI_API_KEY"] = "test_key"
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_USER"] = "root"
os.environ["MYSQL_PASSWORD"] = "password"

# Mock mysql connector before importing app
with patch("mysql.connector.connect") as mock_connect:
    from fastapi.testclient import TestClient
    from src.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch("src.api.process_nl_query_async")
def test_query_endpoint_success(mock_process):
    mock_process.return_value = ("SELECT * FROM users", [{"id": 1, "name": "test"}])
    
    response = client.post("/query", json={"query": "show users"})
    
    assert response.status_code == 200
    assert response.json()["sql"] == "SELECT * FROM users"
    assert response.json()["results"] == [{"id": 1, "name": "test"}]
    mock_process.assert_called_once_with("show users")

def test_query_endpoint_missing_query():
    response = client.post("/query", json={})
    assert response.status_code == 400
    assert "Missing 'query' field" in response.json()["detail"]

@patch("src.api.process_nl_query_async")
def test_query_endpoint_error(mock_process):
    mock_process.side_effect = Exception("Internal error")
    
    response = client.post("/query", json={"query": "show users"})
    
    assert response.status_code == 500
    assert response.json()["error"] == "Internal error"
