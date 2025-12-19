"""
Unit tests for DataGovernanceService

Tests sensitive column detection, query validation, SQL sanitization,
result masking, and partial masking strategies.
"""

import unittest
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.data_governance_service import DataGovernanceService


class TestDataGovernanceService(unittest.TestCase):
    """Test suite for DataGovernanceService"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Force enable governance for tests
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
        os.environ["DATA_GOVERNANCE_STRICT_MODE"] = "true"
        self.governance = DataGovernanceService()
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    # Test: Sensitive Column Detection
    def test_sensitive_column_detection(self):
        """Test that sensitive column names are detected correctly"""
        # Should be detected as sensitive
        sensitive_columns = [
            "user_password",
            "api_token",
            "secret_key",
            "password_hash",
            "credit_card_number",
            "ssn",
            "private_key",
            "auth_token"
        ]
        
        for col in sensitive_columns:
            with self.subTest(column=col):
                self.assertTrue(
                    self.governance.is_sensitive_column(col),
                    f"Column '{col}' should be detected as sensitive"
                )
    
    def test_non_sensitive_column_detection(self):
        """Test that non-sensitive columns are not flagged"""
        non_sensitive_columns = [
            "user_id",
            "email",  # email is partial mask, not fully sensitive
            "username",
            "created_at",
            "product_name",
            "order_total"
        ]
        
        for col in non_sensitive_columns:
            with self.subTest(column=col):
                # These should either not be sensitive or be partial mask only
                if col == "email":
                    self.assertTrue(self.governance.is_partial_mask_column(col))
                else:
                    self.assertFalse(
                        self.governance.is_sensitive_column(col),
                        f"Column '{col}' should not be detected as sensitive"
                    )
    
    # Test: Query Validation
    def test_validate_query_blocks_sensitive_columns(self):
        """Test that queries selecting sensitive columns are blocked"""
        sql = "SELECT user_id, email, password FROM users WHERE user_id = 1"
        is_valid, error = self.governance.validate_query(sql)
        
        self.assertFalse(is_valid, "Query with sensitive column should be blocked")
        self.assertIn("password", error.lower(), "Error should mention the sensitive column")
    
    def test_validate_query_allows_safe_columns(self):
        """Test that queries without sensitive columns are allowed"""
        sql = "SELECT user_id, username, created_at FROM users WHERE user_id = 1"
        is_valid, error = self.governance.validate_query(sql)
        
        self.assertTrue(is_valid, "Query without sensitive columns should be allowed")
        self.assertIsNone(error)
    
    def test_validate_query_blocks_select_star_strict_mode(self):
        """Test that SELECT * is blocked in strict mode when table has sensitive columns"""
        # Create schema context with sensitive columns
        schema_context = {
            "users": {
                "columns": ["user_id", "username", "password", "email"]
            }
        }
        
        sql = "SELECT * FROM users WHERE user_id = 1"
        is_valid, error = self.governance.validate_query(sql, schema_context)
        
        self.assertFalse(is_valid, "SELECT * should be blocked in strict mode")
        self.assertIn("SELECT *", error, "Error should mention SELECT *")
    
    # Test: SQL Sanitization
    def test_sanitize_sql_masks_sensitive_columns(self):
        """Test that SQL sanitization replaces sensitive columns with masked values"""
        sql = "SELECT user_id, username, password, api_token FROM users"
        sanitized = self.governance.sanitize_sql(sql)
        
        self.assertIn("'***MASKED***' AS password", sanitized)
        self.assertIn("'***MASKED***' AS api_token", sanitized)
        self.assertIn("user_id", sanitized)
        self.assertIn("username", sanitized)
    
    def test_sanitize_sql_preserves_aliases(self):
        """Test that SQL sanitization preserves column aliases"""
        sql = "SELECT user_id AS id, password AS pwd FROM users"
        sanitized = self.governance.sanitize_sql(sql)
        
        self.assertIn("'***MASKED***' AS pwd", sanitized)
        self.assertIn("user_id AS id", sanitized)
    
    # Test: Result Masking
    def test_mask_results_full_masking(self):
        """Test that sensitive values in results are fully masked"""
        results = [
            {"user_id": 1, "username": "john", "password": "secret123"},
            {"user_id": 2, "username": "jane", "password": "password456"}
        ]
        
        masked = self.governance.mask_results(results)
        
        self.assertEqual(masked[0]["password"], "***MASKED***")
        self.assertEqual(masked[1]["password"], "***MASKED***")
        self.assertEqual(masked[0]["username"], "john")  # Non-sensitive preserved
    
    def test_mask_results_partial_masking_email(self):
        """Test partial masking for email addresses"""
        results = [
            {"user_id": 1, "email": "john.doe@example.com"},
            {"user_id": 2, "email": "jane@company.org"}
        ]
        
        masked = self.governance.mask_results(results)
        
        # Emails should be partially masked
        self.assertIn("@example.com", masked[0]["email"])
        self.assertIn("***", masked[0]["email"])
        self.assertNotEqual(masked[0]["email"], "john.doe@example.com")
    
    def test_mask_results_partial_masking_phone(self):
        """Test partial masking for phone numbers"""
        results = [
            {"user_id": 1, "phone_number": "+1-555-123-4567"},
            {"user_id": 2, "mobile": "555-9876"}
        ]
        
        masked = self.governance.mask_results(results)
        
        # Phone numbers should be partially masked
        self.assertIn("***", masked[0]["phone_number"])
        self.assertNotEqual(masked[0]["phone_number"], "+1-555-123-4567")
    
    # Test: Schema Filtering
    def test_get_safe_columns_filters_sensitive(self):
        """Test that sensitive columns are filtered from schema"""
        table_columns = {
            "users": ["user_id", "username", "password", "email", "api_token"],
            "orders": ["order_id", "user_id", "total", "credit_card"]
        }
        
        safe_columns = self.governance.get_safe_columns(table_columns)
        
        # Sensitive columns should be removed
        self.assertNotIn("password", safe_columns["users"])
        self.assertNotIn("api_token", safe_columns["users"])
        self.assertNotIn("credit_card", safe_columns["orders"])
        
        # Safe columns should be preserved
        self.assertIn("user_id", safe_columns["users"])
        self.assertIn("username", safe_columns["users"])
        self.assertIn("order_id", safe_columns["orders"])
    
    # Test: Configuration
    def test_governance_can_be_disabled(self):
        """Test that governance can be disabled via environment variable"""
        os.environ["DATA_GOVERNANCE_ENABLED"] = "false"
        disabled_governance = DataGovernanceService()
        
        # Should not flag anything when disabled
        self.assertFalse(disabled_governance.is_sensitive_column("password"))
        
        sql = "SELECT password FROM users"
        is_valid, error = disabled_governance.validate_query(sql)
        self.assertTrue(is_valid)
        
        # Restore
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
    
    def test_custom_keywords_from_csv(self):
        """Test loading custom sensitive keywords from CSV"""
        # Create temporary CSV with custom keywords
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("keyword,mask_type\n")
            f.write("custom_secret,full\n")
            f.write("internal_key,full\n")
            csv_path = f.name
        
        try:
            custom_governance = DataGovernanceService(sensitive_keywords_csv=csv_path)
            
            # Custom keywords should be detected
            self.assertTrue(custom_governance.is_sensitive_column("custom_secret"))
            self.assertTrue(custom_governance.is_sensitive_column("internal_key"))
        finally:
            os.unlink(csv_path)
    
    # Test: Governance Summary
    def test_get_governance_summary(self):
        """Test that governance summary returns correct configuration"""
        summary = self.governance.get_governance_summary()
        
        self.assertIn("enabled", summary)
        self.assertIn("strict_mode", summary)
        self.assertIn("sensitive_keywords_count", summary)
        self.assertIn("policies", summary)
        
        self.assertTrue(summary["enabled"])
        self.assertTrue(summary["strict_mode"])
        self.assertGreater(summary["sensitive_keywords_count"], 0)


class TestPartialMasking(unittest.TestCase):
    """Test suite for partial masking strategies"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
        self.governance = DataGovernanceService()
    
    def test_partial_mask_email_standard(self):
        """Test partial masking of standard email"""
        masked = self.governance._partial_mask_value("user@example.com")
        self.assertIn("@example.com", masked)
        self.assertIn("***", masked)
        self.assertNotEqual(masked, "user@example.com")
    
    def test_partial_mask_email_long_local(self):
        """Test partial masking of email with long local part"""
        masked = self.governance._partial_mask_value("john.doe@company.com")
        self.assertIn("@company.com", masked)
        self.assertIn("***", masked)
        self.assertTrue(masked.startswith("j"))
    
    def test_partial_mask_phone_number(self):
        """Test partial masking of phone number"""
        masked = self.governance._partial_mask_value("+1-555-123-4567")
        self.assertIn("***", masked)
        # Should preserve some structure
        self.assertGreater(len(masked), 5)
    
    def test_partial_mask_short_value(self):
        """Test partial masking of very short values"""
        masked = self.governance._partial_mask_value("ab")
        self.assertEqual(masked, "***")


