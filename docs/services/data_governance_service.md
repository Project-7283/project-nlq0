# Data Governance Service

## Overview

The `DataGovernanceService` enforces data security and governance policies throughout the NLQ-to-SQL pipeline. Unlike simple masking during profiling, this service provides **query-time security** to prevent unauthorized access to sensitive data.

## Architecture

```
User Query: "Show me passwords for all users"
         ↓
    Intent Extraction
         ↓
    SQL Generation: "SELECT email, password FROM users"
         ↓
    🔒 Data Governance Check ← BLOCKS QUERY HERE
         ↓
    ❌ Query Rejected: "Access to sensitive column 'password' denied"
```

## Key Features

### 1. **Query Validation**
Inspects SQL before execution and blocks queries accessing sensitive columns:
- Checks SELECT clauses for sensitive column names
- Blocks `SELECT *` in strict mode if table has sensitive columns
- Returns actionable error messages

### 2. **SQL Sanitization**
Rewrites SQL to mask sensitive columns:
```sql
-- Original
SELECT user_id, email, password FROM users;

-- Sanitized
SELECT user_id, email, '***MASKED***' AS password FROM users;
```

### 3. **Result Masking**
Masks sensitive values in query results as last line of defense.

### 4. **Schema Filtering**
Filters sensitive columns from schema context sent to LLM.

## Configuration

### Environment Variables

```bash
# Enable/disable governance
DATA_GOVERNANCE_ENABLED=true

# Strict mode: blocks SELECT * queries
DATA_GOVERNANCE_STRICT_MODE=true

# Path to sensitive keywords CSV
SENSITIVE_COLUMNS_CSV=config/sensitive_keywords.csv
```

### Sensitive Keywords CSV Format

```csv
keyword,mask_type
password,full
token,full
secret,full
api_key,full
email,partial
phone,partial
ssn,full
```

Currently only `keyword` column is used. The `mask_type` column is for future enhancements.

## Integration Points

### 1. MySQLService Integration

```python
from src.services.mysql_service import MySQLService
from src.services.data_governance_service import DataGovernanceService

class SecureMySQLService(MySQLService):
    def __init__(self, *args, governance_service=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.governance = governance_service or DataGovernanceService()
    
    def execute_query(self, sql: str, asDict=True):
        # Validate query before execution
        is_valid, error_msg = self.governance.validate_query(sql)
        if not is_valid:
            raise SecurityError(error_msg)
        
        # Execute query
        results = super().execute_query(sql, asDict)
        
        # Mask results
        return self.governance.mask_results(results)
```

### 2. SQLGenerationService Integration

```python
from src.services.sql_generation_service import SQLGenerationService
from src.services.data_governance_service import DataGovernanceService

class SecureSQLGenerationService(SQLGenerationService):
    def __init__(self, *args, governance_service=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.governance = governance_service or DataGovernanceService()
    
    def generate_sql(self, path, graph, user_query):
        # Filter sensitive columns from schema context
        schema_context = self._get_schema_context(path, graph)
        safe_schema = self.governance.get_safe_columns(schema_context)
        
        # Generate SQL with filtered schema
        sql = self._generate_with_llm(safe_schema, user_query)
        
        # Validate generated SQL
        is_valid, error_msg = self.governance.validate_query(sql, schema_context)
        if not is_valid:
            # Regenerate with stricter context or return error
            raise ValueError(f"Generated SQL violates governance: {error_msg}")
        
        return sql
```

### 3. DBProfilingService Integration

Already integrated - uses `is_sensitive_column()` to mask sample data.

## API Reference

### Class: `DataGovernanceService`

#### `__init__(sensitive_keywords_csv: Optional[str] = None)`
Initialize governance service with optional custom keywords.

#### `is_sensitive_column(column_name: str) -> bool`
Check if column name contains sensitive keywords.

#### `validate_query(sql: str, schema_context: Optional[Dict] = None) -> Tuple[bool, Optional[str]]`
Validate SQL query for governance compliance.

**Returns:**
- `(True, None)` if valid
- `(False, "error message")` if blocked

#### `sanitize_sql(sql: str, mask_value: str = "'***MASKED***'") -> str`
Rewrite SQL to mask sensitive columns.

#### `mask_results(results: List[Dict]) -> List[Dict]`
Mask sensitive values in query results.

#### `get_safe_columns(table_columns: Dict[str, List[str]]) -> Dict[str, List[str]]`
Filter sensitive columns from schema.

#### `get_governance_summary() -> Dict[str, Any]`
Get configuration summary.

## Usage Examples

### Basic Validation

```python
from src.services.data_governance_service import DataGovernanceService

governance = DataGovernanceService()

# Check column
if governance.is_sensitive_column("user_password"):
    print("Sensitive column detected!")

# Validate query
sql = "SELECT email, password FROM users"
is_valid, error = governance.validate_query(sql)
if not is_valid:
    print(f"Query blocked: {error}")
```

### SQL Sanitization

```python
sql = "SELECT user_id, email, password, api_token FROM users LIMIT 10"
sanitized = governance.sanitize_sql(sql)
print(sanitized)
# Output: SELECT user_id, email, '***MASKED***' AS password, '***MASKED***' AS api_token FROM users LIMIT 10
```

### Result Masking

```python
results = [
    {"user_id": 1, "email": "user@example.com", "password": "secret123"},
    {"user_id": 2, "email": "admin@example.com", "password": "admin456"}
]

masked = governance.mask_results(results)
# Output: [
#   {"user_id": 1, "email": "user@example.com", "password": "***MASKED***"},
#   {"user_id": 2, "email": "admin@example.com", "password": "***MASKED***"}
# ]
```

## Best Practices

1. **Always integrate at query execution level** - Not just in profiling
2. **Use strict mode in production** - Prevents accidental `SELECT *` exposure
3. **Customize keywords for your domain** - Add industry-specific sensitive terms
4. **Log blocked queries** - Monitor for potential security issues or user education needs
5. **Provide clear error messages** - Help users understand why queries are blocked

## Security Considerations

- **Defense in depth**: Governance is one layer - combine with DB permissions, encryption, audit logs
- **Keyword-based detection**: May not catch all cases (e.g., `user_pwd` vs `user_password`)
- **LLM bypass risk**: Prompt injection could generate non-sensitive-looking SQL that accesses sensitive data indirectly
- **Performance**: Regex matching is fast but scales with number of keywords

## Future Enhancements

- [ ] Column-level access control lists (ACLs)
- [ ] Row-level security policies
- [ ] Partial masking strategies (e.g., show last 4 digits)
- [ ] Audit logging of blocked queries
- [ ] ML-based sensitive data detection
- [ ] Integration with external policy engines (OPA, etc.)
