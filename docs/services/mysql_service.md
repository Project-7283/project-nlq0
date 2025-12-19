# MySQL Service

## Class: `MySQLService`

**File:** `src/services/mysql_service.py`

### Description
A wrapper class for managing MySQL database connections and executing queries. It handles connection establishment using environment variables and provides methods for fetching data.

### Configuration
Requires the following environment variables (loaded via `.env`):
*   `MYSQL_HOST`
*   `MYSQL_USER`
*   `MYSQL_PASSWORD`
*   `MYSQL_DATABASE`

### Key Methods

#### `__init__(self, host=None, user=None, password=None, database=None)`
Initializes the connection. Can override environment variables with direct arguments.

#### `execute_query(self, sql: str, asDict = True)`
Executes a SQL query and returns the results.

*   **Parameters:**
    *   `sql`: The SQL query string.
    *   `asDict`: If `True` (default), returns results as a list of dictionaries (column name -> value). If `False`, returns a tuple of `(results, headers)`.
*   **Returns:** List of rows (dicts or tuples).

#### `run_sql(self, sql)`
Executes a SQL query using `conn.info_query`. (Note: This seems to be a specific wrapper or alias, potentially for non-fetching queries or getting execution info).

#### `shutdown(self)`
Closes the database connection.
