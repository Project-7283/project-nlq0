# Azure Log Analytics Services - Complete Documentation Index

## Quick Links

### 📋 Start Here
- **[AZURE_SERVICES_SUMMARY.md](./AZURE_SERVICES_SUMMARY.md)** - Executive summary of all created services
- **[AZURE_ARCHITECTURE.md](./docs/AZURE_ARCHITECTURE.md)** - Architecture diagrams and concept mapping
- **[AZURE_INTEGRATION_README.md](./docs/services/AZURE_INTEGRATION_README.md)** - Complete integration guide

### 💻 Implementation Files

| File | Purpose | Protocol |
|------|---------|----------|
| [src/services/database_protocols.py](./src/services/database_protocols.py) | Protocol definitions for interchangeability | Core architecture |
| [src/services/azure_log_analytics_service.py](./src/services/azure_log_analytics_service.py) | Query execution service | DatabaseExecutionProtocol |
| [src/services/azure_log_analytics_reader.py](./src/services/azure_log_analytics_reader.py) | Schema discovery service | DatabaseReaderProtocol |
| [src/services/azure_log_analytics_profiling_service.py](./src/services/azure_log_analytics_profiling_service.py) | Table profiling service | DatabaseProfilingServiceProtocol |
| [src/services/AZURE_SETUP_GUIDE.py](./src/services/AZURE_SETUP_GUIDE.py) | Code examples and quick reference | Examples |

### 📖 Service Documentation

| Service | Documentation | Purpose |
|---------|---|---------|
| Azure Log Analytics Service | [azure_log_analytics_service.md](./docs/services/azure_log_analytics_service.md) | Query execution with governance |
| Azure Log Analytics Reader | [azure_log_analytics_reader.md](./docs/services/azure_log_analytics_reader.md) | Schema discovery and metadata |
| Azure Log Analytics Profiler | [azure_log_analytics_profiling_service.md](./docs/services/azure_log_analytics_profiling_service.md) | Table statistics and semantics |
| Database Protocols | [database_protocols.md](./docs/services/database_protocols.md) | Protocol architecture and interchangeability |

### 🔧 Setup & Configuration

**Installation:**
```bash
pip install azure-identity azure-monitor-query
```

**Environment Variables:**
```bash
# Azure Authentication
AZURE_TENANT_ID="your-tenant-id"
AZURE_CLIENT_ID="your-client-id"
AZURE_CLIENT_SECRET="your-client-secret"
AZURE_LOG_ANALYTICS_WORKSPACE_ID="your-workspace-id"

# Governance & Profiling
DATA_GOVERNANCE_ENABLED="true"
SENSITIVE_COLUMNS_CSV="config/sensitive_keywords.csv"
CATEGORICAL_THRESHOLD="0.1"
PROFILING_SAMPLE_SIZE="10000"
```

See [AZURE_INTEGRATION_README.md](./docs/services/AZURE_INTEGRATION_README.md) for complete setup.

## What Was Created

### 4 Implementation Files

1. **database_protocols.py** (269 lines)
   - `DatabaseExecutionProtocol` - Query execution interface
   - `DatabaseReaderProtocol` - Schema discovery interface
   - `DatabaseProfilingServiceProtocol` - Table profiling interface
   - Enables drop-in replacement of services

2. **azure_log_analytics_service.py** (220 lines)
   - Drop-in replacement for `MySQLService`
   - KQL query execution with Azure Monitor Client
   - Sync/async execution modes
   - Data governance integration
   - Multi-cloud support (public, China, government)

3. **azure_log_analytics_reader.py** (380 lines)
   - Drop-in replacement for `DBSchemaReaderService`
   - Workspace and table discovery
   - Column schema inference from KQL
   - Schema caching
   - System table filtering

4. **azure_log_analytics_profiling_service.py** (520 lines)
   - Drop-in replacement for `DBProfilingService`
   - KQL-based statistics collection
   - Masked sample retrieval
   - LLM-powered semantic analysis
   - Virtual table inference

### 6 Documentation Files

1. **database_protocols.md** (470 lines)
   - Protocol definitions and usage
   - Interchangeability examples
   - Implementation checklist
   - Concept mapping across databases

2. **azure_log_analytics_service.md** (130 lines)
   - Service overview and methods
   - Data flow diagrams
   - Governance integration
   - Protocol implementation details

3. **azure_log_analytics_reader.md** (250 lines)
   - Service overview and algorithms
   - Concept mapping (Azure LA → MySQL)
   - Usage examples
   - Schema discovery details

4. **azure_log_analytics_profiling_service.md** (360 lines)
   - Profiling algorithms and configuration
   - Sample output format
   - Performance considerations
   - Comparison with MySQL profiler

5. **AZURE_INTEGRATION_README.md** (400 lines)
   - Complete setup guide (5 steps)
   - Quick start examples
   - Integration patterns
   - Troubleshooting guide
   - API reference

6. **AZURE_ARCHITECTURE.md** (400 lines)
   - Architecture diagrams
   - Interface compatibility matrix
   - Data flow comparison
   - Method mapping reference

### 1 Example/Reference File

**AZURE_SETUP_GUIDE.py** (300 lines)
- 10 practical code sections
- MySQL vs Azure comparison
- Identical interface examples
- Multi-database hybrid patterns
- Governance examples

## Key Features

### ✅ Protocol-Based Interchangeability
```python
# Same code works with MySQL or Azure!
def execute_query(db_service, query):
    return db_service.execute_query(query)

# Use with MySQL
execute_query(mysql_service, "SELECT * FROM users")

# Use with Azure - just swap service
execute_query(azure_service, "SecurityEvent | limit 100")
```

