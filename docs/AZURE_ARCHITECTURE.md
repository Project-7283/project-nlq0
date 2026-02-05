# Azure Log Analytics Services - Architecture & Mapping

## Service Architecture Comparison

### MySQL Service Stack

```
┌──────────────────────────────────────┐
│   NLQ Pipeline Layer                 │
│   (SQL Generation, Execution)        │
├──────────────────────────────────────┤
│   MySQLService                       │
│   ├─ execute_query()                 │
│   ├─ execute_query_async()           │
│   └─ shutdown()                      │
├──────────────────────────────────────┤
│   DBSchemaReaderService              │
│   ├─ get_databases()                 │
│   ├─ get_tables()                    │
│   ├─ get_table_schema()              │
│   └─ read_full_schema()              │
├──────────────────────────────────────┤
│   DBProfilingService                 │
│   ├─ profile_database()              │
│   └─ profile_table()                 │
├──────────────────────────────────────┤
│   DataGovernanceService              │
│   ├─ validate_query()                │
│   └─ mask_results()                  │
├──────────────────────────────────────┤
│   MySQL Connector                    │
│   (Python mysql-connector-python)    │
└──────────────────────────────────────┘
```

### Azure Log Analytics Service Stack

```
┌──────────────────────────────────────┐
│   NLQ Pipeline Layer                 │
│   (KQL Generation, Execution)        │
├──────────────────────────────────────┤
│   AzureLogAnalyticsService           │
│   ├─ execute_query()                 │
│   ├─ execute_query_async()           │
│   └─ shutdown()                      │
├──────────────────────────────────────┤
│   AzureLogAnalyticsSchemaReader      │
│   ├─ get_databases()                 │
│   ├─ get_tables()                    │
│   ├─ get_table_schema()              │
│   └─ read_full_schema()              │
├──────────────────────────────────────┤
│   AzureLogAnalyticsProfilingService  │
│   ├─ profile_database()              │
│   └─ profile_table()                 │
├──────────────────────────────────────┤
│   DataGovernanceService/Config       │
│   ├─ validate_query()                │
│   └─ mask_results()                  │
├──────────────────────────────────────┤
│   Azure Monitor Query Client         │
│   (Python azure-monitor-query SDK)   │
└──────────────────────────────────────┘
```

## Interface Compatibility Matrix

| Interface | MySQLService | AzureLogAnalyticsService | Compatible |
|---|---|---|---|
| `execute_query(sql, asDict, schema_context)` | ✅ SQL queries | ✅ KQL queries | ✅ Yes |
| `execute_query_async(...)` | ✅ Async support | ✅ Async support | ✅ Yes |
| `shutdown()` | ✅ Close conn | ✅ Close client | ✅ Yes |
| Error handling | ✅ SecurityError | ✅ SecurityError | ✅ Yes |
| Governance integration | ✅ Yes | ✅ Yes | ✅ Yes |

| Interface | DBSchemaReaderService | AzureLogAnalyticsSchemaReader | Compatible |
|---|---|---|---|
| `get_databases()` | ✅ SHOW DATABASES | ✅ List workspaces | ✅ Yes |
| `get_tables(db)` | ✅ SHOW TABLES | ✅ KQL union query | ✅ Yes |
| `get_table_schema(db, table)` | ✅ SHOW COLUMNS | ✅ KQL limit 0 | ✅ Yes |
| `get_view_schema(db, view)` | ✅ SHOW VIEW | ✅ ARM API metadata | ✅ Yes |
| `get_views(db)` | ✅ List views | ✅ List saved queries | ✅ Yes |
| `get_stored_procedures(db)` | ✅ List procedures | ✅ Return empty | ✅ Yes |
| `read_full_schema()` | ✅ Full introspection | ✅ Full introspection | ✅ Yes |
| Schema caching | ✅ Optional | ✅ Implemented | ✅ Yes |

