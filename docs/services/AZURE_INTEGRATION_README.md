# Azure Log Analytics Services - Complete Integration Guide

This package provides Azure Log Analytics services that implement the same protocols as the MySQL services, enabling seamless interchangeability in the NLQ pipeline.

## Overview

The following services have been created to mirror the MySQL services:

| MySQL Service | Azure Log Analytics Service | Purpose |
|---|---|---|
| `MySQLService` | `AzureLogAnalyticsService` | Query execution with governance |
| `DBSchemaReaderService` | `AzureLogAnalyticsSchemaReader` | Schema discovery |
| `DBProfilingService` | `AzureLogAnalyticsProfilingService` | Table profiling with statistics |

All three are built on **protocol-based architecture** using Python's `typing.Protocol`, enabling drop-in replacement without code changes.

## Files Created

### Implementation Files
- **[azure_log_analytics_service.py](../src/services/azure_log_analytics_service.py)** - Azure query execution service
- **[azure_log_analytics_reader.py](../src/services/azure_log_analytics_reader.py)** - Azure schema reader
- **[azure_log_analytics_profiling_service.py](../src/services/azure_log_analytics_profiling_service.py)** - Azure table profiler
- **[database_protocols.py](../src/services/database_protocols.py)** - Protocol definitions for interchangeability

### Documentation Files
- **[azure_log_analytics_service.md](./azure_log_analytics_service.md)** - Query execution documentation
- **[azure_log_analytics_reader.md](./azure_log_analytics_reader.md)** - Schema reader documentation
- **[azure_log_analytics_profiling_service.md](./azure_log_analytics_profiling_service.md)** - Profiling documentation
- **[database_protocols.md](./database_protocols.md)** - Protocol architecture documentation

### Example/Reference Files
- **[AZURE_SETUP_GUIDE.py](../src/services/AZURE_SETUP_GUIDE.py)** - Code examples and quick reference

## Quick Start

### 1. Install Azure SDK

```bash
pip install azure-identity azure-monitor-query
```

### 2. Set Environment Variables

```bash
# Azure authentication
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_LOG_ANALYTICS_WORKSPACE_ID="your-workspace-id"

# Optional: Cloud environment (default: public)
export AZURE_LOG_ANALYTICS_ENVIRONMENT="public"  # or "china", "government"

# Governance
export DATA_GOVERNANCE_ENABLED="true"
export DATA_MASKING_ENABLED="true"
export SENSITIVE_COLUMNS_CSV="config/sensitive_keywords.csv"

# Profiling
export CATEGORICAL_THRESHOLD="0.1"
export PROFILING_SAMPLE_SIZE="10000"
export PROFILE_TIMESPAN_DAYS="7"
export ENABLE_DEBUG_DUMPS="true"
```

### 3. Initialize Services

```python
from src.services.azure_log_analytics_service import AzureLogAnalyticsService
from src.services.azure_log_analytics_reader import AzureLogAnalyticsSchemaReader
from src.services.azure_log_analytics_profiling_service import AzureLogAnalyticsProfilingService
from src.services.data_governance_service import DataGovernanceService

# Setup governance
governance = DataGovernanceService("config/sensitive_keywords.csv")

# Initialize services
azure_service = AzureLogAnalyticsService(
    workspace_id="<workspace-id>",
    governance_service=governance
)

azure_reader = AzureLogAnalyticsSchemaReader(azure_service)

azure_profiler = AzureLogAnalyticsProfilingService(
    azure_reader=azure_reader,
    azure_service=azure_service,
    light_llm=light_llm_model,
    heavy_llm=heavy_llm_model
)
```

### 4. Use Like MySQL Services

```python
# Execute KQL queries (same interface as MySQL)
results = azure_service.execute_query(
    "SecurityEvent | where EventID == 4625 | limit 100"
)

# Discover schema (same interface as MySQL)
schema = azure_reader.read_full_schema()

# Profile tables (same interface as MySQL)
profile = azure_profiler.profile_database("<workspace-id>")
```

## Key Concepts

### Concept Mapping

Azure Log Analytics uses different terminology than traditional databases:

| Concept | MySQL | Azure Log Analytics |
|---------|-------|---------------------|
| SQL Language | SQL | KQL (Kusto Query Language) |
| Database | Database | Workspace |
| Table | Table | Table (built-in or custom) |
| Column | Column | Field |
| View | View | Saved Query |
| Procedure | Stored Procedure | Function/Analytics Rule |
| Row Count | SELECT COUNT(*) | `\| count()` |
| Type Discovery | SHOW COLUMNS | `\| limit 0` |
| Sampling | LIMIT N | `\| limit N` |