### ✅ Unified Data Governance
- Same `DataGovernanceService` for both
- Identical query validation
- Identical result masking
- Unified audit logging

### ✅ Concept Mapping
- Workspace ↔ Database
- Tables ↔ Tables
- Fields ↔ Columns
- Saved Queries ↔ Views
- KQL ↔ SQL

### ✅ Dual-LLM Integration
- Light LLM for column descriptions
- Heavy LLM for business context
- Both models used in profiling

### ✅ Data Privacy
- Sample data retrieved with masking
- Sensitive columns never exported
- Masking at query level (KQL WHERE)

### ✅ Comprehensive Documentation
- 6 documentation files
- 1 setup guide with examples
- Architecture diagrams
- Troubleshooting guide
- API reference

## Integration Workflow

### Step 1: Choose Service Type
```python
# Detect from environment
database_type = os.getenv("DATABASE_TYPE", "mysql")
```

### Step 2: Initialize Appropriate Service
```python
if database_type == "mysql":
    db_service = MySQLService(...)
    reader = DBSchemaReaderService(...)
    profiler = DBProfilingService(...)
else:  # azure
    db_service = AzureLogAnalyticsService(...)
    reader = AzureLogAnalyticsSchemaReader(...)
    profiler = AzureLogAnalyticsProfilingService(...)
```

### Step 3: Use Unified Interface
```python
# All the same regardless of database type
schema = reader.read_full_schema()
profile = profiler.profile_database("mydb")
results = db_service.execute_query(query)
```

## Performance Characteristics

| Operation | MySQL | Azure Log Analytics |
|---|---|---|
| Query execution | <1s | 1-3s |
| Schema discovery | <100ms/table | 1-5s total |
| Table profiling | Moderate | Moderate + cost |
| Result masking | O(R×C) | O(R×C) |
| Caching | Optional | Implemented |

## Files Summary

### Implementation (4 files, ~1400 lines)
- Protocols: 269 lines
- Services: 220 + 380 + 520 = 1120 lines
- Total: ~1400 lines of production code

### Documentation (6 files, ~2000 lines)
- Service docs: 130 + 250 + 360 = 740 lines
- Integration guide: 400 lines
- Protocol guide: 470 lines
- Architecture guide: 400 lines
- Total: ~2000 lines of documentation

### Examples (1 file, ~300 lines)
- Complete working examples with all patterns

## Usage Scenarios

### Scenario 1: Drop-in Replacement
Replace MySQL with Azure in existing pipeline without code changes.

### Scenario 2: Multi-Database Support
Use both MySQL and Azure in same application, routing based on query content.

### Scenario 3: Migration
Start with MySQL, gradually migrate tables to Azure Log Analytics.

### Scenario 4: Hybrid Analytics
Combine MySQL operational data with Azure Log Analytics security events.

### Scenario 5: Testing
Use mock implementations of protocols for unit testing.

## Architecture Principles

1. **Protocol-Driven Design** - All services implement standard protocols
2. **Concept Mapping** - Transparent mapping between database concepts
3. **Unified Governance** - Single governance service for all databases
4. **Query Language Abstraction** - Different query languages (SQL, KQL) but same interface
5. **Privacy-Focused** - Data masking at query level, never in transit
6. **Async-Ready** - Both sync and async execution modes
7. **Extensible** - Easy to add new database connectors

## Troubleshooting

See [AZURE_INTEGRATION_README.md#troubleshooting](./docs/services/AZURE_INTEGRATION_README.md) for:
- Authentication issues
- Query timeouts
- No results returned
- Permission problems

## API Reference

See [AZURE_INTEGRATION_README.md#api-reference](./docs/services/AZURE_INTEGRATION_README.md) for:
- `AzureLogAnalyticsService` methods
- `AzureLogAnalyticsSchemaReader` methods
- `AzureLogAnalyticsProfilingService` methods

## Code Examples

See [src/services/AZURE_SETUP_GUIDE.py](./src/services/AZURE_SETUP_GUIDE.py) for:
- Setup and initialization
- Query execution
- Schema discovery
- Table profiling
- Async operations
- Multi-database usage
- Governance integration
- Hybrid execution patterns

## Contributing

When extending these services:
1. Maintain protocol compliance
2. Use appropriate query language (KQL for Azure)
3. Handle service-specific differences
4. Test interchangeability
5. Document concept mappings

## Next Steps

1. **Review** [AZURE_SERVICES_SUMMARY.md](./AZURE_SERVICES_SUMMARY.md)
2. **Setup** Using [AZURE_INTEGRATION_README.md](./docs/services/AZURE_INTEGRATION_README.md)
3. **Study** Service documentation in [docs/services/](./docs/services/)
4. **Code** Using examples in [src/services/AZURE_SETUP_GUIDE.py](./src/services/AZURE_SETUP_GUIDE.py)
5. **Integrate** Into your NLQ pipeline
6. **Test** With your Azure workspace
7. **Optimize** Using profiling and performance tuning

## Support

- **Protocol Questions**: See [database_protocols.md](./docs/services/database_protocols.md)
- **Service Details**: See service-specific documentation
- **Setup Help**: See [AZURE_INTEGRATION_README.md](./docs/services/AZURE_INTEGRATION_README.md)
- **Code Examples**: See [AZURE_SETUP_GUIDE.py](./src/services/AZURE_SETUP_GUIDE.py)
- **Architecture**: See [AZURE_ARCHITECTURE.md](./docs/AZURE_ARCHITECTURE.md)

---

**Created:** January 28, 2026
**Status:** ✅ Complete - Ready for integration testing
**Total Files:** 11 (4 implementation + 6 documentation + 1 example)
**Total Lines:** ~3700 (1400 code + 2000 documentation + 300 examples)
