````markdown
# Database Service Protocols and Interchangeability

**File:** `src/services/database_protocols.py`

## Overview
This document defines abstract protocols for database services that enable seamless interchangeability between different database systems (MySQL, Azure Log Analytics, and others).

## Philosophy
The service architecture follows the **Protocol Pattern** from Python's `typing` module, allowing any database implementation to be swapped with another without changing client code. This enables:

1. **Flexible Multi-Database Support**: Switch between MySQL, Azure Log Analytics, PostgreSQL, etc.
2. **Unified NLQ Pipeline**: Single NLQ→SQL/KQL generation and execution pipeline
3. **Testability**: Mock database services for unit testing
4. **Future-Proofing**: Add new database connectors without modifying existing code

## Three Core Protocols

### 1. DatabaseExecutionProtocol
Protocol for executing queries and managing connections.

**Implementations:**
- `MySQLService` (SQL against MySQL)
- `AzureLogAnalyticsService` (KQL against Azure Log Analytics)

**Key Methods:**

\`\`\`python
def execute_query(
    sql: str,
    asDict: bool = True,
    schema_context: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """Execute query and return results as dicts"""

async def execute_query_async(
    sql: str,
    asDict: bool = True,
    schema_context: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """Async query execution"""

def shutdown() -> None:
    """Close connection and cleanup"""
\`\`\`

**Governance Integration:**
Both implementations integrate with `DataGovernanceService`:
- Query validation before execution
- Result masking for sensitive columns
- Audit logging of all operations

### 2. DatabaseReaderProtocol
Protocol for schema discovery and metadata retrieval.

**Implementations:**
- `DBSchemaReaderService` (MySQL information_schema)
- `AzureLogAnalyticsSchemaReader` (KQL metadata queries)

**Key Methods:**

\`\`\`python
def get_databases() -> List[str]:
    """List databases/workspaces"""

def get_tables(database: str) -> Tuple[List[str], List[str]]:
    """Return (tables, views) lists"""

def get_table_schema(database: str, table: str) -> List[Dict[str, Any]]:
    """Column definitions with types"""

def get_view_schema(database: str, view: str) -> Dict[str, Any]:
    """View definition metadata"""

def get_views(database: str) -> List[str]:
    """List views/saved queries"""

def get_stored_procedures(database: str) -> List[str]:
    """List procedures/functions"""

def read_full_schema() -> Dict[str, Any]:
    """Hierarchical schema for all databases"""
\`\`\`

### 3. DatabaseProfilingServiceProtocol
Protocol for table profiling with statistics and semantics.

**Implementations:**
- `DBProfilingService` (MySQL profiling)
- `AzureLogAnalyticsProfilingService` (Azure Log Analytics profiling)

**Key Methods:**

\`\`\`python
def profile_database(dbname: str) -> Dict[str, Any]:
    """Profile entire database with statistics and business context"""

def profile_table(dbname: str, table: str) -> Dict[str, Any]:
    """Profile single table with column statistics"""
\`\`\`

**Output Format:**
Both return JSON with:
- Row counts and cardinality
- Column types and statistics
- Masked sample data
- LLM-generated business descriptions
- Virtual table suggestions

## Interchangeability Examples

### Example 1: Query Execution
\`\`\`python
from src.services.database_protocols import DatabaseExecutionProtocol

# Can use either MySQL or Azure Log Analytics service
def execute_nlq_query(
    db_service: DatabaseExecutionProtocol,
    query_string: str
) -> List[Dict[str, Any]]:
    # Implementation works with any conforming service
    return db_service.execute_query(query_string)

# Usage - seamless switching
mysql_service = MySQLService(...)
azure_service = AzureLogAnalyticsService(...)

results = execute_nlq_query(mysql_service, "SELECT * FROM users")
results = execute_nlq_query(azure_service, "SecurityEvent | limit 100")
\`\`\`

### Example 2: Schema Discovery
\`\`\`python
from src.services.database_protocols import DatabaseReaderProtocol

def build_semantic_graph(
    reader: DatabaseReaderProtocol
) -> Dict[str, Any]:
    schema = reader.read_full_schema()
    # Build semantic graph from schema
    return semantic_graph

# Usage - works with both
mysql_reader = DBSchemaReaderService(mysql_service)
azure_reader = AzureLogAnalyticsSchemaReader(azure_service)

graph1 = build_semantic_graph(mysql_reader)
graph2 = build_semantic_graph(azure_reader)
\`\`\`

### Example 3: Table Profiling
\`\`\`python
from src.services.database_protocols import DatabaseProfilingServiceProtocol

def create_embedding_context(
    profiler: DatabaseProfilingServiceProtocol,
    database: str
) -> Dict[str, Any]:
    profile = profiler.profile_database(database)
    # Generate embeddings from profile
    return embeddings

# Usage - unified profiling
mysql_profiler = DBProfilingService(
    db_reader=mysql_reader,
    mysql_service=mysql_service,
    light_llm=llm_light,
    heavy_llm=llm_heavy
)

azure_profiler = AzureLogAnalyticsProfilingService(
    azure_reader=azure_reader,
    azure_service=azure_service,
    light_llm=llm_light,
    heavy_llm=llm_heavy
)

embeddings1 = create_embedding_context(mysql_profiler, "mydb")
embeddings2 = create_embedding_context(azure_profiler, "workspace-id")
\`\`\`

## Implementation Checklist

To create a new database service that conforms to these protocols:

### For DatabaseExecutionProtocol:
- [ ] Implement `execute_query(sql, asDict, schema_context)`
- [ ] Implement `execute_query_async(sql, asDict, schema_context)`
- [ ] Implement `shutdown()`
- [ ] Support governance hooks (validation + masking)
- [ ] Implement audit logging
- [ ] Handle async/await properly

### For DatabaseReaderProtocol:
- [ ] Implement `get_databases()`
- [ ] Implement `get_tables(database)`
- [ ] Implement `get_table_schema(database, table)`
- [ ] Implement `get_view_schema(database, view)`
- [ ] Implement `get_views(database)`
- [ ] Implement `get_stored_procedures(database)`
- [ ] Implement `read_full_schema()`
- [ ] Implement schema caching where appropriate
- [ ] Filter system objects appropriately

### For DatabaseProfilingServiceProtocol:
- [ ] Implement `profile_database(dbname)`
- [ ] Implement `profile_table(dbname, table)`
- [ ] Collect statistics (row counts, cardinality, types)
- [ ] Support masked sample retrieval
- [ ] Integrate LLM services for semantic analysis
- [ ] Support data governance masking
- [ ] Implement debug logging/dumps
- [ ] Return standardized JSON profile format

## Mapping Concepts Across Systems

| Concept | MySQL | Azure Log Analytics | PostgreSQL |
|---------|-------|---------------------|------------|
| Database | `SHOW DATABASES` | Workspace | `\\l` |
| Table | `SHOW TABLES` | Tables (KQL union) | `\\dt` |
| Column | `SHOW COLUMNS` | Fields (limit 0) | `\\d table` |
| Row Count | `COUNT(*)` | `\| count()` | `COUNT(*)` |
| Distinct | `DISTINCT` | `\| dcount()` | `DISTINCT` |
| Type Info | COLUMN_TYPE | KQL inference | data_type |
| Sample | `LIMIT N` | `\| limit N` | `LIMIT N` |
| Masking | SQL CASE | KQL evaluate | SQL CASE |

## Query Language Transformation

The NLQ pipeline must adapt queries to each database:

\`\`\`python
def generate_database_query(
    nlq: str,
    database_type: str,  # "mysql" or "azure_log_analytics"
    schema: Dict[str, Any]
) -> str:
    if database_type == "mysql":
        # Generate SQL
        return sql_generation_service.generate_sql(nlq, schema)
    elif database_type == "azure_log_analytics":
        # Generate KQL
        return kql_generation_service.generate_kql(nlq, schema)
    else:
        raise ValueError(f"Unknown database type: {database_type}")
\`\`\`

## Error Handling

All implementations must raise:
- `SecurityError` - When governance policies block query
- `Exception` - For connection, syntax, or execution errors

\`\`\`python
try:
    results = db_service.execute_query(query)
except SecurityError as e:
    # Query violated governance policy
    logger.warning(f"Query blocked: {e}")
    return []
except Exception as e:
    # Connection or execution error
    logger.error(f"Query failed: {e}")
    raise
\`\`\`

## Performance Considerations

### DatabaseExecutionProtocol
- Sync execution: Use for simple, fast queries
- Async execution: Use for batch operations or timeouts

### DatabaseReaderProtocol
- Implement caching to reduce repeated metadata queries
- Use `clear_cache()` when schema is known to have changed
- Consider lazy-loading for large schemas

### DatabaseProfilingServiceProtocol
- Profiling is expensive (multiple queries per table)
- Cache profile results and refresh periodically
- Use configurable sample sizes and time windows
- Support incremental profiling (profile subset of tables)

## Future Extensions

This protocol framework supports:
1. **Multi-Database Queries**: Join data across MySQL and Azure LA
2. **Query Routing**: Route NLQ to appropriate database based on keywords
3. **Federated Search**: Search across multiple database instances
4. **Synthetic Data**: Mock implementations for testing
5. **Alternative Databases**: PostgreSQL, MongoDB, Snowflake, etc.
````
