"""
Azure Log Analytics Profiling Service

Enriches Azure Log Analytics table metadata with statistics and LLM-generated business semantics.
Implements the same interface as DBProfilingService for interchangeable usage.

Provides:
- Table statistics (row counts, distinct values, data types)
- Masked sample data retrieval
- LLM-powered business context generation
- Virtual table/view suggestions
- Data governance integration

Uses KQL queries for metadata and profiling operations.
"""

import os
import json
import logging
import time
from typing import Optional, Dict, Any, List, Protocol
from datetime import datetime, timedelta
from pathlib import Path

from .azure_log_analytics_service import AzureLogAnalyticsService
from .azure_log_analytics_reader import AzureLogAnalyticsSchemaReader
from src.utils.logging import performance_logger, app_logger as logger


class InferenceServiceProtocol(Protocol):
    """Protocol for LLM inference services"""
    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]: ...


class DataGovernanceConfig:
    """
    Configuration for data governance and sensitive data masking.
    """
    
    def __init__(self, sensitive_keywords_csv: Optional[str] = None):
        self.default_keywords = [
            "password", "token", "secret", "hash", "api_key",
            "private_key", "salt", "ssn", "credit_card", "cvv",
            "pin", "auth", "credential", "key", "bearer"
        ]
        
        self.sensitive_keywords = self._load_keywords(sensitive_keywords_csv)
        self.masking_enabled = os.getenv("DATA_MASKING_ENABLED", "true").lower() == "true"
    
    def _load_keywords(self, csv_path: Optional[str]) -> List[str]:
        """Load sensitive keywords from CSV file"""
        if not csv_path:
            csv_path = os.getenv("SENSITIVE_COLUMNS_CSV")
        
        if csv_path and os.path.exists(csv_path):
            try:
                import csv as csv_module
                keywords = []
                with open(csv_path, 'r') as f:
                    reader = csv_module.DictReader(f)
                    for row in reader:
                        keywords.append(row['keyword'].lower())
                logger.info(f"Loaded {len(keywords)} sensitive keywords from {csv_path}")
                return keywords
            except Exception as e:
                logger.warning(f"Error loading sensitive keywords CSV: {e}. Using defaults.")
                return self.default_keywords
        
        return self.default_keywords
    
    def is_sensitive_column(self, column_name: str) -> bool:
        """Check if column name contains sensitive keywords"""
        if not self.masking_enabled:
            return False
        
        column_lower = column_name.lower()
        return any(keyword in column_lower for keyword in self.sensitive_keywords)


