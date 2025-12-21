import mysql.connector
import os
import asyncio
from typing import List, Dict, Any, Optional
from src.utils.logging import audit_logger, app_logger as logger

class SecurityError(Exception):
    """Raised when a query violates data governance policies"""
    pass

class MySQLService:
    def __init__(self, host=None, user=None, password=None, database=None, governance_service=None):
        self.db_config = {
            "host": host or os.getenv("MYSQL_HOST"),
            "user": user or os.getenv("MYSQL_USER"),
            "password": password or os.getenv("MYSQL_PASSWORD"),
            "database": database or os.getenv("MYSQL_DATABASE"),
        }

        try:
            self.conn = mysql.connector.connect(
                host=self.db_config.get("host"),
                user=self.db_config.get("user"),
                password=self.db_config.get("password"),
                database=self.db_config.get("database"),
                port=3306
            )
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {str(e)}")
            raise e
        
        self.governance = governance_service
        self.governance_enabled = os.getenv("DATA_GOVERNANCE_ENABLED", "true").lower() == "true"

    def _execute_sync(self, sql: str, asDict: bool = True, schema_context: Optional[Dict] = None):
        if self.governance_enabled and self.governance:
            is_valid, error_msg = self.governance.validate_query(sql, schema_context)
            if not is_valid:
                self._audit_log("BLOCKED", sql, error_msg)
                raise SecurityError(error_msg)
        
        try:
            cursor = self.conn.cursor(dictionary=asDict)
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            
            self._audit_log("SUCCESS", sql, f"Returned {len(result)} rows")
            
            if asDict and self.governance_enabled and self.governance:
                result = self.governance.mask_results(result)
            
            return result
        except Exception as e:
            self._audit_log("ERROR", sql, str(e))
            raise e

    async def execute_query_async(self, sql: str, asDict: bool = True, schema_context: Optional[Dict] = None):
        return await asyncio.to_thread(self._execute_sync, sql, asDict, schema_context)

    def execute_query(self, sql: str, asDict: bool = True, schema_context: Optional[Dict] = None):
        return self._execute_sync(sql, asDict, schema_context)
    
    def _audit_log(self, status: str, sql: str, message: str):
        audit_logger.info(f"[{status}] SQL: {sql[:200]}... | Message: {message}")
    
    def shutdown(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
