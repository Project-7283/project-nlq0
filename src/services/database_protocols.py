"""
Database Service Protocols

This module defines abstract protocols for database services to enable interchangeability
between different database systems (MySQL, Azure Log Analytics, etc.).

All database services should implement these protocols to be used interchangeably
in the NLQ pipeline.
"""

from typing import List, Dict, Any, Optional, Tuple, Protocol, Callable, Awaitable


class DatabaseExecutionProtocol(Protocol):
    """Protocol for database query execution services"""
    
    def execute_query(
        self, 
        sql: str, 
        asDict: bool = True, 
        schema_context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a query against the database.
        
        Args:
            sql: Query string (SQL for MySQL, KQL for Azure LA)
            asDict: Return results as list of dicts
            schema_context: Optional schema metadata for governance validation
            
        Returns:
            List of result rows as dicts or tuples
            
        Raises:
            SecurityError: If query violates governance policies
            Exception: If query execution fails
        """
        ...
    
    async def execute_query_async(
        self, 
        sql: str, 
        asDict: bool = True, 
        schema_context: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Asynchronously execute a query against the database.
        
        Args:
            sql: Query string
            asDict: Return results as list of dicts
            schema_context: Optional schema metadata
            
        Returns:
            List of result rows
        """
        ...
    
    def shutdown(self) -> None:
        """Close database connection and cleanup resources"""
        ...


class DatabaseReaderProtocol(Protocol):
    """Protocol for database schema reading services"""
    
    def get_databases(self) -> List[str]:
        """
        Get list of available databases/workspaces.
        
        Returns:
            List of database names
        """
        ...
    
    def get_tables(self, database: str) -> Tuple[List[str], List[str]]:
        """
        Get tables and views in a database.
        
        Args:
            database: Database name
            
        Returns:
            Tuple of (tables, views) lists
        """
        ...
    
    def get_table_schema(self, database: str, table: str) -> List[Dict[str, Any]]:
        """
        Get schema (columns with metadata) for a table.
        
        Args:
            database: Database name
            table: Table name
            
        Returns:
            List of column definitions with metadata
        """
        ...
    
    def get_view_schema(self, database: str, view: str) -> Dict[str, Any]:
        """
        Get definition of a view.
        
        Args:
            database: Database name
            view: View name
            
        Returns:
            View definition metadata
        """
        ...
    
    def get_views(self, database: str) -> List[str]:
        """
        Get list of views in a database.
        
        Args:
            database: Database name
            
        Returns:
            List of view names
        """
        ...
    
    def get_stored_procedures(self, database: str) -> List[str]:
        """
        Get list of stored procedures/functions.
        
        Args:
            database: Database name
            
        Returns:
            List of procedure names
        """
        ...
    
    def read_full_schema(self) -> Dict[str, Any]:
        """
        Read complete schema metadata for all databases.
        
        Returns:
            Hierarchical dict with all database, table, and column metadata
        """
        ...


class DatabaseProfilingServiceProtocol(Protocol):
    """Protocol for database profiling services"""
    
    def profile_database(self, dbname: str) -> Dict[str, Any]:
        """
        Profile entire database with statistics and semantic analysis.
        
        Args:
            dbname: Database name
            
        Returns:
            Profiling data including statistics, column descriptions, and business context
        """
        ...
    
    def profile_table(self, dbname: str, table: str) -> Dict[str, Any]:
        """
        Profile a single table.
        
        Args:
            dbname: Database name
            table: Table name
            
        Returns:
            Table profiling data
        """
        ...
