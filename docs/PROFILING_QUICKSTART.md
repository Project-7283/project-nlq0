# Quick Start: Database Profiling

## What is Database Profiling?

Database profiling enriches your semantic graph with business context using LLMs. This helps the system understand:
- What "books" means (a category value, not a table)
- What each table is used for
- What questions users typically ask
- Which columns contain sensitive data

## Quick Setup (3 Steps)

### 1. Configure Environment

Add to your `.env` file:
```bash
# Enable profiling
ENABLE_DB_PROFILING=true

# LLM configuration (recommended)
LIGHT_LLM_PROVIDER=openai
LIGHT_LLM_MODEL=gpt-4o-mini
HEAVY_LLM_PROVIDER=gemini

# Required API keys
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

### 2. Generate Enriched Graph

```bash
PYTHONPATH=. python init/generate_graph_for_db.py
```

This will:
- Connect to your database
- Profile all tables and columns
- Use LLMs to understand business context
- Detect categorical values
- Generate enriched graph JSON

**Time:** ~5-10 minutes for 50 tables
**Cost:** ~$0.50-1.00 (one-time)

### 3. Use the Enriched Graph

```bash
# Start Streamlit UI
PYTHONPATH=. streamlit run src/main.py

# Or start FastAPI
uvicorn src.api:app --reload
```

Now try queries like:
- "Show me all books" ✅ (knows books is a category value)
- "Which customers bought electronics?" ✅ (understands product categories)
- "Low stock products" ✅ (knows stock_quantity column semantics)

## What Gets Added to the Graph?

### Table Nodes
```json
{
  "products": {
    "type": "table",
    "properties": {
      "business_purpose": "Stores sellable product catalog",
      "data_domain": "Inventory & Sales",
      "business_impact": "HIGH",
      "typical_queries": [
        "Show all books in stock",
        "Which products are low on inventory"
      ]
    }
  }
}
```

### Column Nodes
```json
{
  "products.category": {
    "type": "attribute",
    "properties": {
      "is_categorical": true,
      "sample_values": ["books", "electronics", "clothing"],
      "description": "Product category classification",
      "semantic_meaning": "Categorical identifier for product type"
    }
  }
}
```

## Configuration Options

### Sensitive Data Masking

Edit `config/sensitive_keywords.csv`:
```csv
keyword,mask_type
password,full
token,full
your_custom_keyword,full
```

Columns matching these keywords will be masked in profiling.

### Profiling Thresholds

```bash
# Column with <10% unique values = categorical
CATEGORICAL_THRESHOLD=0.1

# Max rows to sample for large tables
PROFILING_SAMPLE_SIZE=10000

# Disable masking (not recommended)
DATA_MASKING_ENABLED=false
```

## Disable Profiling

To generate schema-only graph (faster, no LLM cost):

```bash
ENABLE_DB_PROFILING=false python init/generate_graph_for_db.py
```

## Troubleshooting

### "GEMINI_API_KEY is required"
Get your free API key: https://makersuite.google.com/app/apikey

### "OPENAI_API_KEY is required"
- Option 1: Get OpenAI key: https://platform.openai.com/api-keys
- Option 2: Use Gemini for both:
  ```bash
  LIGHT_LLM_PROVIDER=gemini
  HEAVY_LLM_PROVIDER=gemini
  ```

### Profiling is slow
Normal for first run. Results are cached in the graph JSON.

### High API costs
Use lighter models:
```bash
LIGHT_LLM_MODEL=gpt-4o-mini  # Cheaper
HEAVY_LLM_MODEL=gemini-2.5-flash  # Fast and cheap
```

## Example Output

```
============================================================
DATABASE SEMANTIC GRAPH GENERATION
============================================================

📊 Connecting to database...
   Database: ecommerce_marketplace

🤖 Initializing LLM services for profiling...
   Light LLM: OpenAI gpt-4o-mini
   Heavy LLM: Gemini

🔒 Initializing data governance...
   Sensitive keywords loaded: 14
   Masking enabled: True

🏗️  Building semantic graph...

🔍 Running database profiling for enriched metadata...

[1/10] Profiling table: products
[2/10] Profiling table: customers
[3/10] Profiling table: orders
...

Profiled 10 tables

Inferring virtual tables from data patterns...
  ✨ Added virtual table: customer_order_summary
  ✨ Added virtual table: product_sales_analytics

============================================================
✅ SUCCESS! Semantic graph saved to: schemas/ecommerce_marketplace.json
============================================================
```

## Next Steps

1. ✅ Run profiling once
2. ✅ Start your application
3. ✅ Try natural language queries with categorical values
4. 🔄 Re-run profiling when schema changes

## Learn More

- [Full Documentation](docs/services/db_profiling_service.md)
- [Implementation Details](docs/PROFILING_IMPLEMENTATION.md)
- [Configuration Guide](config/README.md)
