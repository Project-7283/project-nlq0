# DB Profiling Service

## Class: `DBProfilingService`

**File:** `src/services/db_profiling_service.py`

### Description
The DBProfilingService combines statistical analysis with LLM-powered semantic understanding to enrich database schema metadata. It profiles tables, columns, views, and even infers virtual tables while respecting data governance policies for sensitive information.

### Key Features
- **Dual-LLM Architecture**: Uses lightweight and heavyweight LLMs for cost optimization
- **Data Governance**: Automatic masking of sensitive columns using configurable keywords
- **Business Context Extraction**: LLM-powered analysis of business purpose, domain, and impact
- **Categorical Detection**: Identifies enum-like columns with low cardinality
- **Virtual Table Inference**: Suggests useful views based on data patterns
- **DB Comment Integration**: Uses existing database-level table and column comments

## Architecture

### Dependencies
- `src.services.db_reader.DBReaderProtocol`: Interface for reading database metadata
- `src.services.inference.InferenceServiceProtocol`: LLM interface for semantic analysis
- `src.services.mysql_service.MySQLService`: Database execution service

### Components

#### 1. DataGovernanceConfig
Manages sensitive data masking policies.

**Configuration:**
```python
# .env
SENSITIVE_COLUMNS_CSV=config/sensitive_keywords.csv
DATA_MASKING_ENABLED=true
```

**CSV Format (config/sensitive_keywords.csv):**
```csv
keyword,mask_type
password,full
token,full
secret,full
hash,full
```

#### 2. DBProfilingService
Main service class for database profiling.

### Key Methods

#### `__init__(db_reader, light_llm, heavy_llm, governance_config)`
Initializes the profiling service with required dependencies.

**Parameters:**
- `db_reader`: Database reader service (DBReaderProtocol)
- `light_llm`: Lightweight LLM for simple tasks (InferenceServiceProtocol)
- `heavy_llm`: Heavyweight LLM for complex analysis (InferenceServiceProtocol)
- `governance_config`: Optional data governance configuration

#### `profile_database(dbname: str) -> Dict[str, Any]`
Profiles entire database including tables, views, and virtual tables.

**Returns:**
```python
{
    "database": "ecommerce_marketplace",
    "tables": {
        "products": {
            "row_count": 1500,
            "table_comment": "Product catalog",
            "business_purpose": "Stores sellable product information",
            "data_domain": "Inventory & Sales",
            "business_impact": "HIGH",
            "description": "Central product repository",
            "typical_queries": ["Show all books", "Products low on stock"],
            "column_statistics": {...},
            "column_descriptions": {...}
        }
    },
    "views": {...},
    "virtual_tables": {...},
    "profiling_timestamp": "2025-12-19T10:30:00"
}
```

#### `profile_table(dbname: str, table: str) -> Dict[str, Any]`
Profiles a single table with full statistical and semantic analysis.

**Process:**
1. Retrieves schema with DB comments
2. Computes statistical metadata (row counts, cardinality, null percentages)
3. Fetches masked sample data
4. Performs LLM business analysis (Heavy LLM)
5. Generates column semantic descriptions (Light LLM)

#### `_get_sample_rows(dbname, table, columns, limit)`
**Key Feature:** Implements intelligent masking using SQL fragments.

Instead of:
```sql
SELECT * FROM products LIMIT 5
```

Generates:
```sql
SELECT 
    product_id,
    name,
    category,
    '***MASKED***' AS api_key,  -- Sensitive column masked
    price
FROM products LIMIT 5
```

This ensures sensitive data never leaves the database.

## LLM Usage Strategy

### Light LLM (Cost-Optimized)
Used for: Column descriptions, semantic meanings

**Example Task:**
```
For each column, provide:
- description: What the column stores
- semantic_meaning: The semantic type
- business_relevance: How it's used

Batch process: 10-20 columns per call
```

### Heavy LLM (Capability-Optimized)
Used for: Business context analysis, virtual table inference

**Example Task:**
```
Analyze table and provide:
- business_purpose
- data_domain
- business_impact (HIGH/MEDIUM/LOW)
- typical_queries (array)
- related_business_processes
```

## Profiling Outputs

