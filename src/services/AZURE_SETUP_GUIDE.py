"""
Quick Reference: Using Azure Log Analytics Services

This guide shows how to use Azure Log Analytics services as drop-in replacements
for MySQL services in the NLQ pipeline.
"""

# ============================================================================
# 1. SETUP AND INITIALIZATION
# ============================================================================

# MySQL Setup (Original)
from src.services.mysql_service import MySQLService
from src.services.db_reader import DBSchemaReaderService
from src.services.db_profiling_service import DBProfilingService as MySQLProfilingService
from src.services.data_governance_service import DataGovernanceService

# MySQL initialization
mysql_governance = DataGovernanceService("config/sensitive_keywords.csv")
mysql_service = MySQLService(
    host="localhost",
    user="root",
    password="secret",
    database="mydb",
    governance_service=mysql_governance
)
mysql_reader = DBSchemaReaderService(mysql_service)
mysql_profiler = MySQLProfilingService(
    db_reader=mysql_reader,
    mysql_service=mysql_service,
    light_llm=light_llm_model,
    heavy_llm=heavy_llm_model
)

# ============================================================================

# Azure Log Analytics Setup (New - Drop-in Replacement)
from src.services.azure_log_analytics_service import AzureLogAnalyticsService
from src.services.azure_log_analytics_reader import AzureLogAnalyticsSchemaReader
from src.services.azure_log_analytics_profiling_service import (
    AzureLogAnalyticsProfilingService,
    DataGovernanceConfig
)

# Azure initialization - uses same governance config
azure_governance = DataGovernanceConfig("config/sensitive_keywords.csv")
azure_service = AzureLogAnalyticsService(
    workspace_id="<workspace-id>",
    governance_service=azure_governance  # Same governance service!
)
azure_reader = AzureLogAnalyticsSchemaReader(azure_service)
azure_profiler = AzureLogAnalyticsProfilingService(
    azure_reader=azure_reader,
    azure_service=azure_service,
    light_llm=light_llm_model,
    heavy_llm=heavy_llm_model,
    governance_config=azure_governance
)

# ============================================================================
# 2. QUERY EXECUTION - IDENTICAL INTERFACE
# ============================================================================

# Both services implement DatabaseExecutionProtocol
# Use the same code for both!

def execute_nlq_query(db_service, query_string, schema_context=None):
    """Execute query on any database service"""
    results = db_service.execute_query(
        query_string,
        asDict=True,
        schema_context=schema_context
    )
    return results

# Works with MySQL
mysql_results = execute_nlq_query(mysql_service, "SELECT * FROM users")

# Works with Azure Log Analytics - just swap the service!
azure_results = execute_nlq_query(azure_service, "SecurityEvent | limit 100")

# ============================================================================
# 3. SCHEMA DISCOVERY - IDENTICAL INTERFACE
# ============================================================================

# Both readers implement DatabaseReaderProtocol
# Use the same code for both!

def discover_database_schema(reader):
    """Discover schema on any database"""
    databases = reader.get_databases()
    full_schema = reader.read_full_schema()
    return {
        "databases": databases,
        "schema": full_schema
    }

# Works with MySQL
mysql_schema = discover_database_schema(mysql_reader)

# Works with Azure Log Analytics - just swap the reader!
azure_schema = discover_database_schema(azure_reader)

# ============================================================================
# 4. TABLE PROFILING - IDENTICAL INTERFACE
# ============================================================================

# Both profilers implement DatabaseProfilingServiceProtocol
# Use the same code for both!

def profile_for_vector_embedding(profiler, database_name):
    """Profile database for vector store embedding"""
    profile = profiler.profile_database(database_name)
    # Generate embeddings from profile...
    return profile

# Works with MySQL
mysql_profile = profile_for_vector_embedding(mysql_profiler, "mydb")

# Works with Azure Log Analytics - just swap the profiler!
# For Azure, use workspace ID instead of database name
azure_profile = profile_for_vector_embedding(azure_profiler, "<workspace-id>")

# ============================================================================
# 5. ASYNC EXECUTION - IDENTICAL INTERFACE
# ============================================================================

import asyncio

async def execute_multiple_queries(db_service, queries):
    """Execute multiple queries asynchronously"""
    tasks = [
        db_service.execute_query_async(q)
        for q in queries
    ]
    results = await asyncio.gather(*tasks)
    return results

# Works with both MySQL and Azure Log Analytics!
# Just pass the appropriate service

# ============================================================================
# 6. MULTI-DATABASE SUPPORT - HYBRID SETUP
# ============================================================================

# You can use MySQL and Azure Log Analytics together in the same pipeline!

