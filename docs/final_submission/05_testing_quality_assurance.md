# 5. Testing & Quality Assurance

## 5.1 Test Plan

The project employs a multi-layered testing strategy to ensure robustness and security.

1.  **Unit Testing**: Validates individual components (e.g., `CircuitBreaker`, `SemanticGraph`) in isolation using mocks.
2.  **Integration Testing**: Verifies that services talk to each other correctly (e.g., `DBSchemaReader` -> `SchemaGraphService`).
3.  **Functional Testing**: Tests the end-to-end flow from Natural Language to SQL using the LangGraph orchestrator.
4.  **Security Testing**: Specifically targets the `DataGovernanceService` to ensure it blocks injections and masks PII.

## 5.2 Test Cases (Sample)

| ID | Test Case Description | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | **NL-to-SQL Flow**: "Show count of users" | SQL: `SELECT COUNT(*) FROM users` | `SELECT COUNT(*) FROM users` | **PASS** |
| **TC-02** | **Schema Integration**: Build graph from DB | Graph contains `users` node and edges | Graph built successfully | **PASS** |
| **TC-03** | **Security**: Query requesting `password` | Query Blocked / SecurityError | Query Blocked | **PASS** |
| **TC-04** | **Injection**: `UNION SELECT password` | Query Blocked | Query Blocked | **PASS** |
| **TC-05** | **Profiling**: Masking in sample data | Result: `***MASKED***` | Result: `***MASKED***` | **PASS** |
| **TC-06** | **Graph Script**: Run `generate_graph_for_db.py` | JSON file created in `schemas/` | JSON file created | **PASS** |

## 5.3 Bug Reports & Fixes

### Bug 1: Schema Graph Initialization
*   **Issue**: The `SchemaGraphService` was failing in integration tests because it was initialized with a `Graph` object instead of a `dbname` string.
*   **Fix**: Updated the test fixture to pass the correct `dbname` argument, aligning the test with the implementation.

### Bug 2: Governance Bypass via Subqueries
*   **Issue**: Initial regex for sensitive columns missed keywords nested inside subqueries (e.g., `SELECT * FROM (SELECT password ...)`).
*   **Fix**: Enhanced `DataGovernanceService` with a robust regex pattern that detects sensitive identifiers anywhere in the SQL string, regardless of nesting.

### Bug 3: Profiling Data Leakage
*   **Issue**: The database profiling service was fetching raw sample data and masking it in Python, which is a security risk.
*   **Fix**: Refactored `_get_sample_rows` to generate SQL that masks data at the source (e.g., `SELECT '***MASKED***' as password`), ensuring PII never leaves the DB.

## 5.4 Validation Results
All **20 tests** across the Unit, Integration, Functional, and Security suites are currently **PASSING**.
