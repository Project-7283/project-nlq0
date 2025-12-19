"""
Data Governance Service

This service enforces data governance policies across the entire NLQ pipeline:
1. Query validation: Block queries that access sensitive columns
2. SQL sanitization: Rewrite SQL to mask sensitive columns
3. Result filtering: Mask sensitive data in query results

Usage:
- Integrate with MySQLService to block/sanitize queries before execution
- Integrate with SQLGenerationService to prevent generating sensitive queries
- Use in DBProfilingService to mask sample data
"""

import os
import re
import csv
from typing import List, Dict, Any, Optional, Tuple


class DataGovernanceService:
    """
    Enforces data governance and security policies for database access.
    Prevents unauthorized access to sensitive columns at query-time.
    """
    
    def __init__(self, sensitive_keywords_csv: Optional[str] = None):
        """
        Initialize data governance service.
        
        Args:
            sensitive_keywords_csv: Path to CSV file with sensitive keywords
        """
        self.default_keywords = [
            "password", "token", "secret", "hash", "api_key",
            "private_key", "salt", "ssn", "credit_card", "cvv",
            "pin", "auth", "credential", "key", "passwd"
        ]
        
        self.sensitive_keywords = self._load_keywords(sensitive_keywords_csv)
        self.enabled = os.getenv("DATA_GOVERNANCE_ENABLED", "true").lower() == "true"
        self.strict_mode = os.getenv("DATA_GOVERNANCE_STRICT_MODE", "true").lower() == "true"
        
        # Masking strategies by keyword pattern
        self.partial_mask_keywords = ["email", "phone", "mobile", "tel", "contact"]
        
        # Compile regex patterns for efficient matching
        self._compile_patterns()
    
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
                print(f"✓ Data Governance: Loaded {len(keywords)} sensitive keywords from {csv_path}")
                return keywords
            except Exception as e:
                print(f"⚠️  Data Governance: Error loading CSV ({e}), using defaults")
                return self.default_keywords
        
        return self.default_keywords
    
    def _compile_patterns(self):
        """Compile regex patterns for sensitive column detection"""
        # Create patterns without strict word boundaries to match compound words
        # e.g., "password" matches "user_password", "password_hash", "api_token" matches "token"
        self.patterns = [
            re.compile(re.escape(keyword), re.IGNORECASE)
            for keyword in self.sensitive_keywords
        ]
    
    def is_sensitive_column(self, column_name: str) -> bool:
        """
        Check if a column name indicates sensitive data.
        
        Args:
            column_name: Column name to check
            
        Returns:
            True if column is sensitive (excludes partial mask columns)
        """
        if not self.enabled:
            return False
        
        # Check if it's a partial mask column first (those are sensitive but handled differently)
        if self.is_partial_mask_column(column_name):
            return False  # Not "fully" sensitive
        
        column_lower = column_name.lower()
        return any(pattern.search(column_lower) for pattern in self.patterns)
    
    def is_partial_mask_column(self, column_name: str) -> bool:
        """
        Check if column should use partial masking instead of full masking.
        
        Args:
            column_name: Column name to check
            
        Returns:
            True if column should be partially masked
        """
        if not self.enabled:
            return False
        
        column_lower = column_name.lower()
        return any(keyword in column_lower for keyword in self.partial_mask_keywords)
    
    def validate_query(self, sql: str, schema_context: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate if a SQL query accesses sensitive columns.
        
        Args:
            sql: SQL query to validate
            schema_context: Optional schema context with table.column mappings
            
        Returns:
            Tuple of (is_valid, error_message)
            - If query is valid: (True, None)
            - If query is invalid: (False, "error message")
        """
        if not self.enabled:
            return True, None
        
        sql_upper = sql.upper()
        
        # Check for SELECT * (potentially exposes sensitive columns)
        if self.strict_mode and re.search(r'SELECT\s+\*', sql_upper):
            # Check if any table in the query might have sensitive columns
            if schema_context:
                tables = self._extract_tables_from_query(sql)
                for table in tables:
                    if table in schema_context:
                        columns = schema_context[table].get('columns', [])
                        sensitive_cols = [col for col in columns if self.is_sensitive_column(col)]
                        if sensitive_cols:
                            return False, (
                                f"Query blocked: SELECT * may expose sensitive columns in table '{table}': "
                                f"{', '.join(sensitive_cols)}. Please specify columns explicitly."
                            )
        
        # Extract column names from SELECT clause
        selected_columns = self._extract_selected_columns(sql)
        
        # Check if any selected column is sensitive
        sensitive_found = []
        for col in selected_columns:
            # Handle qualified names (table.column)
            col_name = col.split('.')[-1]
            if self.is_sensitive_column(col_name):
                sensitive_found.append(col)
        
        if sensitive_found:
            return False, (
                f"Query blocked: Access to sensitive columns denied: {', '.join(sensitive_found)}. "
                f"This query violates data governance policies."
            )
        
        return True, None
    
    def sanitize_sql(self, sql: str, mask_value: str = "'***MASKED***'") -> str:
        """
        Rewrite SQL to mask sensitive columns.
        
        Args:
            sql: Original SQL query
            mask_value: Value to use for masking
            
        Returns:
            Sanitized SQL query
        """
        if not self.enabled:
            return sql
        
        # Extract SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return sql
        
        select_clause = select_match.group(1)
        columns = [col.strip() for col in select_clause.split(',')]
        
        # Replace sensitive columns with masked values
        sanitized_columns = []
        for col in columns:
            col_clean = col.strip()
            # Handle aliases (e.g., "column AS alias")
            if ' AS ' in col_clean.upper():
                parts = re.split(r'\s+AS\s+', col_clean, flags=re.IGNORECASE)
                col_name = parts[0].strip()
                alias = parts[1].strip()
            else:
                col_name = col_clean
                alias = None
            
            # Check if sensitive
            base_name = col_name.split('.')[-1].strip('`"[]')
            if self.is_sensitive_column(base_name):
                if alias:
                    sanitized_columns.append(f"{mask_value} AS {alias}")
                else:
                    sanitized_columns.append(f"{mask_value} AS {base_name}")
            else:
                sanitized_columns.append(col)
        
        # Reconstruct query
        new_select = "SELECT " + ", ".join(sanitized_columns) + " FROM"
        return re.sub(r'SELECT\s+.*?\s+FROM', new_select, sql, count=1, flags=re.IGNORECASE | re.DOTALL)
    
    def mask_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mask sensitive columns in query results.
        Supports both full masking and partial masking strategies.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Results with sensitive values masked
        """
        if not self.enabled or not results:
            return results
        
        masked_results = []
        for row in results:
            masked_row = {}
            for key, value in row.items():
                # Check partial masking first (has priority)
                if self.is_partial_mask_column(key):
                    masked_row[key] = self._partial_mask_value(str(value))
                elif self.is_sensitive_column(key):
                    masked_row[key] = "***MASKED***"
                else:
                    masked_row[key] = value
            masked_results.append(masked_row)
        
        return masked_results
    
    def _partial_mask_value(self, value: str) -> str:
        """
        Apply partial masking to a value (e.g., email, phone).
        
        Examples:
            user@example.com → u***@example.com
            +1-555-1234 → +1-***-1234
            john.doe@company.com → j***@company.com
        """
        if not value or len(value) < 3:
            return "***"
        
        # Email pattern
        if '@' in value:
            parts = value.split('@')
            if len(parts) == 2:
                local = parts[0]
                domain = parts[1]
                if len(local) > 2:
                    return f"{local[0]}***@{domain}"
                return f"***@{domain}"
        
        # Phone pattern (keep first 3 and last 4 digits if long enough)
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) >= 7:
            non_digits = ''.join(c for c in value if not c.isdigit())
            # Keep format but mask middle digits
            masked_digits = digits[:3] + '***' + digits[-4:]
            # Reconstruct with non-digit characters
            return value[:3] + '***' + value[-4:]
        
        # Default: show first char + ***
        return f"{value[0]}***"
    
    def get_safe_columns(self, table_columns: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Filter out sensitive columns from schema.
        
        Args:
            table_columns: Dict mapping table names to column lists
            
        Returns:
            Dict with only non-sensitive columns
        """
        if not self.enabled:
            return table_columns
        
        safe_columns = {}
        for table, columns in table_columns.items():
            safe_columns[table] = [
                col for col in columns 
                if not self.is_sensitive_column(col)
            ]
        
        return safe_columns
    
    def _extract_selected_columns(self, sql: str) -> List[str]:
        """Extract column names from SELECT clause"""
        # Simple extraction - can be enhanced
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return []
        
        select_clause = select_match.group(1)
        
        # Handle SELECT *
        if '*' in select_clause:
            return ['*']
        
        # Split by comma and clean
        columns = []
        for col in select_clause.split(','):
            col = col.strip()
            # Remove AS aliases
            if ' AS ' in col.upper():
                col = re.split(r'\s+AS\s+', col, flags=re.IGNORECASE)[0].strip()
            # Remove function calls (e.g., COUNT(column))
            col = re.sub(r'\w+\((.*?)\)', r'\1', col)
            # Remove quotes and backticks
            col = col.strip('`"\'[]')
            if col:
                columns.append(col)
        
        return columns
    
    def _extract_tables_from_query(self, sql: str) -> List[str]:
        """Extract table names from SQL query"""
        tables = []
        
        # Find all table references after FROM and JOIN keywords
        # Match: FROM table, JOIN table, etc.
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r',\s*(\w+)'  # Comma-separated tables
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tables = []
        for table in tables:
            if table.lower() not in seen:
                seen.add(table.lower())
                unique_tables.append(table)
        
        return unique_tables
    
    def get_governance_summary(self) -> Dict[str, Any]:
        """Get governance configuration summary"""
        return {
            "enabled": self.enabled,
            "strict_mode": self.strict_mode,
            "sensitive_keywords_count": len(self.sensitive_keywords),
            "sample_keywords": self.sensitive_keywords[:5],
            "policies": {
                "block_select_star": self.strict_mode,
                "block_sensitive_columns": True,
                "mask_results": True
            }
        }


# Convenience function for quick checks
def check_column_sensitive(column_name: str, keywords_csv: Optional[str] = None) -> bool:
    """
    Quick check if a column is sensitive.
    
    Args:
        column_name: Column name to check
        keywords_csv: Optional path to keywords CSV
        
    Returns:
        True if sensitive
    """
    service = DataGovernanceService(keywords_csv)
    return service.is_sensitive_column(column_name)
