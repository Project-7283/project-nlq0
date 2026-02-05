# Azure Log Analytics Services - Implementation Summary

## Overview
Created Azure Log Analytics services that mirror MySQL services with identical protocols for interchangeability in the NLQ pipeline.

## Files Created

### Core Implementation (4 files)

#### 1. `src/services/database_protocols.py` ✅
**Protocol Definitions** for database service interchangeability
- `DatabaseExecutionProtocol` - Query execution interface
- `DatabaseReaderProtocol` - Schema discovery interface  
- `DatabaseProfilingServiceProtocol` - Table profiling interface

**Key Features:**
- Enables drop-in replacement of MySQL services with Azure services
- Protocol-based architecture using Python `typing.Protocol`
- Unified error handling (SecurityError, governance integration)
- Documentation of implementation checklist

#### 2. `src/services/azure_log_analytics_service.py` ✅
**Azure Log Analytics Query Execution Service**
- Mirrors: `MySQLService`
- Implements: `DatabaseExecutionProtocol`

**Key Methods:**
- `execute_query(kql, asDict=True, schema_context=None)` - Execute KQL queries
- `execute_query_async(kql, ...)` - Async execution support
- `shutdown()` - Cleanup Azure client connection

**Key Features:**
- Uses Azure Monitor Query Client SDK
- Service principal and managed identity authentication
- Multi-cloud support (public, China, government)
- Data governance integration (query validation, result masking)
- Audit logging for compliance
- Configurable result timespan (default: 24 hours)

#### 3. `src/services/azure_log_analytics_reader.py` ✅
**Azure Log Analytics Schema Discovery Service**
- Mirrors: `DBSchemaReaderService`
- Implements: `DatabaseReaderProtocol`

**Key Methods:**
- `get_databases()` → List workspaces
- `get_tables(workspace)` → (tables, views) tuple
- `get_table_schema(workspace, table)` → Column definitions
- `get_view_schema(workspace, view)` → View metadata
- `get_views(workspace)` → List saved queries
- `get_stored_procedures(workspace)` → Empty (N/A for Log Analytics)
- `read_full_schema()` → Full workspace schema
- `clear_cache()` → Invalidate schema cache

**Key Features:**
- Discovers tables via KQL union query
- Infers column types from `limit 0` results
- Filters system tables (OperationLogs, Heartbeat, etc.)
- Schema caching to reduce API calls
- Type inference for KQL types (bool, long, real, string, dynamic)

#### 4. `src/services/azure_log_analytics_profiling_service.py` ✅
**Azure Log Analytics Table Profiling Service**
- Mirrors: `DBProfilingService`
- Implements: `DatabaseProfilingServiceProtocol`

**Key Methods:**
- `profile_database(workspace)` → Full workspace profile
- `profile_table(workspace, table)` → Single table profile

**Key Features:**
- Collects statistics via KQL (row counts, cardinality, types)
- Fetches masked samples (keeps PII in Azure)
- LLM-powered business context generation
  - Light LLM: Column descriptions
  - Heavy LLM: Table business context
- Virtual table inference based on naming patterns
- Data governance integration (automatic masking)
- Debug logging and profiling dumps
- Configurable sampling and timespan

**Output Format:**
```json
{
  "table_name": "SecurityEvent",
  "row_count": 1500000,
  "business_purpose": "Windows security events",
  "data_domain": "Security",
  "business_impact": "HIGH",
  "column_statistics": {...},
  "column_descriptions": {...},
  "sample_data": [...]
}
```

### Documentation (6 files)

#### 1. `docs/services/database_protocols.md` ✅
Comprehensive protocol architecture documentation
- Three core protocols explained
- Interchangeability examples
- Implementation checklist
- Concept mapping across databases
- Error handling patterns
- Performance considerations
- Future extensions

