import os
import json
import csv
import logging
from typing import Optional, Dict, Any, List, Protocol
from datetime import datetime
from pathlib import Path


class InferenceServiceProtocol(Protocol):
    """Protocol for LLM inference services"""
    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]: ...


class DBReaderProtocol(Protocol):
    """Protocol for database reader services"""
    def get_tables(self, dbname: str) -> tuple: ...
    def get_table_schema(self, dbname: str, table: str) -> List[Dict[str, Any]]: ...
    def get_views(self, dbname: str) -> list: ...
    def get_view_schema(self, dbname: str, view: str) -> List[Dict[str, Any]]: ...


class MySQLServiceProtocol(Protocol):
    """Protocol for MySQL service"""
    def execute_query(self, sql: str, asDict: bool = True) -> List[Dict[str, Any]]: ...


class DataGovernanceConfig:
    """
    Configuration for data governance and sensitive data masking.
    Loads sensitive keywords from CSV file or uses defaults.
    """
    
    def __init__(self, sensitive_keywords_csv: Optional[str] = None):
        self.default_keywords = [
            "password", "token", "secret", "hash", "api_key",
            "private_key", "salt", "ssn", "credit_card", "cvv",
            "pin", "auth", "credential", "key"
        ]
        
        self.sensitive_keywords = self._load_keywords(sensitive_keywords_csv)
        self.masking_enabled = os.getenv("DATA_MASKING_ENABLED", "true").lower() == "true"
    
    def _load_keywords(self, csv_path: Optional[str]) -> List[str]:
        """Load sensitive keywords from CSV file"""
        if not csv_path:
            csv_path = os.getenv("SENSITIVE_COLUMNS_CSV")
        
        if csv_path and os.path.exists(csv_path):
            try:
                keywords = []
                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        keywords.append(row['keyword'].lower())
                print(f"Loaded {len(keywords)} sensitive keywords from {csv_path}")
                return keywords
            except Exception as e:
                print(f"Error loading sensitive keywords CSV: {e}. Using defaults.")
                return self.default_keywords
        
        return self.default_keywords
    
    def is_sensitive_column(self, column_name: str) -> bool:
        """Check if column name contains sensitive keywords"""
        if not self.masking_enabled:
            return False
        
        column_lower = column_name.lower()
        return any(keyword in column_lower for keyword in self.sensitive_keywords)