| Interface | DBProfilingService | AzureLogAnalyticsProfilingService | Compatible |
|---|---|---|---|
| `profile_database(dbname)` | ✅ SQL stats | ✅ KQL stats | ✅ Yes |
| `profile_table(db, table)` | ✅ Column stats | ✅ Column stats | ✅ Yes |
| Row count stats | ✅ COUNT(*) | ✅ \| count() | ✅ Yes |
| Cardinality | ✅ DISTINCT | ✅ \| dcount() | ✅ Yes |
| Sample retrieval | ✅ LIMIT N | ✅ \| limit N | ✅ Yes |
| LLM integration | ✅ Light + Heavy | ✅ Light + Heavy | ✅ Yes |
| Data masking | ✅ SQL CASE | ✅ KQL evaluate | ✅ Yes |
| Output format | ✅ JSON profile | ✅ JSON profile | ✅ Yes |

## Data Flow Comparison

### MySQL Data Flow

```
User NLQ Query
      ↓
[SQL Generation Service]
      ↓
SQL Query String
      ↓
[Data Governance Service] → Validate query
      ↓
[MySQLService] → Execute query
      ↓
Result Set
      ↓
[Data Governance Service] → Mask sensitive columns
      ↓
Final Results to User
```

### Azure Log Analytics Data Flow

```
User NLQ Query
      ↓
[KQL Generation Service]  ← Same pipeline, different LLM prompt
      ↓
KQL Query String
      ↓
[Data Governance Service] → Validate query
      ↓
[AzureLogAnalyticsService] → Execute KQL
      ↓
Result Set (Azure Table format)
      ↓
[Data Governance Service] → Mask sensitive columns
      ↓
Final Results to User
```

## Method Mapping

### Query Execution

| Task | MySQL | Azure Log Analytics |
|---|---|---|
| Execute query | `mysql_service.execute_query(sql)` | `azure_service.execute_query(kql)` |
| Async execute | `mysql_service.execute_query_async(sql)` | `azure_service.execute_query_async(kql)` |
| Cleanup | `mysql_service.shutdown()` | `azure_service.shutdown()` |

### Schema Discovery

| Task | MySQL | Azure Log Analytics |
|---|---|---|
| List databases | `mysql_reader.get_databases()` | `azure_reader.get_databases()` |
| List tables | `mysql_reader.get_tables(db)` | `azure_reader.get_tables(ws)` |
| Get column info | `mysql_reader.get_table_schema(db, tbl)` | `azure_reader.get_table_schema(ws, tbl)` |
| Full schema | `mysql_reader.read_full_schema()` | `azure_reader.read_full_schema()` |
| View definition | `mysql_reader.get_view_schema(db, v)` | `azure_reader.get_view_schema(ws, v)` |
| List procedures | `mysql_reader.get_stored_procedures(db)` | `azure_reader.get_stored_procedures(ws)` |

### Table Profiling

| Task | MySQL | Azure Log Analytics |
|---|---|---|
| Profile database | `mysql_profiler.profile_database(db)` | `azure_profiler.profile_database(ws)` |
| Profile table | `mysql_profiler.profile_table(db, tbl)` | `azure_profiler.profile_table(ws, tbl)` |

## Concept Mapping

### Database vs Workspace

```
MySQL: Database
  ├─ Tables
  │  ├─ Columns
  │  └─ Indexes
  ├─ Views
  └─ Stored Procedures

Azure Log Analytics: Workspace
  ├─ Tables (built-in + custom)
  │  ├─ Fields (columns)
  │  └─ Implicit indexing
  ├─ Saved Queries (views)
  └─ Analytics Rules/Functions
```

### Column Type Mapping

| SQL Type | Azure KQL Type | Mapping |
|---|---|---|
| TINYINT | long | Integer types |
| INT | long | Integer types |
| BIGINT | long | Integer types |
| FLOAT | real | Floating point |
| DECIMAL | real | Floating point |
| VARCHAR | string | String types |
| TEXT | string | String types |
| DATETIME | datetime | Temporal |
| BOOLEAN | bool | Boolean |
| JSON | dynamic | Complex/nested |
| BLOB | dynamic | Complex/nested |

## Governance & Security Alignment

### Data Governance Service Integration

