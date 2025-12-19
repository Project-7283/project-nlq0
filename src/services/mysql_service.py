import mysql.connector
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Configure audit logger
audit_logger = logging.getLogger('mysql_audit')
audit_logger.setLevel(logging.INFO)
if not audit_logger.handlers:
    handler = logging.FileHandler('logs/mysql_audit.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    audit_logger.addHandler(handler)

class SecurityError(Exception):
    """Raised when a query violates data governance policies"""
    pass

class MySQLService:
    def __init__(self, host=None, user=None, password=None, database=None, governance_service=None):
        """
        Initialize MySQL service with optional data governance.
        
        Args:
            host: MySQL host
            user: MySQL user
            password: MySQL password
            database: Database name
            governance_service: Optional DataGovernanceService for query validation
        """
        self.db_config = {
            "host": host or os.getenv("MYSQL_HOST"),
            "user": user or os.getenv("MYSQL_USER"),
            "password": password or os.getenv("MYSQL_PASSWORD"),
            "database": database or os.getenv("MYSQL_DATABASE"),
        }

        self.conn = mysql.connector.connect(
            host=self.db_config.get("host"),
            user=self.db_config.get("user"),
            password=self.db_config.get("password"),
            database=self.db_config.get("database"),
            port=3306
        )
        
        # Data governance integration
        self.governance = governance_service
        if self.governance is None:
            # Lazy import to avoid circular dependencies
            try:
                from .data_governance_service import DataGovernanceService
                self.governance = DataGovernanceService()
            except Exception:
                self.governance = None
        
        # Enable/disable governance
        self.governance_enabled = os.getenv("DATA_GOVERNANCE_ENABLED", "true").lower() == "true"

    def execute_query(self, sql: str, asDict: bool = True, schema_context: Optional[Dict] = None):
        """
        Execute SQL query with data governance validation and result masking.
        
        Args:
            sql: SQL query to execute
            asDict: Return results as dictionaries
            schema_context: Optional schema context for governance validation
            
        Returns:
            Query results (masked if governance is enabled)
            
        Raises:
            SecurityError: If query violates data governance policies
        """
        # Data governance validation
        if self.governance_enabled and self.governance:
            is_valid, error_msg = self.governance.validate_query(sql, schema_context)
            if not is_valid:
                # Audit log blocked query
                self._audit_log("BLOCKED", sql, error_msg)
                raise SecurityError(error_msg)
        
        try:
            cursor = self.conn.cursor(dictionary=asDict)
            cursor.execute(sql)
            if not asDict:
                headers = [desc[0] for desc in cursor.description]
            result = cursor.fetchall()
            cursor.close()
            
            # Audit log successful query
            self._audit_log("SUCCESS", sql, f"Returned {len(result)} rows")
            
            # Mask sensitive data in results
            if asDict and self.governance_enabled and self.governance:
                result = self.governance.mask_results(result)
            
            if asDict:
                return result
            else:
                return result, headers
                
        except Exception as e:
            # Audit log failed query
            self._audit_log("ERROR", sql, str(e))
            raise
    
    def _audit_log(self, status: str, sql: str, message: str):
        """Log query execution for audit trail"""
        try:
            audit_logger.info(f"[{status}] SQL: {sql[:200]}... | Message: {message}")
        except Exception:
            pass  # Don't fail on logging errors
    
    def run_sql(self, sql):
        return self.conn.info_query(sql)
    
    def shutdown(self):
        self.conn.close()