### Query Language Translation

**KQL Basics** (instead of SQL):

```kusto
// Simple select
SecurityEvent
| where EventID == 4625
| limit 100

// Aggregation
SecurityEvent
| summarize Count=count() by Computer
| top 10 by Count

// Distinct values
SecurityEvent
| distinct Computer

// Join
SecurityEvent
| join kind=inner (
    AuditEvent
) on Computer

// Masking samples
SecurityEvent
| where EventID == 4625
| limit 5
```

## Integration Patterns

### Pattern 1: Drop-in Replacement

```python
# MySQL version
mysql_service = MySQLService(...)
results = mysql_service.execute_query("SELECT * FROM users")

# Azure version (no other code changes!)
azure_service = AzureLogAnalyticsService(...)
results = azure_service.execute_query("SecurityEvent | limit 100")
```

### Pattern 2: Abstraction Layer

```python
def get_database_service(database_type: str):
    """Factory for database services"""
    if database_type == "mysql":
        return MySQLService(...)
    elif database_type == "azure":
        return AzureLogAnalyticsService(...)
    else:
        raise ValueError(f"Unknown database: {database_type}")

# Use with protocol type hints
from src.services.database_protocols import DatabaseExecutionProtocol
db_service: DatabaseExecutionProtocol = get_database_service("azure")
results = db_service.execute_query(query)
```

### Pattern 3: Multi-Database Pipeline

```python
class HybridNLQPipeline:
    """Execute NLQ against MySQL or Azure based on content"""
    
    def __init__(self, mysql_service, azure_service):
        self.mysql_service = mysql_service
        self.azure_service = azure_service
    
    def execute(self, nlq: str, target: str = "auto") -> List[Dict]:
        if target == "auto":
            # Route based on keywords
            target = "azure" if self._is_security_query(nlq) else "mysql"
        
        if target == "azure":
            kql = self.llm_generate_kql(nlq)
            return self.azure_service.execute_query(kql)
        else:
            sql = self.llm_generate_sql(nlq)
            return self.mysql_service.execute_query(sql)
```

## Governance and Security

Both MySQL and Azure services integrate with `DataGovernanceService`:

### Features

1. **Query Validation**: Block queries accessing sensitive columns
2. **Result Masking**: Mask sensitive data in results
3. **Audit Logging**: Log all query executions
4. **Configurable Keywords**: Sensitive column detection via CSV

### Configuration

**config/sensitive_keywords.csv:**
```csv
keyword
password
ssn
credit_card
api_key
token
```

### Example

```python
# Sensitive query blocked automatically
try:
    results = azure_service.execute_query(
        "SecurityEvent | where AccountPassword == 'secret'"
    )
except SecurityError as e:
    print(f"Query blocked: {e}")  # Query blocked by governance policy

# Results masked automatically
results = azure_service.execute_query(
    "SecurityEvent | where EventID == 4625"
)
# Sensitive columns in results are masked
for row in results:
    print(row["UserPassword"])  # Returns "***MASKED***"
```

## Table Profiling

Both MySQL and Azure profilers output the same format:

```json
{
  "table_name": "SecurityEvent",
  "workspace": "<workspace-id>",
  "row_count": 1500000,
  "business_purpose": "Windows security events from domain controllers",
  "data_domain": "Security & Compliance",
  "business_impact": "HIGH",
  "column_statistics": {
    "EventID": {
      "type": "long",
      "distinct_count": 42,
      "is_categorical": true,
      "top_values": [4625, 4624, 4672]
    }
  },
  "column_descriptions": {
    "EventID": "Windows event type code"
  },
  "sample_data": [
    {"EventID": 4625, "Computer": "DC01", "Account": "***MASKED***"}
  ]
}
```

This format is fed into the semantic graph and vector store for NLQ understanding.

## Performance Considerations

### Query Execution
- **Sync vs Async**: Use async for batch operations or timeouts
- **Timespan**: Default 24 hours; configure via `execute_query(timespan=...)`
- **Limits**: Use `limit N` in KQL to reduce data transfer

### Schema Discovery
- **Caching**: Readers implement schema caching; call `clear_cache()` when schema changes
- **Large Workspaces**: Table enumeration via union may be slow; consider filtering
- **Metadata Queries**: Direct `information_schema` equivalent not available; uses KQL inference

