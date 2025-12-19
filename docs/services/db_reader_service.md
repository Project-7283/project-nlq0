# DB Reader Service

## Class: `DBSchemaReaderService`

**File:** `src/services/db_reader.py`

### Description
A service designed to inspect the database metadata. It queries the database `information_schema` and system tables to retrieve information about tables, views, columns, and stored procedures.

### Dependencies
*   `src.services.mysql_service.MySQLService`: Used to execute metadata queries.

### Key Methods

#### `get_databases(self)`
Returns a list of available databases, excluding system databases.

#### `get_tables(self, database)`
Returns a list of base tables and views in the specified database.

#### `get_table_schema(self, database, table)`
Retrieves detailed column information (Field, Type, Key, etc.) for a specific table.

#### `get_view_schema(self, database, view)`
Retrieves the `CREATE VIEW` statement for a specific view.

#### `get_stored_procedures(self, database)`
Returns a list of stored procedure names.

#### `read_full_schema(self)`
Crawls the entire database server to build a nested dictionary representation of all databases, tables, views, and procedures.
