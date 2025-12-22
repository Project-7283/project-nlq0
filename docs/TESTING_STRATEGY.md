# Testing Strategy & Quality Assurance

This document outlines the comprehensive testing strategy for the NLQ-to-SQL system, covering various testing levels and methodologies to ensure reliability, security, and performance.

## 1. Unit Testing (Completed)
- **Scope**: Individual modules and services in `src/`.
- **Tools**: `pytest`, `pytest-mock`, `pytest-asyncio`.
- **Coverage**: Tracked via `pytest-cov` with results published in Cobertura (XML) format.
- **Key Areas**:
    - `CircuitBreaker`: State transitions and rejection logic.
    - `Container`: Dependency injection and singleton integrity.
    - `DataGovernanceService`: Sensitive column detection and SQL sanitization.
    - `InferenceService`: Multi-provider LLM adapters and async handling.
    - `MySQLService`: Query execution and audit logging.
    - `SemanticGraph`: Pathfinding algorithms and graph manipulation.

## 2. Integration Testing (Implemented)
- **Objective**: Verify that multiple services work together correctly.
- **Key Tests**:
    - `test_db_to_graph_integration`: Verifies `DBSchemaReaderService` -> `SchemaGraphService` -> `SemanticGraph` flow.
    - `test_mysql_governance`: Verifies `MySQLService` + `DataGovernanceService` integration.
- **Location**: `tests/integration/`.

## 3. Functional Testing (Implemented)
- **Objective**: Validate the system against functional requirements (Natural Language to SQL conversion).
- **Key Tests**:
    - `test_nl_to_sql_flow`: Validates the complete LangGraph orchestration from intent to SQL.
- **Location**: `tests/functional/`.

## 4. Security Testing (Implemented)
- **Objective**: Ensure data privacy and protection against malicious queries.
- **Key Tests**:
    - `test_sql_injection_detection`: Tests blocking of sensitive columns and injection patterns.
    - `test_governance_masking_in_profiling`: Verifies that PII is masked during DB profiling.
    - `test_blocks_nested_subqueries`: Validates that governance cannot be bypassed via subqueries or unions.
- **Location**: `tests/security/`.

## 5. System Testing (End-to-End)
- **Objective**: Test the entire application from the user interface to the database.
- **Strategy**:
    - **API Testing**: Use `httpx` to test FastAPI endpoints in `src/api.py`.
    - **UI Testing**: Use tools like Selenium or Playwright to automate Streamlit UI interactions.
- **Location**: `tests/e2e/` (Planned).

## 6. Performance & Load Testing
- **Objective**: Measure system latency and stability under concurrent requests.
- **Strategy**:
    - **Latency Tracking**: Monitor `logs/performance.log` for LLM and DB execution times.
    - **Load Testing**: Use `Locust` or `JMeter` to simulate multiple users.
- **Resilience**: Verify that `CircuitBreaker` triggers correctly.

---

## Running Tests & Coverage

### Run All Tests
```bash
pytest tests/unit tests/integration tests/functional tests/security
```

### Run Specific Suite
```bash
pytest tests/security
```

### Generate Coverage Report
```bash
pytest --cov=src --cov-report=xml:coverage.xml --cov-report=term tests/unit
```
The `coverage.xml` file is in Cobertura format and can be integrated into CI/CD pipelines (e.g., Jenkins, GitHub Actions) for visualization.

**Current Status**: Unit test coverage is at **70%**, with all core services exceeding the 50% threshold.