#### 2. `docs/services/azure_log_analytics_service.md` ✅
Azure query execution service documentation
- Service overview and responsibilities
- Data flow diagrams (Mermaid)
- Key methods with complexity analysis
- Method flow diagrams
- Governance integration examples
- Protocol implementation details

#### 3. `docs/services/azure_log_analytics_reader.md` ✅
Azure schema reader documentation
- Service overview
- Data flow and responsibilities
- Key algorithms (table discovery, schema inference)
- Method documentation with complexity
- Concept mapping (Azure LA → MySQL)
- Usage examples
- Protocol implementation

#### 4. `docs/services/azure_log_analytics_profiling_service.md` ✅
Azure profiling service documentation
- Service overview and algorithms
- Key methods with complexity
- Configuration parameters
- Sample output format
- Workflow documentation
- Comparison with MySQL profiling
- Integration with semantic graph

#### 5. `docs/services/AZURE_INTEGRATION_README.md` ✅
Complete integration guide and reference
- Quick start setup (5 steps)
- Installation, environment variables, initialization
- Concept mapping reference
- Integration patterns
- Governance and security features
- Table profiling examples
- Performance considerations
- Troubleshooting guide
- Advanced usage examples
- API reference
- Contributing guidelines

#### 6. `src/services/AZURE_SETUP_GUIDE.py` ✅
Code examples and quick reference
- 10 practical sections with runnable code
- MySQL vs Azure initialization comparison
- Identical interface examples
- Async execution patterns
- Multi-database hybrid support
- Governance examples
- Environment configuration
- Protocol type hints usage
- Full HybridNLQExecutor example

## Architecture Overview

```
┌─────────────────────────────────────────┐
│      NLQ Pipeline (Unified)             │
├─────────────────────────────────────────┤
│  Query Generation, Execution, Results   │
│  (Works with any DatabaseExecutionProtocol)
├─────────────────────────────────────────┤
│         Protocol Interfaces             │
├────────────────────┬────────────────────┤
│ MySQL Services     │ Azure Services     │
├────────────────────┼────────────────────┤
│ MySQLService       │ AzureService       │
│ ├─execute_query()  │ ├─execute_query()  │
│ ├─async variant    │ ├─async variant    │
│ └─shutdown()       │ └─shutdown()       │
│                    │                    │
│ DBSchemaReader     │ AzureReader        │
│ ├─get_databases()  │ ├─get_databases()  │
│ ├─get_tables()     │ ├─get_tables()     │
│ ├─get_table_schema │ ├─get_table_schema │
│ └─read_full_schema │ └─read_full_schema │
│                    │                    │
│ DBProfiler         │ AzureProfiler      │
│ ├─profile_database │ ├─profile_database │
│ └─profile_table    │ └─profile_table    │
└────────────────────┴────────────────────┘
```

## Key Design Principles

### 1. Protocol-Based Interchangeability
- Both MySQL and Azure services implement standard protocols
- Pipeline code uses protocol types, not concrete implementations
- Drop-in replacement without code changes

### 2. Unified Governance
- Both use same `DataGovernanceService`
- Identical query validation and result masking
- Consistent audit logging

### 3. Concept Mapping
- Azure Log Analytics terminology → Standard DB terminology
- Workspace → Database
- Tables → Tables
- Fields → Columns
- Saved Queries → Views
- KQL → Query language

### 4. Dual-Model LLM Integration
- Light LLM: Fast, column-level descriptions
- Heavy LLM: Complex, table-level business context
- Both models used in profiling for comprehensive semantic understanding

### 5. Data Privacy
- Sample data retrieved with automatic masking
- Sensitive columns never exported from Azure
- All masking happens at query level (SQL/KQL WHERE clauses)

## Interchangeability Examples

### Example 1: Query Execution
```python
# Same code works with both
def execute_query(db_service: DatabaseExecutionProtocol, query: str):
    return db_service.execute_query(query)

# Use with MySQL
execute_query(mysql_service, "SELECT * FROM users")

# Use with Azure - just swap service
execute_query(azure_service, "SecurityEvent | limit 100")
```