class HybridNLQExecutor:
    """Execute NLQ against either MySQL or Azure Log Analytics"""
    
    def __init__(self, mysql_service, azure_service):
        self.mysql_service = mysql_service
        self.azure_service = azure_service
    
    def execute(self, nlq, target_database="auto"):
        """
        Execute NLQ query
        target_database: "mysql", "azure", or "auto" (detect based on keywords)
        """
        if target_database == "mysql":
            db_service = self.mysql_service
            # Generate SQL query
            sql = self.generate_sql(nlq)
            return db_service.execute_query(sql)
        
        elif target_database == "azure":
            db_service = self.azure_service
            # Generate KQL query
            kql = self.generate_kql(nlq)
            return db_service.execute_query(kql)
        
        elif target_database == "auto":
            # Detect based on keywords in NLQ
            if self._has_security_keywords(nlq):
                return self.execute(nlq, target_database="azure")
            else:
                return self.execute(nlq, target_database="mysql")
    
    def _has_security_keywords(self, nlq):
        """Detect if NLQ is about security events"""
        keywords = {"security", "event", "logon", "authentication", "failed"}
        return any(kw in nlq.lower() for kw in keywords)

# Usage
hybrid_executor = HybridNLQExecutor(mysql_service, azure_service)

# Auto-detects: routes to Azure
security_results = hybrid_executor.execute(
    "Show me failed login attempts",
    target_database="auto"
)

# Explicit: routes to MySQL
user_results = hybrid_executor.execute(
    "List all active users",
    target_database="mysql"
)

# ============================================================================
# 7. GOVERNANCE - UNIFIED ACROSS BOTH
# ============================================================================

# Both MySQL and Azure services use the same governance policies!
# Sensitive columns are masked the same way

# Configuration: config/sensitive_keywords.csv
# - password
# - ssn
# - credit_card
# - api_key
# ... etc

# Both services automatically:
# 1. Validate queries before execution (block if accessing sensitive columns)
# 2. Mask sensitive columns in results
# 3. Audit log all operations

# Example: Query accessing sensitive data
try:
    # MySQL attempt
    mysql_results = mysql_service.execute_query(
        "SELECT user_id, password_hash FROM users"  # Will block!
    )
except SecurityError:
    print("Query blocked by governance policy")

try:
    # Azure attempt
    azure_results = azure_service.execute_query(
        "SecurityEvent | where TargetUserName == 'admin'"  # May be blocked
    )
except SecurityError:
    print("Query blocked by governance policy")

# ============================================================================
# 8. ENVIRONMENT CONFIGURATION
# ============================================================================

# MySQL Environment Variables
# MYSQL_HOST=localhost
# MYSQL_USER=root
# MYSQL_PASSWORD=secret
# MYSQL_DATABASE=mydb
# DATA_GOVERNANCE_ENABLED=true

# Azure Log Analytics Environment Variables
# AZURE_TENANT_ID=<tenant-id>
# AZURE_CLIENT_ID=<client-id>
# AZURE_CLIENT_SECRET=<client-secret>
# AZURE_LOG_ANALYTICS_WORKSPACE_ID=<workspace-id>
# AZURE_LOG_ANALYTICS_ENVIRONMENT=public  # or china, government
# DATA_GOVERNANCE_ENABLED=true

# Profiling Configuration (Both)
# CATEGORICAL_THRESHOLD=0.1
# PROFILING_SAMPLE_SIZE=10000
# ENABLE_DEBUG_DUMPS=true
# DATA_MASKING_ENABLED=true
# SENSITIVE_COLUMNS_CSV=config/sensitive_keywords.csv

# ============================================================================
# 9. SHUTDOWN AND CLEANUP
# ============================================================================

# Both services support clean shutdown
mysql_service.shutdown()
azure_service.shutdown()

# ============================================================================
# 10. PROTOCOL TYPES - FOR TYPE HINTS
# ============================================================================

from src.services.database_protocols import (
    DatabaseExecutionProtocol,
    DatabaseReaderProtocol,
    DatabaseProfilingServiceProtocol
)

# Use protocols in type hints for maximum flexibility
def nlq_pipeline(
    executor: DatabaseExecutionProtocol,
    reader: DatabaseReaderProtocol,
    profiler: DatabaseProfilingServiceProtocol
):
    """
    NLQ pipeline works with ANY database service implementing the protocols
    """
    # Get schema
    schema = reader.read_full_schema()
    
    # Get profile
    profile = profiler.profile_database(schema.keys()[0])
    
    # Execute query
    results = executor.execute_query("SELECT * FROM users")
    
    return results

# Can pass MySQL services
nlq_results = nlq_pipeline(mysql_service, mysql_reader, mysql_profiler)

# Can pass Azure services
nlq_results = nlq_pipeline(azure_service, azure_reader, azure_profiler)

# Can mix and match (not recommended, but technically possible)
nlq_results = nlq_pipeline(mysql_service, azure_reader, mysql_profiler)