class DBProfilingService:
    """
    Service for profiling database tables and columns.
    Combines statistical analysis with LLM-powered semantic understanding.
    Supports data governance with sensitive column masking.
    """
    
    def __init__(
        self,
        db_reader: DBReaderProtocol,
        mysql_service: MySQLServiceProtocol,
        light_llm: InferenceServiceProtocol,
        heavy_llm: InferenceServiceProtocol,
        governance_config: Optional[DataGovernanceConfig] = None
    ):
        """
        Initialize profiling service.
        
        Args:
            db_reader: Database reader service (for schema metadata only)
            mysql_service: MySQL service for executing queries
            light_llm: Lightweight LLM for simple tasks (column descriptions)
            heavy_llm: Heavy LLM for complex tasks (business analysis)
            governance_config: Data governance configuration
        """
        self.db_reader = db_reader
        self.mysql_service = mysql_service
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
            print(f"  🐛 Debug dump: {filepath}")
        except Exception as e:
            print(f"  Warning: Could not write debug dump {filename}: {e}")
    
    def profile_database(self, dbname: str) -> Dict[str, Any]:
        """
        Profile entire database.
        
        Args:
            dbname: Database name
            
        Returns:
            Dictionary containing profile data for all tables
        """
        print(f"\n{'='*60}")
        print(f"Starting database profiling: {dbname}")
        print(f"{'='*60}\n")
        
        profile_data = {
            "database": dbname,
            "tables": {},
            "views": {},
            "profiling_timestamp": datetime.now().isoformat(),
            "governance_enabled": self.governance.masking_enabled
        }
        
        tables, views = self.db_reader.get_tables(dbname)
        
        # Profile tables
        for i, table in enumerate(tables, 1):
            print(f"[{i}/{len(tables)}] Profiling table: {table}")
            try:
                profile_data["tables"][table] = self.profile_table(dbname, table)
            except Exception as e:
                print(f"  ❌ Error profiling table {table}: {e}")
                profile_data["tables"][table] = {"error": str(e)}
        
        # Profile views
        print(f"\nProfiled {len(tables)} tables")
        
        # Add existing views
        for view in views:
            print(f"Processing view: {view}")
            try:
                profile_data["views"][view] = self.profile_view(dbname, view)
            except Exception as e:
                print(f"  ❌ Error profiling view {view}: {e}")
        
        # Infer virtual tables using LLM
        print("\nInferring virtual tables from data patterns...")
        virtual_tables = self._infer_virtual_tables(dbname, profile_data)
        profile_data["virtual_tables"] = virtual_tables
        
        print(f"\n{'='*60}")
        print(f"Profiling complete!")
        print(f"  Tables: {len(profile_data['tables'])}")
        print(f"  Views: {len(profile_data['views'])}")
        print(f"  Virtual Tables: {len(virtual_tables)}")
        print(f"{'='*60}\n")
        
        return profile_data
    
    def profile_table(self, dbname: str, table: str) -> Dict[str, Any]:
        """
        Profile a single table with statistics and LLM analysis.
        
        Args:
            dbname: Database name
            table: Table name
            
        Returns:
            Dictionary containing table profile
        """
        # 1. Get schema with DB comments
        columns = self.db_reader.get_table_schema(dbname, table)
        print(f"  📋 Retrieved {len(columns)} columns from schema")
        print(f"     Column names: {[col['Field'] for col in columns]}")
        self._dump_debug_data(
            f"{table}_01_schema_columns.json",
            columns,
            f"Columns retrieved from schema for table {table}"
        )
        table_comment = self._get_table_comment(dbname, table)
        
        # 2. Statistical profiling
        print(f"  📊 Computing statistics for {len(columns)} columns...")
        stats = self._compute_table_statistics(dbname, table, columns)
        print(f"     Statistics computed for {len(stats['columns'])} columns")
        self._dump_debug_data(
            f"{table}_02_statistics.json",
            stats,
            f"Statistical analysis for table {table}"
        )
        
        # 3. Get masked sample data for LLM
        print(f"  📥 Fetching {5} sample rows...")
        sample_rows = self._get_sample_rows(dbname, table, columns, limit=5)
        print(f"     Retrieved {len(sample_rows)} sample rows")
        self._dump_debug_data(
            f"{table}_03_sample_rows.json",
            sample_rows,
            f"Sample rows for table {table} (with masking)"
        )
        
        # 4. LLM-powered business analysis (HEAVY)
        print(f"  🤖 Running heavy LLM business analysis...")
        business_context = self._analyze_table_business_context(
            table, columns, sample_rows, table_comment
        )
        print(f"     Business context keys: {list(business_context.keys())}")
        self._dump_debug_data(
            f"{table}_04_business_context.json",
            business_context,
            f"Heavy LLM business analysis for table {table}"
        )
        
        # 5. LLM-powered column descriptions (LIGHT, batched)
        print(f"  💡 Running light LLM column semantic analysis...")
        column_descriptions = self._analyze_column_semantics(
            table, columns, stats
        )
        print(f"     Descriptions generated for {len(column_descriptions)} columns")
        self._dump_debug_data(
            f"{table}_05_column_descriptions.json",
            column_descriptions,
            f"Light LLM column semantic analysis for table {table}"
        )
        
        result = {
            "row_count": stats["row_count"],
            "table_comment": table_comment,
            "columns": columns,
            "column_statistics": stats["columns"],
            "column_descriptions": column_descriptions,
            **business_context
        }
        print(f"  ✅ Profile complete. Keys in result: {list(result.keys())}")
        print(f"     Columns in result: {len(result['columns'])}")
        self._dump_debug_data(
            f"{table}_06_final_profile.json",
            result,
            f"Final profile result for table {table}"
        )
        return result
    
    def profile_view(self, dbname: str, view: str) -> Dict[str, Any]:
        """
        Profile a database view.
        
        Args:
            dbname: Database name
            view: View name
            
        Returns:
            Dictionary containing view profile
        """
        view_schema = self.db_reader.get_view_schema(dbname, view)
        view_comment = self._get_table_comment(dbname, view)
        
        # Extract CREATE VIEW statement
        create_statement = view_schema[0].get('Create View', '') if view_schema else ''
        
        return {
            "type": "view",
            "view_comment": view_comment,
            "create_statement": create_statement,
            "description": view_comment or "Database view"
        }
    
    def _get_table_comment(self, dbname: str, table: str) -> str:
        """Get table or view comment from information_schema"""
        query = f"""
            SELECT TABLE_COMMENT
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table}'
        """
        try:
            result = self.mysql_service.execute_query(query)
            if result and len(result) > 0:
                comment = result[0].get('TABLE_COMMENT', '')
                return comment if comment else ''
        except Exception as e:
            print(f"  Warning: Could not fetch table comment: {e}")
        return ''
    
    def _compute_table_statistics(
        self, 
        dbname: str, 
        table: str, 
        columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute statistical metadata for table and columns.
        
        Args:
            dbname: Database name
            table: Table name
            columns: List of column definitions
            
        Returns:
            Dictionary with row count and column statistics
        """
        row_count = self._get_row_count(dbname, table)
        print(f"     Total rows: {row_count}")
        
        column_stats = {}
        for col in columns:
            col_name = col['Field']
            print(f"     Processing column: {col_name}")
            
            # Check if sensitive
            is_sensitive = self.governance.is_sensitive_column(col_name)
            if is_sensitive:
                print(f"       ⚠️  Sensitive column detected: {col_name}")
            
            if is_sensitive:
                column_stats[col_name] = {
                    "is_sensitive": True,
                    "distinct_count": None,
                    "sample_values": []
                }
                continue
            
            # Compute stats
            try:
                distinct_count = self._get_distinct_count(dbname, table, col_name)
                null_pct = self._get_null_percentage(dbname, table, col_name, row_count)
                cardinality = distinct_count / row_count if row_count > 0 else 0
                
                is_categorical = cardinality < self.categorical_threshold
                if is_categorical:
                    print(f"       📊 Categorical column: {col_name} (cardinality: {cardinality:.4f})")
                
                column_stats[col_name] = {
                    "is_sensitive": False,
                    "distinct_count": distinct_count,
                    "null_percentage": round(null_pct, 2),
                    "cardinality_ratio": round(cardinality, 4),
                    "is_categorical": is_categorical
                }
                
                # Get value distribution if categorical
                if is_categorical and distinct_count > 0:
                    column_stats[col_name]["value_distribution"] = \
                        self._get_value_distribution(dbname, table, col_name, self.top_values_limit)
                    column_stats[col_name]["sample_values"] = \
                        list(column_stats[col_name]["value_distribution"].keys())
            except Exception as e:
                print(f"    Warning: Error computing stats for {col_name}: {e}")
                column_stats[col_name] = {"error": str(e)}
        
        return {
            "row_count": row_count,
            "columns": column_stats
        }
    
    def _get_row_count(self, dbname: str, table: str) -> int:
        """Get total row count for table"""
        query = f"SELECT COUNT(*) as cnt FROM {dbname}.{table}"
        try:
            result = self.mysql_service.execute_query(query)
            return result[0]['cnt'] if result else 0
        except Exception as e:
            print(f"    Warning: Could not get row count: {e}")
            return 0
    
    def _get_distinct_count(self, dbname: str, table: str, column: str) -> int:
        """Get distinct value count for column"""
        query = f"SELECT COUNT(DISTINCT `{column}`) as cnt FROM {dbname}.{table}"
        try:
            result = self.mysql_service.execute_query(query)
            return result[0]['cnt'] if result else 0
        except Exception as e:
            print(f"    Warning: Could not get distinct count for {column}: {e}")
            return 0
    
    def _get_null_percentage(self, dbname: str, table: str, column: str, total_rows: int) -> float:
        """Get null percentage for column"""
        if total_rows == 0:
            return 0.0
        
        query = f"SELECT COUNT(*) as cnt FROM {dbname}.{table} WHERE `{column}` IS NULL"
        try:
            result = self.mysql_service.execute_query(query)
            null_count = result[0]['cnt'] if result else 0
            return (null_count / total_rows) * 100
        except Exception as e:
            print(f"    Warning: Could not get null percentage for {column}: {e}")
            return 0.0
    
    def _get_value_distribution(
        self, 
        dbname: str, 
        table: str, 
        column: str, 
        top_n: int
    ) -> Dict[str, int]:
        """Get top N value distribution for categorical column"""
        query = f"""
            SELECT `{column}`, COUNT(*) as cnt
            FROM {dbname}.{table}
            WHERE `{column}` IS NOT NULL
            GROUP BY `{column}`
            ORDER BY cnt DESC
            LIMIT {top_n}
        """
        try:
            result = self.mysql_service.execute_query(query)
            return {str(row[column]): row['cnt'] for row in result}
        except Exception as e:
            print(f"    Warning: Could not get value distribution for {column}: {e}")
            return {}
    
    def _get_sample_rows(
        self, 
        dbname: str, 
        table: str, 
        columns: List[Dict[str, Any]], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get sample rows with sensitive column masking.
        Uses explicit column selection with SQL fragments for masking.
        
        Args:
            dbname: Database name
            table: Table name
            columns: List of column definitions
            limit: Number of sample rows
            
        Returns:
            List of sample row dictionaries
        """
        # Build SELECT with explicit columns and masking
        select_parts = []
        for col in columns:
            col_name = col['Field']
            if self.governance.is_sensitive_column(col_name):
                # Use SQL fragment for masking
                select_parts.append(f"'***MASKED***' AS `{col_name}`")
            else:
                select_parts.append(f"`{col_name}`")
        
        select_clause = ", ".join(select_parts)
        query = f"SELECT {select_clause} FROM {dbname}.{table} LIMIT {limit}"
        
        try:
            result = self.mysql_service.execute_query(query)
            return result if result else []
        except Exception as e:
            print(f"    Warning: Could not fetch sample rows: {e}")
            return []
    
    def _analyze_table_business_context(
        self,
        table: str,
        columns: List[Dict[str, Any]],
        sample_rows: List[Dict[str, Any]],
        table_comment: str
    ) -> Dict[str, Any]:
        """
        Use HEAVY LLM for business context analysis.
        
        Args:
            table: Table name
            columns: Column definitions
            sample_rows: Sample data rows
            table_comment: DB-level table comment
            
        Returns:
            Dictionary with business context
        """
        schema_str = self._format_schema_for_llm(columns)
        samples_str = self._format_samples_for_llm(sample_rows)
        
        json_schema = {
            "type": "object",
            "properties": {
                "business_purpose": {"type": "string"},
                "data_domain": {"type": "string"},
                "business_impact": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                "description": {"type": "string"},
                "typical_queries": {"type": "array", "items": {"type": "string"}},
                "related_business_processes": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["business_purpose", "description"]
        }
        
        prompt = f"""
Analyze this database table and provide structured business metadata.

Table Name: {table}
{f"Database Comment: {table_comment}" if table_comment else ""}

Schema:
{schema_str}

Sample Rows (first 5):
{samples_str}

Provide comprehensive business context for this table including:
- What business function it serves
- What domain it belongs to (Sales, HR, Finance, etc.)
- Business impact level (HIGH/MEDIUM/LOW)
- Clear description
- 3-5 typical natural language queries users might ask
- Related business processes
"""
        
        try:
            result = self.heavy_llm.get_structured_output(prompt, json_schema)
            return result if result else {}
        except Exception as e:
            print(f"    Warning: LLM business analysis failed: {e}")
            return {
                "business_purpose": "Unknown",
                "description": table_comment or f"Database table: {table}"
            }
    
    def _analyze_column_semantics(
        self,
        table: str,
        columns: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> Dict[str, Dict[str, str]]:
        """
        Use LIGHT LLM for column semantic descriptions (batched).
        
        Args:
            table: Table name
            columns: Column definitions
            stats: Column statistics
            
        Returns:
            Dictionary mapping column names to descriptions
        """
        # Prepare batch prompt for all non-sensitive columns
        column_info = []
        for col in columns:
            col_name = col['Field']
            col_type = col['Type']
            col_comment = col.get('Comment', '')
            
            if self.governance.is_sensitive_column(col_name):
                continue
            
            col_stats = stats["columns"].get(col_name, {})
            sample_vals = col_stats.get("sample_values", [])
            
            column_info.append({
                "name": col_name,
                "type": col_type,
                "comment": col_comment,
                "is_categorical": col_stats.get("is_categorical", False),
                "samples": sample_vals[:5]
            })
        
        if not column_info:
            return {}
        
        json_schema = {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "semantic_meaning": {"type": "string"},
                    "business_relevance": {"type": "string"}
                }
            }
        }
        
        prompt = f"""
For each column in table '{table}', provide a concise semantic description.

Columns:
{json.dumps(column_info, indent=2)}

Return a JSON object where keys are column names and values contain:
- description: What the column stores
- semantic_meaning: The semantic type/meaning
- business_relevance: How it's used in business context
"""
        
        try:
            result = self.light_llm.get_structured_output(prompt, json_schema)
            return result if result else {}
        except Exception as e:
            print(f"    Warning: LLM column analysis failed: {e}")
            return {}
    
    def _infer_virtual_tables(
        self,
        dbname: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Use HEAVY LLM to infer useful virtual tables/views.
        
        Args:
            dbname: Database name
            profile_data: Existing profile data
            
        Returns:
            Dictionary of virtual table definitions
        """
        # Build context about tables
        table_context = []
        for table_name, table_profile in profile_data["tables"].items():
            if "error" in table_profile:
                continue
            
            table_context.append({
                "table": table_name,
                "purpose": table_profile.get("business_purpose", "Unknown"),
                "row_count": table_profile.get("row_count", 0),
                "key_columns": [col['Field'] for col in table_profile.get("columns", [])[:5]]
            })
        
        if not table_context:
            return {}
        
        json_schema = {
            "type": "object",
            "properties": {
                "virtual_tables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "suggested_sql": {"type": "string"},
                            "use_case": {"type": "string"}
                        },
                        "required": ["name", "description", "suggested_sql"]
                    }
                }
            }
        }
        
        prompt = f"""
Based on these database tables, suggest 2-3 useful virtual views that would help answer common business questions.

Database: {dbname}
Tables:
{json.dumps(table_context, indent=2)}

Suggest virtual tables (views) that:
1. Combine related tables for common queries
2. Pre-aggregate data for analytics
3. Simplify complex relationships

For each virtual table, provide:
- name: A clear, descriptive name
- description: What it represents
- suggested_sql: A CREATE VIEW statement
- use_case: Example queries this helps answer

Limit to 2-3 most valuable virtual tables.
"""
        
        try:
            result = self.heavy_llm.get_structured_output(prompt, json_schema)
            virtual_tables = result.get("virtual_tables", [])
            
            # Convert array to dict
            return {
                vt["name"]: {
                    "type": "virtual_table",
                    "description": vt["description"],
                    "suggested_sql": vt["suggested_sql"],
                    "use_case": vt.get("use_case", "")
                }
                for vt in virtual_tables
            }
        except Exception as e:
            print(f"    Warning: Virtual table inference failed: {e}")
            return {}
    
    def _format_schema_for_llm(self, columns: List[Dict[str, Any]]) -> str:
        """Format column schema for LLM consumption"""
        lines = []
        for col in columns:
            comment = col.get('Comment', '')
            comment_str = f" -- {comment}" if comment else ""
            lines.append(f"  {col['Field']} ({col['Type']}){comment_str}")
        return "\n".join(lines)
    
    def _format_samples_for_llm(self, sample_rows: List[Dict[str, Any]]) -> str:
        """Format sample rows for LLM consumption"""
        if not sample_rows:
            return "No sample data available"
        
        lines = []
        for i, row in enumerate(sample_rows, 1):
            row_str = ", ".join([f"{k}={v}" for k, v in row.items()])
            lines.append(f"  Row {i}: {row_str}")
        return "\n".join(lines)
