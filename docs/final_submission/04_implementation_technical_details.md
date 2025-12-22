# 4. Implementation & Technical Details

## 4.1 Environment Setup

### Prerequisites
*   **OS**: macOS, Linux, or Windows (WSL2 recommended).
*   **Python**: Version 3.10 or higher.
*   **Database**: MySQL 8.0+ running locally or via Docker.
*   **API Keys**: Access to Google Gemini (`GEMINI_API_KEY`) or OpenAI (`OPENAI_API_KEY`).

### Installation Steps
1.  **Clone Repository**: `git clone <repo_url>`
2.  **Virtual Environment**: `python -m venv venv && source venv/bin/activate`
3.  **Dependencies**: `pip install -r requirements.txt`
4.  **Configuration**: Create `.env` file with DB credentials and API keys.
5.  **Initialize Data**: Run `scripts/setup_data.sh` to populate the MySQL database.
6.  **Run Application**: `streamlit run src/main.py`

## 4.2 Key Algorithms

### 1. Semantic Graph Traversal (Pathfinding)
To join tables correctly without hallucinating, the system builds a **Semantic Graph** where nodes are tables/columns and edges are Foreign Keys.
*   **Algorithm**: When the user asks a question involving multiple entities (e.g., "Users" and "Products"), the system uses **Dijkstra's Algorithm** (or BFS) on this graph to find the shortest valid join path between them.
*   **Benefit**: Guarantees that generated SQL uses valid `JOIN` conditions defined in the schema.

### 2. Vector-Based Context Retrieval (RAG)
Instead of feeding the entire database schema to the LLM (which wastes tokens and confuses the model), we use **Retrieval-Augmented Generation (RAG)**.
*   **Process**: Table and column descriptions are embedded into **ChromaDB**.
*   **Retrieval**: The user's query is embedded, and a **Cosine Similarity** search finds the top-k most relevant tables.
*   **Benefit**: Allows the system to scale to databases with hundreds of tables.

### 3. Governance & Masking
*   **Regex Detection**: Uses advanced regular expressions to detect sensitive keywords (e.g., `password`, `ssn`) even when hidden in subqueries or aliases.
*   **Source-Level Masking**: Modifies the SQL query *before* execution to replace sensitive columns with `'***MASKED***'`, ensuring PII never leaves the database layer.

## 4.3 API Documentation

While primarily a UI-based tool, the core logic is exposed via FastAPI in `src/api.py`.

### `POST /query`
Processes a natural language query and returns the SQL and results.

**Request Body**:
```json
{
  "query": "How many users are active?"
}
```

**Response Body**:
```json
{
  "sql": "SELECT COUNT(*) FROM users WHERE is_active = 1;",
  "results": [
    { "COUNT(*)": 42 }
  ]
}
```

**Error Codes**:
*   `400`: Missing query field.
*   `500`: Internal server error (LLM failure, DB error).

## 4.4 Third-Party Integrations

*   **Google Gemini / OpenAI**: Provides the reasoning engine for understanding intent and generating SQL.
*   **ChromaDB**: Open-source vector database for schema indexing.
*   **MySQL Connector**: Standard driver for Python-to-MySQL communication.

## 4.5 Semantic Graph Generation Script

The system includes a specialized script `init/generate_graph_for_db.py` that automates the creation of the semantic layer.

### Workflow
1.  **Input**: Reads database connection details from `.env`.
2.  **Schema Introspection**: Uses `DBSchemaReader` to query `information_schema` for table structures and constraints.
3.  **Data Profiling**:
    *   Iterates through every column in the schema.
    *   Fetches a sample of 5 distinct values (masked if sensitive).
    *   Calls the LLM to generate a "Semantic Description" (e.g., "This column `cat_id` represents the product category").
4.  **Graph Serialization**:
    *   Combines schema metadata + LLM descriptions + Foreign Key relationships.
    *   Outputs a JSON file (e.g., `schemas/ecommerce_marketplace.json`).
5.  **Vector Ingestion**: This JSON is then loaded into ChromaDB for RAG retrieval.

**Usage**:
```bash
python init/generate_graph_for_db.py
```