class AzureLogAnalyticsProfilingService:
    """
    Service for profiling Azure Log Analytics tables.
    
    Combines statistical analysis via KQL with LLM-powered semantic understanding.
    Supports data governance with sensitive column masking.
    
    Implements DatabaseProfilingServiceProtocol for interchangeability with DBProfilingService.
    """
    
    def __init__(
        self,
        azure_reader: AzureLogAnalyticsSchemaReader,
        azure_service: AzureLogAnalyticsService,
        light_llm: InferenceServiceProtocol,
        heavy_llm: InferenceServiceProtocol,
        governance_config: Optional[DataGovernanceConfig] = None
    ):
        """
        Initialize Azure Log Analytics profiling service.
        
        Args:
            azure_reader: Azure schema reader for metadata
            azure_service: Azure service for KQL execution
            light_llm: Lightweight LLM for simple tasks (column descriptions)
            heavy_llm: Heavy LLM for complex tasks (business analysis)
            governance_config: Data governance configuration
        """
        self.azure_reader = azure_reader
        self.azure_service = azure_service
        self.light_llm = light_llm
        self.heavy_llm = heavy_llm
        self.governance = governance_config or DataGovernanceConfig()
        
        # Setup debug logging directory
        self.debug_log_dir = Path("logs/profiling_debug")
        self.debug_log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_debug_dumps = os.getenv("ENABLE_DEBUG_DUMPS", "true").lower() == "true"
        
        # Configuration
        self.categorical_threshold = float(os.getenv("CATEGORICAL_THRESHOLD", "0.1"))
        self.profiling_sample_size = int(os.getenv("PROFILING_SAMPLE_SIZE", "10000"))
        self.top_values_limit = 20
        self.profile_timespan = timedelta(days=int(os.getenv("PROFILE_TIMESPAN_DAYS", "7")))
    
    def _dump_debug_data(self, filename: str, data: Any, description: str = ""):
        """Dump data to file for debugging"""
        if not self.enable_debug_dumps:
            return
        
        try:
            filepath = self.debug_log_dir / filename
            with open(filepath, 'w') as f:
                if description:
                    f.write(f"# {description}\n\n")
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Debug dump: {filepath}")
        except Exception as e:
            logger.warning(f"Could not write debug dump {filename}: {e}")
    
    def profile_database(self, workspace: str) -> Dict[str, Any]:
        """
        Profile entire Azure Log Analytics workspace.
        
        Args:
            workspace: Workspace ID
            
        Returns:
            Dictionary containing profile data for all tables
        """
        start_time = time.time()
        logger.info(f"Starting workspace profiling: {workspace}")
        
        profile_data = {
            "workspace": workspace,
            "tables": {},
            "views": {},
            "profiling_timestamp": datetime.now().isoformat(),
            "governance_enabled": self.governance.masking_enabled
        }
        
        tables, views = self.azure_reader.get_tables(workspace)
        
        # Profile tables
        for i, table in enumerate(tables, 1):
            logger.info(f"[{i}/{len(tables)}] Profiling table: {table}")
            try:
                profile_data["tables"][table] = self.profile_table(workspace, table)
            except Exception as e:
                logger.error(f"Error profiling table {table}: {e}")
                profile_data["tables"][table] = {"error": str(e)}
        
        # Process views
        for view in views:
            logger.info(f"Processing view: {view}")
            try:
                profile_data["views"][view] = self._profile_view(workspace, view)
            except Exception as e:
                logger.error(f"Error profiling view {view}: {e}")
        
        # Infer virtual tables
        logger.info("Inferring virtual tables from data patterns...")
        virtual_tables = self._infer_virtual_tables(workspace, profile_data)
        profile_data["virtual_tables"] = virtual_tables
        
        logger.info(f"Profiling complete! Tables: {len(profile_data['tables'])}, "
                   f"Views: {len(profile_data['views'])}, "
                   f"Virtual Tables: {len(virtual_tables)}")
        
        duration = time.time() - start_time
        performance_logger.info(f"Workspace profiling for {workspace} completed in {duration:.2f}s")
        
        return profile_data
    
    def profile_table(self, workspace: str, table: str) -> Dict[str, Any]:
        """
        Profile a single Azure Log Analytics table.
        
        Args:
            workspace: Workspace ID
            table: Table name
            
        Returns:
            Dictionary containing table profile
        """
        logger.info(f"  Profiling table: {table}")
        
        profile = {
            "table_name": table,
            "workspace": workspace,
            "profile_timestamp": datetime.now().isoformat(),
            "column_statistics": {},
            "column_descriptions": {}
        }
        
        try:
            # Get schema
            schema = self.azure_reader.get_table_schema(workspace, table)
            
            # Get row count and stats
            stats = self._get_table_statistics(workspace, table)
            profile.update(stats)
            
            # Profile each column
            for column in schema:
                col_name = column.get('Field')
                col_type = column.get('Type')
                
                if not col_name:
                    continue
                
                logger.debug(f"    Profiling column: {col_name}")
                
                col_stats = self._get_column_statistics(
                    workspace, table, col_name, col_type
                )
                profile["column_statistics"][col_name] = col_stats
            
            # Get masked samples
            logger.debug(f"    Fetching sample data...")
            samples = self._get_sample_rows(workspace, table)
            profile["sample_data"] = samples
            
            # Generate LLM semantics
            logger.debug(f"    Generating LLM semantics...")
            
            # Light LLM for column descriptions
            for col_name in profile["column_statistics"].keys():
                try:
                    description = self._get_column_description_llm(
                        table, col_name, profile["column_statistics"][col_name]
                    )
                    profile["column_descriptions"][col_name] = description
                except Exception as e:
                    logger.debug(f"      Could not generate description for {col_name}: {e}")
            
            # Heavy LLM for table business context
            try:
                business_context = self._get_table_business_context_llm(
                    table, schema, profile["column_statistics"]
                )
                profile.update(business_context)
            except Exception as e:
                logger.debug(f"      Could not generate business context: {e}")
            
            self._dump_debug_data(
                f"profile_{table}.json",
                profile,
                f"Profile for table {table}"
            )
            
        except Exception as e:
            logger.error(f"Error profiling table {table}: {e}")
            profile["error"] = str(e)
        
        return profile
    
    def _get_table_statistics(self, workspace: str, table: str) -> Dict[str, Any]:
        """Get basic table statistics"""
        try:
            # Count rows
            kql = f"{table} | summarize Count=dcount(*)"
            results = self.azure_service.execute_query(kql, workspace_id=workspace)
            
            row_count = results[0]['Count'] if results else 0
            
            return {
                "row_count": row_count,
                "last_update": datetime.now().isoformat(),
                "estimated_size_bytes": None  # KQL doesn't provide direct size info
            }
        except Exception as e:
            logger.warning(f"Could not get table statistics for {table}: {e}")
            return {
                "row_count": None,
                "error": str(e)
            }
    
    def _get_column_statistics(
        self,
        workspace: str,
        table: str,
        column: str,
        col_type: str
    ) -> Dict[str, Any]:
        """Get statistics for a column"""
        try:
            # Basic stats: distinct count, null count, type
            kql = f"""
            {table}
            | summarize
                distinct_count=dcount({column}),
                null_count=countif({column} == ""),
                total_count=count()
            """
            
            results = self.azure_service.execute_query(kql, workspace_id=workspace)
            
            if not results:
                return {"error": "No results"}
            
            stats = results[0]
            total = stats.get('total_count', 0)
            distinct = stats.get('distinct_count', 0)
            
            # Determine if categorical
            is_categorical = False
            if total > 0:
                is_categorical = (distinct / total) < self.categorical_threshold
            
            col_stats = {
                "type": col_type,
                "distinct_count": distinct,
                "null_count": stats.get('null_count', 0),
                "is_categorical": is_categorical
            }
            
            # Get top values for categorical columns
            if is_categorical and distinct <= self.top_values_limit:
                try:
                    top_kql = f"""
                    {table}
                    | where {column} != ""
                    | summarize count() by {column}
                    | top {self.top_values_limit} by count_
                    """
                    top_results = self.azure_service.execute_query(top_kql, workspace_id=workspace)
                    col_stats["top_values"] = [r.get(column) for r in top_results]
                except Exception as e:
                    logger.debug(f"Could not get top values for {column}: {e}")
            
            return col_stats
        
        except Exception as e:
            logger.warning(f"Could not get statistics for column {column}: {e}")
            return {"error": str(e)}
    
    def _get_sample_rows(
        self,
        workspace: str,
        table: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get masked sample rows from table"""
        try:
            kql = f"{table} | limit {limit}"
            
            results = self.azure_service.execute_query(kql, workspace_id=workspace)
            
            # Apply masking to samples
            if self.governance.masking_enabled:
                results = self._mask_sensitive_data(results)
            
            return results
        
        except Exception as e:
            logger.warning(f"Could not fetch samples for {table}: {e}")
            return []
    
    def _mask_sensitive_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mask sensitive columns in data"""
        masked = []
        
        for row in data:
            masked_row = {}
            for key, value in row.items():
                if self.governance.is_sensitive_column(key):
                    masked_row[key] = "***MASKED***"
                else:
                    masked_row[key] = value
            masked.append(masked_row)
        
        return masked
    
    def _get_column_description_llm(
        self,
        table: str,
        column: str,
        stats: Dict[str, Any]
    ) -> str:
        """Generate column description using light LLM"""
        try:
            prompt = f"""
            Based on the column name and statistics, provide a brief one-line description
            of this database column.
            
            Table: {table}
            Column: {column}
            Type: {stats.get('type')}
            Distinct Values: {stats.get('distinct_count')}
            Categorical: {stats.get('is_categorical')}
            
            Provide a concise description.
            """
            
            schema = {
                "type": "object",
                "properties": {
                    "description": {"type": "string"}
                },
                "required": ["description"]
            }
            
            result = self.light_llm.get_structured_output(prompt, schema)
            return result.get("description", f"Column {column} in {table}")
        
        except Exception as e:
            logger.debug(f"LLM description generation failed for {column}: {e}")
            return f"Column {column}"
    
    def _get_table_business_context_llm(
        self,
        table: str,
        schema: List[Dict[str, Any]],
        column_stats: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate business context using heavy LLM"""
        try:
            columns_desc = ", ".join([col.get('Field') for col in schema[:10]])
            
            prompt = f"""
            Based on this table schema and column names, provide business context for
            this Azure Log Analytics table.
            
            Table: {table}
            Columns: {columns_desc}
            
            Provide:
            - business_purpose (one sentence)
            - data_domain (category: HR, Sales, IT, Security, etc.)
            - business_impact (HIGH, MEDIUM, LOW)
            - typical_queries (list of 3 example queries this table could answer)
            """
            
            schema_obj = {
                "type": "object",
                "properties": {
                    "business_purpose": {"type": "string"},
                    "data_domain": {"type": "string"},
                    "business_impact": {"type": "string"},
                    "typical_queries": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["business_purpose", "data_domain", "business_impact", "typical_queries"]
            }
            
            result = self.heavy_llm.get_structured_output(prompt, schema_obj)
            return result
        
        except Exception as e:
            logger.debug(f"LLM business context generation failed for {table}: {e}")
            return {
                "business_purpose": f"Data from {table} table",
                "data_domain": "Unknown",
                "business_impact": "MEDIUM",
                "typical_queries": []
            }
    
    def _profile_view(self, workspace: str, view: str) -> Dict[str, Any]:
        """Profile a saved query/view"""
        return {
            "view_name": view,
            "workspace": workspace,
            "type": "saved_query",
            "profile_timestamp": datetime.now().isoformat(),
            "note": "Saved query metadata - full profiling requires definition access"
        }
    
    def _infer_virtual_tables(
        self,
        workspace: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Infer virtual tables based on naming patterns and data"""
        virtual_tables = {}
        
        try:
            tables = list(profile_data.get("tables", {}).keys())
            
            # Simple heuristic: if multiple tables share a prefix, suggest an aggregated view
            prefixes = {}
            for table in tables:
                parts = table.split('_')
                if len(parts) > 1:
                    prefix = parts[0]
                    if prefix not in prefixes:
                        prefixes[prefix] = []
                    prefixes[prefix].append(table)
            
            # Create virtual tables for prefixes with multiple tables
            for prefix, tables_with_prefix in prefixes.items():
                if len(tables_with_prefix) > 1:
                    virtual_name = f"{prefix}_summary"
                    virtual_tables[virtual_name] = {
                        "type": "virtual_table",
                        "description": f"Aggregated view of {prefix} tables",
                        "source_tables": tables_with_prefix,
                        "suggested_purpose": f"Unified queries across {prefix}* tables"
                    }
        
        except Exception as e:
            logger.debug(f"Error inferring virtual tables: {e}")
        
        return virtual_tables
