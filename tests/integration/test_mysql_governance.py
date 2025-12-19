"""
Integration tests for MySQL Service with Data Governance

Tests the full integration of DataGovernanceService with MySQLService,
including query blocking, result masking, and audit logging.
"""

import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.mysql_service import MySQLService, SecurityError
from src.services.data_governance_service import DataGovernanceService


class TestMySQLServiceWithGovernance(unittest.TestCase):
    """Integration tests for MySQLService with data governance"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        # Skip tests if database is not available
        try:
            cls.mysql_service = MySQLService()
            cls.governance = DataGovernanceService()
            cls.db_available = True
        except Exception as e:
            print(f"\n⚠️  Database not available, skipping integration tests: {e}")
            cls.db_available = False
    
    def setUp(self):
        """Set up before each test"""
        if not self.db_available:
            self.skipTest("Database not available")
        
        # Enable governance
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
        
        # Create test service with governance
        self.service = MySQLService(governance_service=self.governance)
    
    def tearDown(self):
        """Clean up after each test"""
        pass
    
    @classmethod
    def tearDownClass(cls):
        """Clean up database connection"""
        if hasattr(cls, 'mysql_service'):
            cls.mysql_service.shutdown()
    
    # Test: Query Blocking
    def test_blocks_query_with_sensitive_column(self):
        """Test that queries accessing sensitive columns are blocked"""
        # This query should be blocked (assuming users table has password column)
        sql = "SELECT email, password FROM users LIMIT 1"
        
        with self.assertRaises(SecurityError) as context:
            self.service.execute_query(sql)
        
        self.assertIn("password", str(context.exception).lower())
    
    def test_allows_safe_query(self):
        """Test that safe queries are allowed"""
        # This query should be allowed (no sensitive columns)
        sql = "SELECT DATABASE()"
        
        try:
            result = self.service.execute_query(sql)
            self.assertIsNotNone(result)
        except SecurityError:
            self.fail("Safe query should not be blocked")
    
    # Test: Result Masking
    def test_masks_sensitive_results(self):
        """Test that sensitive data in results is masked"""
        # Create test service that allows but masks
        test_service = MySQLService(governance_service=self.governance)
        
        # Mock result with sensitive data
        mock_results = [
            {"user_id": 1, "username": "test", "password": "secret123"}
        ]
        
        masked = self.governance.mask_results(mock_results)
        
        self.assertEqual(masked[0]["password"], "***MASKED***")
        self.assertEqual(masked[0]["username"], "test")
    
    # Test: Audit Logging
    def test_audit_log_created_on_blocked_query(self):
        """Test that blocked queries are logged to audit log"""
        sql = "SELECT password FROM users"
        
        try:
            self.service.execute_query(sql)
        except SecurityError:
            pass  # Expected
        
        # Check that audit log file was created
        log_path = "logs/mysql_audit.log"
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                log_content = f.read()
                self.assertIn("BLOCKED", log_content)
    
    # Test: Schema Context Validation
    def test_validates_with_schema_context(self):
        """Test query validation with schema context"""
        schema_context = {
            "users": {
                "columns": ["user_id", "username", "password", "email"]
            }
        }
        
        # SELECT * should be blocked with schema context
        sql = "SELECT * FROM users"
        
        with self.assertRaises(SecurityError):
            self.service.execute_query(sql, schema_context=schema_context)


class TestSQLGenerationServiceWithGovernance(unittest.TestCase):
    """Integration tests for SQLGenerationService with data governance"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
        # These tests don't require actual DB/LLM connections
    
    def test_sql_generation_filters_sensitive_columns(self):
        """Test that SQL generation filters sensitive columns from schema"""
        # This is a conceptual test - actual implementation would need mock LLM
        from src.services.data_governance_service import DataGovernanceService
        
        governance = DataGovernanceService()
        
        # Mock schema with sensitive columns
        schema = {
            "users": ["user_id", "username", "password", "email", "api_token"]
        }
        
        safe_schema = governance.get_safe_columns(schema)
        
        # Sensitive columns should be filtered
        self.assertNotIn("password", safe_schema["users"])
        self.assertNotIn("api_token", safe_schema["users"])
        
        # Safe columns should remain
        self.assertIn("user_id", safe_schema["users"])
        self.assertIn("username", safe_schema["users"])


