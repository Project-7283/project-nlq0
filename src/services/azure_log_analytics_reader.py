"""
Azure Log Analytics Schema Reader Service

Reads table and schema metadata from Azure Log Analytics workspaces.
Implements the same interface as DBSchemaReaderService for interchangeable usage.

Maps Azure Log Analytics concepts to database schema terminology:
- Azure Tables → Database Tables
- Custom Tables → User-defined tables
- System Tables → System metadata tables
- Columns → Fields with types

Uses KQL queries to introspect workspace metadata.
"""

from typing import List, Dict, Any, Tuple, Optional
import json
from datetime import datetime

from .azure_log_analytics_service import AzureLogAnalyticsService
from src.utils.logging import app_logger as logger


class AzureLogAnalyticsSchemaReader:
    """
    Service for reading schema metadata from Azure Log Analytics workspaces.
    
    Implements DatabaseReaderProtocol for interchangeability with DBSchemaReaderService.
    Provides:
    - Discovery of tables and custom tables
    - Column metadata with types and descriptions
    - Workspace hierarchy (conceptually equivalent to databases)
    - Virtual table suggestions based on naming patterns
    """
    
    # System tables to exclude from discovery
    SYSTEM_TABLES = {
        'OperationLogs', 'AuditLogs', 'SecurityBaseline', 'ConfigurationChange',
        'Heartbeat', 'Usage', 'Alert', 'LAQueryLogs', 'WorkspaceSchemaAudit'
    }
    
    def __init__(self, azure_service: AzureLogAnalyticsService):
        """
        Initialize Azure Log Analytics schema reader.
        
        Args:
            azure_service: AzureLogAnalyticsService instance for query execution
        """
        self.azure_service = azure_service
        self._table_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[datetime] = None
    
    def get_databases(self) -> List[str]:
        """
        Get list of available workspaces (conceptually equivalent to databases).
        
        In Azure Log Analytics, a workspace is the container for tables.
        This returns a single entry for the configured workspace, but can be
        extended to support multiple workspaces.
        
        Returns:
            List of workspace identifiers
        """
        # For single workspace scenario, return the workspace ID
        if hasattr(self.azure_service, 'workspace_id'):
            return [self.azure_service.workspace_id]
        
        # For multi-workspace scenarios, this can be extended to query
        # available workspaces from Azure Resource Graph
        logger.warning("No workspace ID found in Azure service")
        return []
    
    def get_tables(self, workspace: str) -> Tuple[List[str], List[str]]:
        """
        Get tables and views in a workspace.
        
        In Azure Log Analytics:
        - Tables are actual data tables (both built-in and custom)
        - Views are saved queries (KQL queries that can be referenced)
        
        Args:
            workspace: Workspace ID
            
        Returns:
            Tuple of (tables, views) lists
        """
        try:
            # Get list of tables using KQL metadata query
            tables = self._get_table_list(workspace)
            
            # Separate custom tables from system tables
            custom_tables = [t for t in tables if t not in self.SYSTEM_TABLES]
            
            # Get saved queries/views (if available via query)
            views = self._get_saved_queries(workspace)
            
            return custom_tables, views
        
        except Exception as e:
            logger.error(f"Error fetching tables for workspace {workspace}: {e}")
            return [], []
    
    def get_views(self, workspace: str) -> List[str]:
        """
        Get list of saved queries (views) in a workspace.
        
        Args:
            workspace: Workspace ID
            
        Returns:
            List of view/saved query names
        """
        try:
            return self._get_saved_queries(workspace)
        except Exception as e:
            logger.error(f"Error fetching views for workspace {workspace}: {e}")
            return []
    
    def _get_table_list(self, workspace: str) -> List[str]:
        """
        Get list of available tables in workspace using KQL.
        
        Args:
            workspace: Workspace ID
            
        Returns:
            List of table names
        """
        kql = """
        datatable(TableName:string)
        [
        ]
        | union withsource="TableName" *
        | distinct TableName
        | order by TableName asc
        """
        
        try:
            results = self.azure_service.execute_query(kql, workspace_id=workspace)
            tables = [row.get('TableName') for row in results if row.get('TableName')]
            logger.info(f"Discovered {len(tables)} tables in workspace")
            return tables
        
        except Exception as e:
            logger.warning(f"Could not enumerate tables via union method: {e}")
            logger.info("Returning empty table list - workspace may be empty or lack permissions")
            return []
    
    def _get_saved_queries(self, workspace: str) -> List[str]:
        """
        Get list of saved queries in workspace.
        
        Note: Requires access to workspace metadata APIs or separate query tracking.
        For now, returns empty list as KQL doesn't provide direct access to saved queries.
        
        Args:
            workspace: Workspace ID
            
        Returns:
            List of saved query names
        """
        # Azure Log Analytics doesn't expose saved queries via KQL
        # This would require ARM API access
        logger.debug("Saved queries enumeration not available via KQL")
        return []
    
    def get_table_schema(self, workspace: str, table: str) -> List[Dict[str, Any]]:
        """
        Get schema (columns with metadata) for a table.
        
        Args:
            workspace: Workspace ID
            table: Table name
            
        Returns:
            List of column definitions with type information
        """
        # Check cache first
        cache_key = f"{workspace}:{table}"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        try:
            # Get column info by querying the table with LIMIT 0
            # This returns column types without fetching data
            kql = f"{table} | limit 0"
            
            # Execute with small timeout since we're not fetching data
            results = self.azure_service.execute_query(
                kql,
                workspace_id=workspace
            )
            
            # Extract column information from empty result set
            columns = self._extract_columns_from_result_schema(table, results)
            
            # Cache the result
            self._schema_cache[cache_key] = columns
            
            return columns
        
        except Exception as e:
            logger.warning(f"Error getting schema for {table}: {e}")
            # Return a minimal schema when we can't introspect
            return [
                {"Field": table, "Type": "string", "Description": "Unable to introspect schema"}
            ]
    
    def get_view_schema(self, workspace: str, view: str) -> Dict[str, Any]:
        """
        Get definition of a saved query/view.
        
        Args:
            workspace: Workspace ID
            view: View/query name
            
        Returns:
            View definition metadata
        """
        # Note: Azure Log Analytics doesn't expose saved query definitions via KQL
        # This would require ARM REST API access
        return {
            'view_name': view,
            'type': 'saved_query',
            'description': 'Saved query in Azure Log Analytics',
            'note': 'Full definition requires ARM API access'
        }
    
    def get_stored_procedures(self, workspace: str) -> List[str]:
        """
        Get list of stored procedures.
        
        Note: Azure Log Analytics doesn't have traditional stored procedures.
        This returns empty list for compatibility.
        
        Args:
            workspace: Workspace ID
            
        Returns:
            Empty list (not applicable for Log Analytics)
        """
        logger.debug("Stored procedures not applicable for Azure Log Analytics")
        return []
    
    def read_full_schema(self) -> Dict[str, Any]:
        """
        Read complete schema metadata for all workspaces.
        
        Returns:
            Hierarchical dict with workspace and table metadata
        """
        schema = {}
        
        workspaces = self.get_databases()
        
        for workspace in workspaces:
            logger.info(f"Reading schema for workspace: {workspace}")
            
            schema[workspace] = {
                'tables': {},
                'views': {},
                'procedures': {}
            }
            
            # Get tables
            tables, views = self.get_tables(workspace)
            
            for table in tables:
                logger.debug(f"  Introspecting table: {table}")
                try:
                    schema[workspace]['tables'][table] = self.get_table_schema(workspace, table)
                except Exception as e:
                    logger.warning(f"    Error introspecting {table}: {e}")
                    schema[workspace]['tables'][table] = []
            
            # Get views
            for view in views:
                logger.debug(f"  Introspecting view: {view}")
                try:
                    schema[workspace]['views'][view] = self.get_view_schema(workspace, view)
                except Exception as e:
                    logger.warning(f"    Error introspecting {view}: {e}")
                    schema[workspace]['views'][view] = {}
            
            # Procedures not applicable
            schema[workspace]['procedures'] = {}
        
        return schema
    
    def _extract_columns_from_result_schema(
        self,
        table: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract column information from KQL result structure.
        
        Args:
            table: Table name
            results: Results from LIMIT 0 query (contains column info)
            
        Returns:
            List of column definitions
        """
        columns = []
        
        if not results:
            # Empty table, but we can try to infer from table name
            logger.debug(f"No schema information available for {table}")
            return []
        
        # Extract column names and infer types from first row structure
        first_row = results[0] if results else {}
        
        for col_name, col_value in first_row.items():
            col_type = self._infer_kql_type(col_value)
            
            columns.append({
                'Field': col_name,
                'Type': col_type,
                'Null': 'YES',  # KQL is flexible on nulls
                'Key': None,
                'Default': None,
                'Extra': None
            })
        
        return columns
    
    def _infer_kql_type(self, value: Any) -> str:
        """
        Infer KQL column type from value.
        
        Args:
            value: Column value
            
        Returns:
            KQL type string
        """
        if value is None:
            return 'dynamic'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'long'
        elif isinstance(value, float):
            return 'real'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, dict):
            return 'dynamic'
        elif isinstance(value, list):
            return 'dynamic'
        else:
            return 'dynamic'
    
    def clear_cache(self):
        """Clear schema cache (useful after schema changes)"""
        self._schema_cache.clear()
        self._table_cache.clear()
        self._cache_timestamp = None
        logger.info("Schema cache cleared")
