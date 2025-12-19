# Testing Guide

## Overview

This project includes comprehensive unit and integration tests for the data governance and security features.

## Test Structure

```
tests/
├── unit/
│   └── test_data_governance.py      # Unit tests for DataGovernanceService
└── integration/
    └── test_mysql_governance.py     # Integration tests with MySQLService
```

## Running Tests

### Run All Tests

```bash
python run_tests.py
```

### Run Unit Tests Only

```bash
python run_tests.py --unit
```

### Run Integration Tests Only

```bash
python run_tests.py --integration
```

### Run Specific Test

```bash
python run_tests.py --test tests.unit.test_data_governance.TestDataGovernanceService
```

### Run Specific Test Method

```bash
python run_tests.py --test tests.unit.test_data_governance.TestDataGovernanceService.test_sensitive_column_detection
```

## Test Coverage

### Unit Tests (`test_data_governance.py`)

#### TestDataGovernanceService
- ✅ Sensitive column detection
- ✅ Non-sensitive column detection
- ✅ Query validation (blocks sensitive columns)
- ✅ Query validation (allows safe columns)
- ✅ SELECT * blocking in strict mode
- ✅ SQL sanitization (masks sensitive columns)
- ✅ SQL sanitization (preserves aliases)
- ✅ Result masking (full masking)
- ✅ Result masking (partial masking for emails)
- ✅ Result masking (partial masking for phones)
- ✅ Schema filtering
- ✅ Governance can be disabled
- ✅ Custom keywords from CSV
- ✅ Governance summary

#### TestPartialMasking
- ✅ Email partial masking
- ✅ Email with long local part
- ✅ Phone number partial masking
- ✅ Short value masking

#### TestQueryExtraction
- ✅ Extract columns from simple SELECT
- ✅ Extract columns with aliases
- ✅ Extract columns with functions
- ✅ Extract tables from simple query
- ✅ Extract tables from query with JOINs

### Integration Tests (`test_mysql_governance.py`)

#### TestMySQLServiceWithGovernance
- ✅ Blocks queries with sensitive columns
- ✅ Allows safe queries
- ✅ Masks sensitive results
- ✅ Creates audit logs for blocked queries
- ✅ Validates with schema context

#### TestSQLGenerationServiceWithGovernance
- ✅ SQL generation filters sensitive columns

#### TestEndToEndGovernance
- ✅ Full pipeline blocks sensitive queries
- ✅ Full pipeline allows safe queries

#### TestAdversarialQueries
- ✅ Blocks obfuscated column names
- ✅ Blocks aliased sensitive columns
- ✅ Blocks nested subqueries with sensitive data
- ✅ Blocks UNION with sensitive columns
- ✅ Sanitizes queries when possible

## Test Requirements

### For Unit Tests
- No external dependencies required
- Tests run in isolation with mocked data

### For Integration Tests
- Requires MySQL database connection
- Set environment variables in `.env`:
  ```
  MYSQL_HOST=localhost
  MYSQL_USER=root
  MYSQL_PASSWORD=password
  MYSQL_DATABASE=test_db
  ```
- Integration tests will skip if database is unavailable

## Writing New Tests

### Unit Test Template

```python
import unittest
from src.services.data_governance_service import DataGovernanceService

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.governance = DataGovernanceService()
    
    def test_my_feature(self):
        """Test description"""
        # Arrange
        input_data = "test"
        
        # Act
        result = self.governance.some_method(input_data)
        
        # Assert
        self.assertEqual(result, expected_value)

if __name__ == '__main__':
    unittest.main()
```

### Integration Test Template

```python
import unittest
from src.services.mysql_service import MySQLService
from src.services.data_governance_service import DataGovernanceService

class TestMyIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up shared resources"""
        try:
            cls.mysql_service = MySQLService()
            cls.db_available = True
        except Exception:
            cls.db_available = False
    
    def setUp(self):
        """Set up before each test"""
        if not self.db_available:
            self.skipTest("Database not available")
    
    def test_integration_feature(self):
        """Test integration"""
        # Test code here
        pass

if __name__ == '__main__':
    unittest.main()
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        MYSQL_HOST: 127.0.0.1
        MYSQL_USER: root
        MYSQL_PASSWORD: password
        MYSQL_DATABASE: test_db
      run: |
        python run_tests.py
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **AAA Pattern**: Arrange, Act, Assert
4. **Coverage**: Aim for >80% code coverage
5. **Fast**: Unit tests should run in milliseconds
6. **Mocking**: Mock external dependencies in unit tests
7. **Real Data**: Use real connections in integration tests (when available)

## Debugging Tests

### Run with verbose output

```bash
python -m unittest tests.unit.test_data_governance -v
```

### Run specific test with debugging

```python
if __name__ == '__main__':
    # Add breakpoint
    import pdb; pdb.set_trace()
    unittest.main()
```

### Check test discovery

```bash
python -m unittest discover tests/unit -v
```

## Coverage Report

Install coverage:
```bash
pip install coverage
```

Run with coverage:
```bash
coverage run -m unittest discover tests/
coverage report
coverage html  # Generate HTML report
```

View coverage:
```bash
open htmlcov/index.html
```

## Common Issues

### Issue: Tests fail with "Database not available"
**Solution**: Ensure MySQL is running and credentials in `.env` are correct. Integration tests will skip automatically if DB is unavailable.

### Issue: Import errors
**Solution**: Run tests from project root: `python run_tests.py`

### Issue: Audit log permissions
**Solution**: Ensure `logs/` directory exists and is writable: `mkdir -p logs && chmod 755 logs`

### Issue: Environment variables not loaded
**Solution**: Create `.env` file or set variables explicitly before running tests

## Next Steps

- [ ] Add coverage reporting
- [ ] Set up CI/CD pipeline
- [ ] Add performance benchmarks
- [ ] Add security scanning tests
- [ ] Add property-based testing (Hypothesis)
- [ ] Add mutation testing