```
Both MySQL and Azure services use same DataGovernanceService:

Query Validation Flow:
1. Load sensitive keywords from CSV
2. Check if query accesses sensitive columns
3. Block if violated (raise SecurityError)
4. Execute if valid

Result Masking Flow:
1. Execute query
2. Check each column name against sensitive keywords
3. Replace sensitive values with "***MASKED***"
4. Return masked results
```

### Governance Configuration

```bash
# Same configuration works for both
SENSITIVE_COLUMNS_CSV=config/sensitive_keywords.csv
DATA_GOVERNANCE_ENABLED=true
DATA_MASKING_ENABLED=true

# Sensitive keywords:
password, ssn, credit_card, api_key, token,
secret, hash, private_key, salt, cvv, pin, auth,
credential, key, bearer, etc.
```

## Error Handling Alignment

### Both Services Raise Same Exception Types

```python
from src.services.azure_log_analytics_service import SecurityError

# Both MySQL and Azure services raise these:
try:
    results = db_service.execute_query(query)
except SecurityError:
    # Query violated governance policy
    # Same handling for both MySQL and Azure
    print("Query blocked by security policy")
except Exception:
    # Connection or execution error
    # Same handling for both
    print("Query execution failed")
```

## Performance Profile

### Query Execution
- MySQL: Direct TCP connection, typically < 1s
- Azure: HTTPS to Azure Monitor, typically 1-3s
- Result masking: O(R × C) for both, negligible difference

### Schema Discovery
- MySQL: Information_schema queries, fast < 100ms per table
- Azure: KQL union query, moderate ~1-5s for all tables
- Caching: Both benefit from schema caching

### Table Profiling
- MySQL: Multiple queries per column, moderate latency
- Azure: Multiple KQL queries per column, may incur Log Analytics costs
- Both: Support configurable sampling to reduce cost

## Multi-Database Usage

### Hybrid NLQ Pipeline

```python
class HybridExecutor:
    def __init__(self, mysql_service, azure_service):
        self.mysql = mysql_service
        self.azure = azure_service
    
    def execute(self, nlq: str, target: str = "auto"):
        if target == "auto":
            # Route based on query content
            service = self.azure if self._is_security_query(nlq) else self.mysql
        else:
            service = self.mysql if target == "mysql" else self.azure
        
        # Generate appropriate query (SQL or KQL)
        query = self._generate_query(nlq, service)
        
        # Execute - both have same interface!
        return service.execute_query(query)
```

## Implementation Checklist

- ✅ DatabaseExecutionProtocol implemented for both
- ✅ DatabaseReaderProtocol implemented for both
- ✅ DatabaseProfilingServiceProtocol implemented for both
- ✅ Unified error handling
- ✅ Shared governance infrastructure
- ✅ Identical method signatures
- ✅ Compatible output formats
- ✅ Async/await support for both
- ✅ Connection management for both
- ✅ Audit logging for both
- ✅ Schema caching support
- ✅ LLM integration for both
- ✅ Sample data masking for both
- ✅ Virtual table suggestions for both

## Usage Patterns

### Pattern 1: Abstract Database Service
```python
def create_db_service(db_type: str):
    if db_type == "mysql":
        return MySQLService(...)
    else:
        return AzureLogAnalyticsService(...)

service = create_db_service(os.getenv("DATABASE_TYPE"))
results = service.execute_query(query)  # Works for both!
```

### Pattern 2: Protocol-Based Design
```python
def nlq_pipeline(
    executor: DatabaseExecutionProtocol,
    reader: DatabaseReaderProtocol,
    profiler: DatabaseProfilingServiceProtocol
):
    # Works with any conforming implementation
    schema = reader.read_full_schema()
    profile = profiler.profile_database("mydb")
    results = executor.execute_query(query)
    return results
```

### Pattern 3: Multi-Database Routing
```python
def route_nlq(nlq: str):
    if "security" in nlq.lower():
        return execute_with(azure_service, azure_reader, azure_profiler, nlq)
    else:
        return execute_with(mysql_service, mysql_reader, mysql_profiler, nlq)
```
