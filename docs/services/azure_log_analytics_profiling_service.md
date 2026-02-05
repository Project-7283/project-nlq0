# Azure Log Analytics Profiling Service

**File:** `src/services/azure_log_analytics_profiling_service.py`

## Overview
Enriches Azure Log Analytics table metadata with statistics, masked samples, and LLM-generated business semantics. Implements the same interface as DBProfilingService for interchangeable profiling operations.

Combines KQL-based statistical analysis with LLM-powered semantic understanding to provide comprehensive table profiling for NLQ query generation.

## Responsibilities
- Profile tables/columns with KQL statistics (cardinality, null %, distribution)
- Fetch masked samples for LLM context (KQL-level masking keeps PII in-database)
- Generate business context via LLM (purpose, domain, impact, typical queries)
- Suggest virtual tables based on naming patterns
- Integrate data governance for sensitive column masking

## Dependencies
- `AzureLogAnalyticsSchemaReader` (metadata access)
- `AzureLogAnalyticsService` (KQL execution)
- `InferenceServiceProtocol` (light + heavy LLMs)
- `DataGovernanceConfig` (sensitive column detection)

## Data Flow (Mermaid)
\`\`\`mermaid
flowchart TD
    Schema[Azure LA Schema] --> Stats[KQL Stats Collector]
    Stats --> Samples[Masked Samples]
    Samples --> LLM_Light[LLM Light]
    Stats --> LLM_Heavy[LLM Heavy]
    LLM_Light --> Columns[Column Semantics]
    LLM_Heavy --> Tables[Table Semantics]
    Columns --> Graph[Semantic Graph JSON]
    Tables --> Graph
\`\`\`

## Key Algorithms
- **KQL-Level Masking**: Generates masked sample queries to keep PII in Azure (no data export).
- **Categorical Detection**: `is_categorical = distinct_count / row_count < threshold` (default 0.1).
- **Virtual Table Heuristics**: Detects common table name prefixes and proposes aggregated views.
- **Dual-LLM Strategy**: Light model for column descriptions; heavy model for business context.

## Key Methods
- `profile_database(workspace) -> dict` — loops tables; $O(T \times (C + S))$ where $T$ tables, $C$ avg columns, $S$ sampled rows.
- `profile_table(workspace, table) -> dict` — stats + LLM calls; $O(C + S)$ plus LLM latency.
- `_get_table_statistics(...)` — KQL row count; $O(\text{table size})$.
- `_get_column_statistics(...)` — KQL distinct/null stats; $O(\text{column cardinality})$.
- `_get_sample_rows(...)` — KQL limit query + masking; $O(S)$ over sampled rows.

## Method Flow (Mermaid)
\`\`\`mermaid
flowchart TD
    Start[profile_database] --> Tables[list tables]
    Tables --> Loop[for each table]
    Loop --> Stats[profile_table]
    Stats --> ColStats[_get_column_statistics via KQL]
    Stats --> Sample[_get_sample_rows KQL + mask]
    Sample --> LLM1[light_llm column descriptions]
    ColStats --> LLM2[heavy_llm table business context]
    LLM1 --> Merge[merge results]
    LLM2 --> Merge
    Merge --> Out[profiling JSON]
\`\`\`

## Constraints
- Read-only access; profiling queries must not mutate data
- Masking is mandatory when sensitive columns are detected
- Sample limits (5-10 rows) to control query cost and latency
- KQL doesn't provide direct table size bytes; estimation used
- Timespan configurable; default profiles last 7 days of data

## Configuration
Environment variables for profiling behavior:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CATEGORICAL_THRESHOLD` | 0.1 | Ratio for categorical detection |
| `PROFILING_SAMPLE_SIZE` | 10000 | Max rows per sample query |
| `ENABLE_DEBUG_DUMPS` | true | Write profiling JSON to disk |
| `PROFILE_TIMESPAN_DAYS` | 7 | Historical data window for stats |
| `DATA_MASKING_ENABLED` | true | Enable result masking |

## Sample Output (Table Profile)

\`\`\`json
{
  "table_name": "SecurityEvent",
  "workspace": "<workspace-id>",
  "row_count": 1500000,
  "business_purpose": "Windows security events from domain controllers",
  "data_domain": "Security & Compliance",
  "business_impact": "HIGH",
  "typical_queries": [
    "Show failed login attempts",
    "List privileged account access",
    "Find suspicious logon times"
  ],
  "column_statistics": {
    "EventID": {
      "type": "long",
      "distinct_count": 42,
      "is_categorical": true,
      "top_values": [4625, 4624, 4672, ...]
    },
    "Computer": {
      "type": "string",
      "distinct_count": 157,
      "is_categorical": true
    }
  },
  "column_descriptions": {
    "EventID": "Windows event type code",
    "Computer": "Source computer name"
  },
  "sample_data": [
    {"EventID": 4625, "Computer": "DC01", "Account": "***MASKED***"}
  ]
}
\`\`\`

### Virtual Tables
\`\`\`json
{
    "security_summary": {
        "type": "virtual_table",
        "description": "Aggregated security table statistics",
        "source_tables": ["SecurityEvent", "SecurityAlert"],
        "suggested_purpose": "Unified security event analysis"
    }
}
\`\`\`

## Integration with Semantic Graph

The profiling service integrates with `SchemaGraphService`:

\`\`\`python
from src.services.azure_log_analytics_service import AzureLogAnalyticsService
from src.services.azure_log_analytics_reader import AzureLogAnalyticsSchemaReader
from src.services.azure_log_analytics_profiling_service import AzureLogAnalyticsProfilingService

# Setup profiling
azure_service = AzureLogAnalyticsService(workspace_id="<workspace-id>")
azure_reader = AzureLogAnalyticsSchemaReader(azure_service)
profiling_service = AzureLogAnalyticsProfilingService(
    azure_reader=azure_reader,
    azure_service=azure_service,
    light_llm=light_model,
    heavy_llm=heavy_model
)

# Profile workspace
profile = profiling_service.profile_database("<workspace-id>")

# Use in semantic graph
from src.services.schema_graph_service import SchemaGraphService
schema_graph = SchemaGraphService(profile_data=profile)
\`\`\`

## Protocol Implementation
Implements `DatabaseProfilingServiceProtocol` for interchangeability:

\`\`\`python
from src.services.database_protocols import DatabaseProfilingServiceProtocol

# Can be used interchangeably with DBProfilingService
profiler: DatabaseProfilingServiceProtocol = azure_profiling_service
profile = profiler.profile_database(workspace_id)
\`\`\`

## Comparison: Azure LA vs MySQL Profiling

| Aspect | MySQL | Azure Log Analytics |
|--------|-------|---------------------|
| Query Language | SQL | KQL |
| Row Count | SELECT COUNT(*) | `\| count()` |
| Distinct Values | SELECT DISTINCT | `\| dcount()` |
| Type Info | SHOW COLUMNS | `\| limit 0` |
| Sampling | LIMIT 100 | `\| limit 100` |
| Masking Strategy | SQL CASE statements | KQL evaluate |
| Timespan | N/A (static data) | Configurable (e.g., 7 days) |
| System Tables | information_schema | Filtered list |

## Profiling Workflow

1. **Schema Discovery**: Use Azure reader to get tables and columns
2. **Statistics Collection**: KQL queries for row counts, distinct values, types
3. **Sample Retrieval**: Fetch small sample with masking applied
4. **LLM Analysis**: Light model → column descriptions; heavy model → business context
5. **Virtual Tables**: Infer aggregations based on table naming patterns
6. **Output**: JSON profile fed to semantic graph and vector DB

