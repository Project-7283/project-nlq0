"""
Azure Log Analytics Query Service

Wrapper around Azure Monitor Query Client with data governance hooks.
Implements the same interface as MySQLService for interchangeable usage.

Executes KQL (Kusto Query Language) queries against Azure Log Analytics workspaces.
Supports query validation, result masking, and audit logging.

Environment Variables:
    AZURE_TENANT_ID: Azure tenant ID
    AZURE_CLIENT_ID: Service principal client ID
    AZURE_CLIENT_SECRET: Service principal client secret
    AZURE_LOG_ANALYTICS_WORKSPACE_ID: Default workspace ID
    AZURE_LOG_ANALYTICS_ENVIRONMENT: Cloud environment (default: public)
    DATA_GOVERNANCE_ENABLED: Enable/disable governance checks (default: true)
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Optional Azure dependencies - will be imported if available
try:
    from azure.identity import ClientSecretCredential, DefaultAzureCredential
    from azure.monitor.query import LogsQueryClient, LogsQueryStatus
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


from src.utils.logging import audit_logger, app_logger as logger


class SecurityError(Exception):
    """Raised when a query violates data governance policies"""
    pass


class AzureLogAnalyticsService:
    """
    Service for executing KQL queries against Azure Log Analytics.
    
    Implements DatabaseExecutionProtocol for interchangeability with MySQLService.
    Provides:
    - KQL query execution with timeout handling
    - Integration with DataGovernanceService for query validation and result masking
    - Async/sync execution modes
    - Audit logging for all operations
    """
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        workspace_id: Optional[str] = None,
        environment: str = "public",
        governance_service=None
    ):
        """
        Initialize Azure Log Analytics service.
        
        Args:
            tenant_id: Azure tenant ID (env var: AZURE_TENANT_ID)
            client_id: Service principal client ID (env var: AZURE_CLIENT_ID)
            client_secret: Service principal secret (env var: AZURE_CLIENT_SECRET)
            workspace_id: Default workspace ID (env var: AZURE_LOG_ANALYTICS_WORKSPACE_ID)
            environment: Cloud environment - 'public', 'china', 'government' (default: public)
            governance_service: Optional DataGovernanceService for policy enforcement
            
        Raises:
            ImportError: If Azure SDK is not installed
            ValueError: If required credentials are missing
        """
        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure SDK not installed. Install with: "
                "pip install azure-identity azure-monitor-query"
            )
        
        # Load credentials from parameters or environment
        self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
        self.client_id = client_id or os.getenv("AZURE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("AZURE_CLIENT_SECRET")
        self.workspace_id = workspace_id or os.getenv("AZURE_LOG_ANALYTICS_WORKSPACE_ID")
        self.environment = environment or os.getenv("AZURE_LOG_ANALYTICS_ENVIRONMENT", "public")
        
        # Validate required credentials
        if not self.workspace_id:
            raise ValueError(
                "Azure Log Analytics workspace ID is required. "
                "Set AZURE_LOG_ANALYTICS_WORKSPACE_ID environment variable."
            )
        
        # Initialize Azure client
        try:
            if self.tenant_id and self.client_id and self.client_secret:
                # Service principal authentication
                credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                logger.info("Using service principal authentication for Azure Log Analytics")
            else:
                # Default credential chain (managed identity, CLI, etc.)
                credential = DefaultAzureCredential()
                logger.info("Using default credential chain for Azure Log Analytics")
            
            # Determine Azure endpoint based on environment
            endpoint_map = {
                "public": "https://api.loganalytics.io",
                "china": "https://api.loganalytics.azure.cn",
                "government": "https://api.loganalytics.us"
            }
            
            endpoint = endpoint_map.get(self.environment.lower(), endpoint_map["public"])
            
            self.client = LogsQueryClient(credential, endpoint=endpoint)
            logger.info(
                f"Azure Log Analytics client initialized for workspace: {self.workspace_id[:8]}..."
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Log Analytics client: {str(e)}")
            raise e
        
        self.governance = governance_service
        self.governance_enabled = os.getenv("DATA_GOVERNANCE_ENABLED", "true").lower() == "true"
    
    def _execute_sync(
        self,
        kql: str,
        asDict: bool = True,
        schema_context: Optional[Dict] = None,
        workspace_id: Optional[str] = None,
        timespan: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """
        Synchronously execute KQL query.
        
        Args:
            kql: Kusto Query Language string
            asDict: Return results as list of dicts
            schema_context: Optional schema metadata for governance validation
            workspace_id: Workspace ID override (uses default if not provided)
            timespan: Time range for query (default: last 24 hours)
            
        Returns:
            List of result rows as dicts or tuples
            
        Raises:
            SecurityError: If query violates governance policies
        """
        workspace = workspace_id or self.workspace_id
        
        # Governance validation
        if self.governance_enabled and self.governance:
            is_valid, error_msg = self.governance.validate_query(kql, schema_context)
            if not is_valid:
                self._audit_log("BLOCKED", kql, error_msg)
                raise SecurityError(error_msg)
        
        try:
            # Set default timespan if not provided (last 24 hours)
            if timespan is None:
                timespan = timedelta(days=1)
            
            # Execute query
            response = self.client.query_workspace(
                workspace_id=workspace,
                query=kql,
                timespan=timespan
            )
            
            # Process results
            result = []
            if response.status == LogsQueryStatus.SUCCESS:
                for table in response.tables:
                    for row in table.rows:
                        if asDict:
                            # Convert row to dict using column names
                            row_dict = {
                                col.name: row[idx]
                                for idx, col in enumerate(table.columns)
                            }
                            result.append(row_dict)
                        else:
                            result.append(tuple(row))
                
                self._audit_log("SUCCESS", kql, f"Returned {len(result)} rows")
                
                # Apply result masking if governance enabled
                if asDict and self.governance_enabled and self.governance:
                    result = self.governance.mask_results(result)
                
                return result
            
            elif response.status == LogsQueryStatus.PARTIAL:
                logger.warning(f"Partial results returned for query. Errors: {response.error}")
                self._audit_log("PARTIAL", kql, f"Partial results with errors")
                
                # Still return partial results
                for table in response.tables:
                    for row in table.rows:
                        if asDict:
                            row_dict = {
                                col.name: row[idx]
                                for idx, col in enumerate(table.columns)
                            }
                            result.append(row_dict)
                        else:
                            result.append(tuple(row))
                return result
            
            else:
                error_msg = str(response.error) if response.error else "Unknown error"
                self._audit_log("ERROR", kql, error_msg)
                raise Exception(f"KQL query failed: {error_msg}")
        
        except Exception as e:
            self._audit_log("ERROR", kql, str(e))
            raise e
    
    async def execute_query_async(
        self,
        kql: str,
        asDict: bool = True,
        schema_context: Optional[Dict] = None,
        workspace_id: Optional[str] = None,
        timespan: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """
        Asynchronously execute KQL query.
        
        Args:
            kql: Kusto Query Language string
            asDict: Return results as list of dicts
            schema_context: Optional schema metadata for governance validation
            workspace_id: Workspace ID override
            timespan: Time range for query
            
        Returns:
            List of result rows
        """
        return await asyncio.to_thread(
            self._execute_sync,
            kql,
            asDict,
            schema_context,
            workspace_id,
            timespan
        )
    
    def execute_query(
        self,
        kql: str,
        asDict: bool = True,
        schema_context: Optional[Dict] = None,
        workspace_id: Optional[str] = None,
        timespan: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute KQL query synchronously.
        
        Implements DatabaseExecutionProtocol.execute_query() for interchangeability.
        
        Args:
            kql: Kusto Query Language query string
            asDict: Return results as list of dicts (default: True)
            schema_context: Optional schema metadata for governance
            workspace_id: Log Analytics workspace ID (uses default if not provided)
            timespan: Time range for query (default: last 24 hours)
            
        Returns:
            List of result rows as dicts or tuples
        """
        return self._execute_sync(kql, asDict, schema_context, workspace_id, timespan)
    
    def _audit_log(self, status: str, query: str, message: str):
        """Log query execution for audit purposes"""
        audit_logger.info(
            f"[{status}] KQL: {query[:200]}... | Message: {message}"
        )
    
    def shutdown(self):
        """Close connection and cleanup resources"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("Azure Log Analytics client closed")
        except Exception as e:
            logger.warning(f"Error closing Azure client: {e}")
