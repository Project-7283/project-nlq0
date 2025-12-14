# SQL Generation Service

## Class: `SQLGenerationService`

**File:** `src/services/sql_generation_service.py`

### Description
This service handles the generation of SQL queries from a given semantic graph path and user query. It uses an LLM to construct the SQL and the `MySQLService` to execute it.

### Dependencies
*   `src.services.inference.InferenceServiceProtocol`: LLM interface.
*   `src.services.mysql_service.MySQLService`: Database execution service.
*   `src.modules.semantic_graph.SemanticGraph`: Graph structure.

### Key Methods

#### `path_to_sql_prompt(self, path: List[str], graph: SemanticGraph) -> str`
Constructs a detailed prompt for the LLM.

*   **Input:** A list of nodes representing the path and the graph object.
*   **Process:**
    *   Iterates through the path to describe edges (relationships) and conditions.
    *   Fetches schema details (columns) for the tables in the path.
    *   Combines this info into a prompt asking for a JSON response containing the SQL.

#### `generate_sql(self, path: List[str], graph: SemanticGraph, user_query: str = "") -> str`
Generates the SQL query.

*   **Process:**
    1.  Calls `path_to_sql_prompt` to get the base prompt.
    2.  Appends the user's natural language query.
    3.  Calls the LLM to get a structured JSON output.
    4.  Extracts and returns the SQL string.

#### `correct_sql(self, invalid_sql: str, error_message: str, user_query: str) -> str`
Attempts to fix a failed SQL query.

*   **Input:** The invalid SQL, the error message from the database, and the original user query.
*   **Process:**
    *   Constructs a prompt asking the LLM to fix the SQL based on the error.
    *   Returns the corrected SQL.

#### `run_sql(self, sql: str) -> List[Any]`
Executes the generated SQL using the underlying `MySQLService`.
