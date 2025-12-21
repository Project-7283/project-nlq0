import pytest
from unittest.mock import MagicMock
from src.services.db_reader import DBSchemaReaderService

@pytest.fixture
def mock_mysql():
    return MagicMock()

def test_db_reader_get_databases(mock_mysql):
    mock_mysql.execute_query.return_value = ([("db1",), ("information_schema",), ("db2",)], ["Database"])
    
    reader = DBSchemaReaderService(mock_mysql)
    dbs = reader.get_databases()
    
    assert dbs == ["db1", "db2"]
    mock_mysql.execute_query.assert_called_once()

def test_db_reader_get_tables(mock_mysql):
    mock_mysql.execute_query.return_value = ([("t1", "BASE TABLE"), ("v1", "VIEW")], ["Table", "Type"])
    
    reader = DBSchemaReaderService(mock_mysql)
    tables, views = reader.get_tables("db1")
    
    assert tables == ["t1"]
    assert views == ["v1"]

def test_db_reader_get_table_schema(mock_mysql):
    mock_mysql.execute_query.return_value = [{"Field": "id", "Type": "int"}]
    
    reader = DBSchemaReaderService(mock_mysql)
    schema = reader.get_table_schema("db1", "t1")
    
    assert schema == [{"Field": "id", "Type": "int"}]

def test_db_reader_get_view_schema(mock_mysql):
    mock_mysql.execute_query.return_value = [{"Create View": "CREATE VIEW..."}]
    
    reader = DBSchemaReaderService(mock_mysql)
    schema = reader.get_view_schema("db1", "v1")
    
    assert schema == {"Create View": "CREATE VIEW..."}