### Table Profiling
- **Expensive Operation**: Multiple KQL queries per column
- **Sampling**: Configure `PROFILING_SAMPLE_SIZE` and `PROFILE_TIMESPAN_DAYS`
- **Cost**: Azure Log Analytics charges per GB queried; profiling can be costly
- **Caching**: Cache profile results and refresh periodically

## Troubleshooting

### Authentication Issues

```python
# Check credentials
try:
    azure_service = AzureLogAnalyticsService()
except Exception as e:
    print(f"Authentication failed: {e}")
    # Verify environment variables are set
    # Verify service principal has Log Analytics Reader role
```

### Query Timeouts

```python
# Increase timeout (not directly supported; Azure SDK defaults to 30s)
# Instead, limit query scope:
results = azure_service.execute_query(
    "SecurityEvent | where EventID == 4625 | limit 1000"
)
```

### No Results

```python
# Check if table exists
tables, views = azure_reader.get_tables("<workspace-id>")
print(f"Available tables: {tables}")

# Check timespan (data may not exist for the time range)
from datetime import timedelta
results = azure_service.execute_query(
    "SecurityEvent | limit 1",
    timespan=timedelta(days=30)  # Search last 30 days
)
```

## Advanced Usage

### Async Batch Operations

```python
import asyncio

async def profile_multiple_workspaces(profiler, workspace_ids):
    tasks = [
        asyncio.to_thread(profiler.profile_database, ws)
        for ws in workspace_ids
    ]
    profiles = await asyncio.gather(*tasks)
    return profiles
```

### Custom Query Functions

```python
def get_failed_logins(azure_service, hours=24):
    kql = f"""
    SecurityEvent
    | where EventID == 4625
    | where TimeGenerated > ago({hours}h)
    | summarize Count=count() by Computer
    | sort by Count desc
    """
    return azure_service.execute_query(kql)

failed_logins = get_failed_logins(azure_service, hours=1)
```

### Schema Extension

```python
# Add custom virtual tables
custom_schema = {
    "virtual_tables": {
        "security_summary": {
            "source_tables": ["SecurityEvent", "SecurityAlert"],
            "description": "Unified security events"
        }
    }
}
```

## API Reference

### AzureLogAnalyticsService

```python
service = AzureLogAnalyticsService(
    tenant_id: str,           # Azure tenant ID
    client_id: str,           # Service principal client ID
    client_secret: str,       # Service principal secret
    workspace_id: str,        # Log Analytics workspace ID
    environment: str = "public",  # Cloud environment
    governance_service = None  # Optional governance
)

# Execute query
results = service.execute_query(
    kql: str,
    asDict: bool = True,
    schema_context: Dict = None,
    workspace_id: str = None,
    timespan: timedelta = None
)

# Async execution
results = await service.execute_query_async(...)

# Cleanup
service.shutdown()
```

### AzureLogAnalyticsSchemaReader

```python
reader = AzureLogAnalyticsSchemaReader(
    azure_service: AzureLogAnalyticsService
)

# Schema discovery
workspaces = reader.get_databases()
tables, views = reader.get_tables(workspace)
schema = reader.get_table_schema(workspace, table)
full_schema = reader.read_full_schema()

# Cache management
reader.clear_cache()
```

### AzureLogAnalyticsProfilingService

```python
profiler = AzureLogAnalyticsProfilingService(
    azure_reader: AzureLogAnalyticsSchemaReader,
    azure_service: AzureLogAnalyticsService,
    light_llm: InferenceServiceProtocol,
    heavy_llm: InferenceServiceProtocol,
    governance_config: DataGovernanceConfig = None
)

# Profiling
profile = profiler.profile_database(workspace)
table_profile = profiler.profile_table(workspace, table)
```

## Contributing

When extending Azure services:

1. **Maintain Protocol Compliance**: All implementations must conform to the protocol interfaces
2. **Use KQL, Not SQL**: Transform any SQL concepts to KQL equivalents
3. **Handle Azure Differences**: Map Azure concepts properly (Workspace ≠ Database)
4. **Test Interchangeability**: Ensure MySQL and Azure services can be swapped
5. **Document Mappings**: Document how Azure concepts map to standard DB concepts

## References

- [Azure Monitor Query API](https://learn.microsoft.com/en-us/python/api/overview/azure/monitor-query-readme)
- [Kusto Query Language (KQL) Reference](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Log Analytics Workspace Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-overview)
- [Database Protocol Architecture](./database_protocols.md)
