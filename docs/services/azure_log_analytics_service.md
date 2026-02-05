````markdown
# Azure Log Analytics Service

**File:** `src/services/azure_log_analytics_service.py`

## Overview
Wrapper around Azure Monitor Query Client implementing the same interface as MySQLService. Executes KQL (Kusto Query Language) queries against Azure Log Analytics workspaces with data governance integration.

## Responsibilities
- Manage Azure credentials and workspace connections
- Execute KQL queries with timeout and error handling
- Integrate DataGovernanceService for query validation and result masking
- Provide async/sync execution modes
- Audit logging for all operations

## Dependencies
- Azure SDK: `azure-identity`, `azure-monitor-query`
- Env vars: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_LOG_ANALYTICS_WORKSPACE_ID`
- `DataGovernanceService` (optional) for query validation and result masking

## Data Flow (Mermaid)
\`\`\`mermaid
flowchart TD
    KQL[KQL from SQLGenerationService] --> Gov{Governance?}
    Gov -- Block --> Err[SecurityError]
    Gov -- OK --> Exec[Azure Monitor Client]
    Exec --> Process[Process Results]
    Process --> Mask[Mask Results]
    Mask --> Caller
\`\`\`

## Key Methods
- `execute_query(kql, asDict=True)` — governance validation $O(L)$ then KQL execution; result masking $O(R \times C)$.
- `execute_query_async(kql, asDict=True)` — async wrapper around execute_query.
- `shutdown()` — closes Azure client connection; $O(1)$.

## Method Flow (Mermaid)
\`\`\`mermaid
flowchart TD
    KQL[Input KQL] --> Gov[validate_query]
    Gov -- Block --> Err[SecurityError]
    Gov -- OK --> Exec[client.query_workspace]
    Exec -- SUCCESS --> Process[process results]
    Exec -- PARTIAL --> Warn[log warning]
    Exec -- FAILURE --> Error[raise exception]
    Process --> Mask[mask_results]
    Warn --> Mask
    Mask --> Return[rows]
\`\`\`

## Constraints
- Async credential handling required for service principal auth
- Result processing converts Azure table format to dict
- Query timespan defaults to last 24 hours
- Supports public, China, and US Government cloud environments

## Integration with Governance
The service integrates seamlessly with DataGovernanceService:

\`\`\`python
from src.services.azure_log_analytics_service import AzureLogAnalyticsService
from src.services.data_governance_service import DataGovernanceService

# Setup governance
governance = DataGovernanceService("config/sensitive_keywords.csv")

# Setup Azure service with governance
azure_service = AzureLogAnalyticsService(
    workspace_id="<workspace-id>",
    governance_service=governance
)

# Execute query - governance validation happens automatically
results = azure_service.execute_query("SecurityEvent | where EventID == 4625")
# Results are automatically masked if sensitive columns detected
\`\`\`

## Protocol Implementation
Implements `DatabaseExecutionProtocol` for interchangeability:

\`\`\`python
from src.services.database_protocols import DatabaseExecutionProtocol

# Can be used interchangeably with MySQLService
service: DatabaseExecutionProtocol = azure_service
results = service.execute_query(query_string)
\`\`\`
````