### Example 2: Schema Discovery
```python
def build_schema_graph(reader: DatabaseReaderProtocol):
    return reader.read_full_schema()

# Works with both
graph = build_schema_graph(mysql_reader)
graph = build_schema_graph(azure_reader)
```

### Example 3: Table Profiling
```python
def profile_for_embeddings(profiler: DatabaseProfilingServiceProtocol, db_name: str):
    return profiler.profile_database(db_name)

# Works with both
profile = profile_for_embeddings(mysql_profiler, "mydb")
profile = profile_for_embeddings(azure_profiler, "workspace-id")
```

## Integration Checklist

- ✅ Protocol definitions created
- ✅ Azure query execution service implemented
- ✅ Azure schema reader implemented
- ✅ Azure profiling service implemented
- ✅ Data governance integration
- ✅ Async/await support
- ✅ Audit logging
- ✅ Comprehensive documentation
- ✅ Code examples and quick reference
- ✅ Protocol implementation guide
- ✅ Troubleshooting guide
- ✅ Integration patterns documented

## Configuration

### Environment Variables

```bash
# Azure Authentication
AZURE_TENANT_ID="<tenant-id>"
AZURE_CLIENT_ID="<client-id>"
AZURE_CLIENT_SECRET="<client-secret>"
AZURE_LOG_ANALYTICS_WORKSPACE_ID="<workspace-id>"
AZURE_LOG_ANALYTICS_ENVIRONMENT="public"  # or china, government

# Governance
DATA_GOVERNANCE_ENABLED="true"
DATA_MASKING_ENABLED="true"
SENSITIVE_COLUMNS_CSV="config/sensitive_keywords.csv"

# Profiling
CATEGORICAL_THRESHOLD="0.1"
PROFILING_SAMPLE_SIZE="10000"
PROFILE_TIMESPAN_DAYS="7"
ENABLE_DEBUG_DUMPS="true"
```

## Quick Start

```python
from src.services.azure_log_analytics_service import AzureLogAnalyticsService
from src.services.azure_log_analytics_reader import AzureLogAnalyticsSchemaReader
from src.services.azure_log_analytics_profiling_service import AzureLogAnalyticsProfilingService

# Initialize
azure_service = AzureLogAnalyticsService()
azure_reader = AzureLogAnalyticsSchemaReader(azure_service)
azure_profiler = AzureLogAnalyticsProfilingService(
    azure_reader, azure_service, llm_light, llm_heavy
)

# Use identically to MySQL services
results = azure_service.execute_query("SecurityEvent | limit 100")
schema = azure_reader.read_full_schema()
profile = azure_profiler.profile_database("<workspace-id>")
```

## Performance Considerations

- **Query Timeouts**: Default 30s via Azure SDK
- **Result Sizes**: Use `limit N` in KQL to control data transfer
- **Schema Discovery**: Table enumeration via union; slower for large workspaces
- **Profiling Cost**: Multiple KQL queries; Configure sampling to reduce cost
- **Caching**: Schema readers cache results; call `clear_cache()` when needed

## Next Steps

1. **Test Integration**: Run NLQ pipeline with Azure services
2. **Performance Tuning**: Adjust profiling parameters for your workspace
3. **Multi-Database Setup**: Use HybridNLQExecutor for MySQL + Azure
4. **Custom Connectors**: Extend protocol for PostgreSQL, Snowflake, etc.
5. **Cost Optimization**: Monitor Azure Log Analytics query costs during profiling

## Support

For issues or questions:
1. Check [AZURE_INTEGRATION_README.md](./AZURE_INTEGRATION_README.md) troubleshooting section
2. Review code examples in [AZURE_SETUP_GUIDE.py](../src/services/AZURE_SETUP_GUIDE.py)
3. Consult protocol documentation in [database_protocols.md](./database_protocols.md)
4. Review service-specific docs in this directory