### Table-Level Metadata
```python
{
    "row_count": 1500,
    "table_comment": "Product inventory catalog",
    "business_purpose": "Manages product catalog for e-commerce",
    "data_domain": "Inventory & Sales",
    "business_impact": "HIGH",
    "description": "Central repository for sellable products",
    "typical_queries": [
        "Show all books in stock",
        "Which products are low on inventory",
        "Top-selling products by category"
    ],
    "related_business_processes": [
        "Order Fulfillment",
        "Inventory Management",
        "Pricing Strategy"
    ]
}
```

### Column-Level Metadata
```python
{
    "Field": "category",
    "Type": "varchar(50)",
    "Comment": "Product category",  # From DB
    
    # Statistical profiling
    "distinct_count": 12,
    "null_percentage": 0.5,
    "cardinality_ratio": 0.008,
    "is_categorical": True,
    "sample_values": ["books", "electronics", "clothing"],
    "value_distribution": {
        "books": 450,
        "electronics": 320,
        "clothing": 280
    },
    
    # LLM-generated descriptions
    "description": "Product category for classification",
    "semantic_meaning": "Categorical identifier for product types",
    "business_relevance": "Used for filtering, analytics, and browsing"
}
```

### Virtual Tables
```python
{
    "customer_order_summary": {
        "type": "virtual_table",
        "description": "Aggregated customer order statistics",
        "suggested_sql": "CREATE VIEW customer_order_summary AS SELECT ...",
        "use_case": "Answers queries like 'show customer purchase history'"
    }
}
```

## Integration with Semantic Graph

The profiling service integrates seamlessly with `SchemaGraphService`:

```python
from src.services.db_profiling_service import DBProfilingService
from src.services.schema_graph_service import SchemaGraphService

# Setup profiling
profiling_service = DBProfilingService(
    db_reader=db_reader,
    light_llm=light_llm,
    heavy_llm=heavy_llm,
    governance_config=governance
)

# Build enriched graph
graph_service = SchemaGraphService(
    db_reader=db_reader,
    dbname="ecommerce_marketplace",
    profiling_service=profiling_service
)

# Graph nodes now contain rich metadata
graph_service.build_and_save(enable_profiling=True)
```

## Configuration

### Environment Variables
```bash
# Profiling Control
ENABLE_DB_PROFILING=true
CATEGORICAL_THRESHOLD=0.1
PROFILING_SAMPLE_SIZE=10000

# Data Governance
DATA_MASKING_ENABLED=true
SENSITIVE_COLUMNS_CSV=config/sensitive_keywords.csv

# LLM Selection
LIGHT_LLM_PROVIDER=openai
LIGHT_LLM_MODEL=gpt-4o-mini
HEAVY_LLM_PROVIDER=gemini
HEAVY_LLM_MODEL=gemini-2.5-flash
```

## Benefits

### 1. Semantic Understanding
System now knows that "books" is a value in `products.category`, not a separate table.

**Before:** Query "show books" → Search for "books" table → Fail
**After:** Query "show books" → Vector search finds "books" in products.category → Success

### 2. Business Context
Tables have purpose, domain, and typical queries that help with intent extraction.

### 3. Cost Optimization
Light LLM for descriptions, Heavy LLM for complex analysis minimizes API costs.

### 4. Data Security
Sensitive columns automatically masked before LLM processing.

### 5. Virtual Tables
LLM suggests useful aggregate views that simplify complex queries.

## Usage Example

```python
# Initialize services
mysql_service = MySQLService()
db_reader = DBSchemaReaderService(mysql_service)

light_llm = OpenAIService(model="gpt-4o-mini")
heavy_llm = GeminiService()

governance = DataGovernanceConfig(
    sensitive_keywords_csv="config/sensitive_keywords.csv"
)

profiling_service = DBProfilingService(
    db_reader=db_reader,
    light_llm=light_llm,
    heavy_llm=heavy_llm,
    governance_config=governance
)

# Profile database
profile_data = profiling_service.profile_database("ecommerce_marketplace")

# Access results
products_profile = profile_data["tables"]["products"]
print(products_profile["business_purpose"])
print(products_profile["typical_queries"])
```

## Performance Considerations

- **Sampling**: For large tables (>1M rows), consider adding sampling logic
- **Caching**: Profile results can be cached and regenerated periodically
- **Batch Processing**: Column descriptions processed in batches to minimize LLM calls
- **Parallel Execution**: Future enhancement to profile multiple tables in parallel