class TestQueryExtraction(unittest.TestCase):
    """Test suite for SQL query parsing and extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
        self.governance = DataGovernanceService()
    
    def test_extract_selected_columns_simple(self):
        """Test extraction of columns from simple SELECT"""
        sql = "SELECT user_id, username, email FROM users"
        columns = self.governance._extract_selected_columns(sql)
        
        self.assertIn("user_id", columns)
        self.assertIn("username", columns)
        self.assertIn("email", columns)
    
    def test_extract_selected_columns_with_aliases(self):
        """Test extraction of columns with aliases"""
        sql = "SELECT user_id AS id, username AS name FROM users"
        columns = self.governance._extract_selected_columns(sql)
        
        self.assertIn("user_id", columns)
        self.assertIn("username", columns)
    
    def test_extract_selected_columns_with_functions(self):
        """Test extraction of columns with SQL functions"""
        sql = "SELECT COUNT(user_id), MAX(created_at) FROM users"
        columns = self.governance._extract_selected_columns(sql)
        
        self.assertIn("user_id", columns)
        self.assertIn("created_at", columns)
    
    def test_extract_tables_from_query_simple(self):
        """Test extraction of table names from simple query"""
        sql = "SELECT * FROM users WHERE user_id = 1"
        tables = self.governance._extract_tables_from_query(sql)
        
        self.assertIn("users", tables)
    
    def test_extract_tables_from_query_with_joins(self):
        """Test extraction of table names from query with JOINs"""
        sql = "SELECT * FROM users JOIN orders ON users.id = orders.user_id"
        tables = self.governance._extract_tables_from_query(sql)
        
        self.assertIn("users", tables)
        self.assertIn("orders", tables)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
