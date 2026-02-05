````markdown
# Azure Log Analytics Reader Service

**File:** `src/services/azure_log_analytics_reader.py`

## Overview
Reads Azure Log Analytics workspace metadata from tables and custom tables. Implements the same interface as DBSchemaReaderService for interchangeable schema discovery.

Maps Azure Log Analytics concepts to database terminology:
- Azure Tables → Database Tables
- Custom Tables → User-defined tables
- Saved Queries → Views
- Columns → Fields with KQL types

## Responsibilities
- Discover tables and custom tables in workspaces
- Enumerate columns with type information
- Retrieve saved query definitions
- Provide structured metadata for SchemaGraphService and ProfilingService
- Handle system table filtering

## Dependencies
- `AzureLogAnalyticsService` for KQL query execution
- Optional: Azure Resource Graph API for multi-workspace scenarios

## Data Flow (Mermaid)
\`\`\`mermaid
flowchart TD
	LogA[(Azure Log<br/>Analytics)] --> Reader[AzureLogAnalyticsReader]
	Reader --> Tables[Tables List]
	Reader --> Columns[Columns/Types]
	Tables --> SchemaBuilder[SchemaGraphService]
	Columns --> SchemaBuilder
	Columns --> Profiler[AzureLogAnalyticsProfilingService]
\`\`\`

## Key Methods
- `get_databases()` — list available workspaces; $O(W)$ where $W$ workspaces.
- `get_tables(workspace)` — fetch table names; $O(T)$.
- `get_table_schema(workspace, table)` — columns + types; $O(C)$ where $C$ columns.
- `get_view_schema(workspace, view)` — parse definition; $O(|V|)$ by definition length.
- `get_stored_procedures(workspace)` — returns empty (not applicable to Log Analytics); $O(1)$.
- `read_full_schema()` — orchestrates full discovery; $O(W + \sum T + \sum C)$.
- `clear_cache()` — invalidates schema cache; $O(1)$.

## Method Flow (Mermaid)
\`\`\`mermaid
flowchart TD
	Start[read_full_schema] --> DBs[get_databases]
	DBs --> TLoop[for each workspace]
	TLoop --> Tables[get_tables]
	Tables --> SLoop[for each table]
	SLoop --> Schema[get_table_schema]
	Schema --> Views[get_views]
	Views --> Out[structured metadata]
\`\`\`

## Key Algorithms
- **Table Discovery**: Union query across all tables to enumerate names; filters system tables.
- **Schema Inference**: Runs `table | limit 0` to extract column types without data transfer.
- **Type Detection**: Infers KQL types (bool, long, real, string, dynamic) from column values.
- **Caching**: Implements per-workspace schema cache to reduce API calls.

## Constraints
- Read-only access; no DDL/DML operations
- System tables filtered: OperationLogs, AuditLogs, Heartbeat, Usage, etc.
- Saved query definitions require ARM API access (not available via KQL)
- Workspace metadata accessible only if user has Log Analytics Reader role

## Mapping: Azure LA → Database Schema

| Concept | MySQL | Azure Log Analytics |
|---------|-------|---------------------|
| Database | Database | Workspace |
| Table | Table | Table (built-in or custom) |
| Column | Column | Field with KQL type |
| View | View | Saved Query |
| Procedure | Stored Procedure | Function/Analytics Rule |
| Row Count | COUNT(*) | `table \| count()` |
| Column Type | SHOW COLUMNS | `table \| limit 0` |

## Example Usage

\`\`\`python
from src.services.azure_log_analytics_service import AzureLogAnalyticsService
from src.services.azure_log_analytics_reader import AzureLogAnalyticsSchemaReader

# Initialize services
azure_service = AzureLogAnalyticsService(workspace_id="<workspace-id>")
reader = AzureLogAnalyticsSchemaReader(azure_service)

# Discover schema
workspaces = reader.get_databases()
for ws in workspaces:
    tables, views = reader.get_tables(ws)
    print(f"Workspace {ws}: {len(tables)} tables, {len(views)} views")
    
    for table in tables:
        schema = reader.get_table_schema(ws, table)
        for col in schema:
            print(f"  {col['Field']}: {col['Type']}")

# Get full schema
full_schema = reader.read_full_schema()
\`\`\`

## Protocol Implementation
Implements `DatabaseReaderProtocol` for interchangeability:

\`\`\`python
from src.services.database_protocols import DatabaseReaderProtocol

# Can be used interchangeably with DBSchemaReaderService
reader: DatabaseReaderProtocol = azure_reader
schema = reader.read_full_schema()
\`\`\`
````