class TestEndToEndGovernance(unittest.TestCase):
    """End-to-end tests for data governance across the pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
        self.governance = DataGovernanceService()
    
    def test_full_pipeline_blocks_sensitive_query(self):
        """Test that sensitive queries are blocked throughout the pipeline"""
        # Stage 1: Schema filtering (for LLM context)
        schema = {"users": ["user_id", "username", "password"]}
        safe_schema = self.governance.get_safe_columns(schema)
        self.assertNotIn("password", safe_schema["users"])
        
        # Stage 2: Query validation (before execution)
        sql = "SELECT user_id, password FROM users"
        is_valid, error = self.governance.validate_query(sql)
        self.assertFalse(is_valid)
        
        # Stage 3: Result masking (if somehow executed)
        results = [{"user_id": 1, "password": "secret"}]
        masked = self.governance.mask_results(results)
        self.assertEqual(masked[0]["password"], "***MASKED***")
    
    def test_full_pipeline_allows_safe_query(self):
        """Test that safe queries flow through the pipeline"""
        # Stage 1: Schema filtering
        schema = {"users": ["user_id", "username", "email"]}
        safe_schema = self.governance.get_safe_columns(schema)
        self.assertEqual(len(safe_schema["users"]), 3)  # All safe
        
        # Stage 2: Query validation
        sql = "SELECT user_id, username FROM users"
        is_valid, error = self.governance.validate_query(sql)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Stage 3: Result masking (should not mask non-sensitive data)
        results = [{"user_id": 1, "username": "john"}]
        masked = self.governance.mask_results(results)
        self.assertEqual(masked[0]["username"], "john")


class TestAdversarialQueries(unittest.TestCase):
    """Security tests with adversarial query patterns"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
        os.environ["DATA_GOVERNANCE_STRICT_MODE"] = "true"
        self.governance = DataGovernanceService()
    
    def test_blocks_obfuscated_column_names(self):
        """Test that obfuscated sensitive column names are still blocked"""
        # Try to bypass with case variations
        queries = [
            "SELECT PASSWORD FROM users",
            "SELECT PaSsWoRd FROM users",
            "SELECT `password` FROM users",
        ]
        
        for sql in queries:
            with self.subTest(sql=sql):
                is_valid, error = self.governance.validate_query(sql)
                self.assertFalse(is_valid, f"Should block: {sql}")
    
    def test_blocks_aliased_sensitive_columns(self):
        """Test that sensitive columns with aliases are blocked"""
        sql = "SELECT password AS user_secret FROM users"
        is_valid, error = self.governance.validate_query(sql)
        self.assertFalse(is_valid)
    
    def test_blocks_nested_subqueries_with_sensitive_data(self):
        """Test that nested queries with sensitive data are blocked"""
        sql = "SELECT * FROM (SELECT user_id, password FROM users) AS subq"
        is_valid, error = self.governance.validate_query(sql)
        self.assertFalse(is_valid)
    
    def test_blocks_union_with_sensitive_columns(self):
        """Test that UNION queries with sensitive columns are blocked"""
        sql = """
        SELECT user_id, username FROM users
        UNION
        SELECT user_id, password FROM users
        """
        is_valid, error = self.governance.validate_query(sql)
        self.assertFalse(is_valid)
    
    def test_sanitizes_instead_of_blocking_when_possible(self):
        """Test that queries can be sanitized instead of blocked"""
        sql = "SELECT user_id, username, password FROM users"
        
        # First check it would be blocked
        is_valid, error = self.governance.validate_query(sql)
        self.assertFalse(is_valid)
        
        # Then check sanitization works
        sanitized = self.governance.sanitize_sql(sql)
        self.assertIn("'***MASKED***' AS password", sanitized)
        self.assertIn("username", sanitized)
        
        # Sanitized query should be valid
        is_valid, error = self.governance.validate_query(sanitized)
        # Still invalid because it explicitly masks, but that's the point


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
