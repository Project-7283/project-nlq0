# NLQ Enhancement: Scalable Natural Language to SQL

## Overview

**NLQ Enhancement** (Project NLQ0) is a system designed to scale Natural Language Query (NLQ) capabilities for complex database schemas. It addresses the latency and token limit bottlenecks of traditional "schema-in-prompt" approaches by utilizing a **Self-Evolving Semantic Graph**.

Instead of feeding the entire database schema to the Large Language Model (LLM), this project abstracts the schema into a lightweight graph. For each user query, it identifies the relevant "path" in the graph, pruning unrelated tables and columns. This results in a highly focused context for the LLM, leading to faster, cheaper, and more accurate SQL generation.

## Key Features

*   **Semantic Graph Abstraction:** Models database tables, columns, and relationships (foreign keys) as a graph.
*   **Intelligent Schema Pruning:** Uses graph pathfinding (Dijkstra's algorithm) to select only the relevant schema subset for a given query.
*   **LangGraph Orchestration:** Manages the NLQ pipeline (Intent Extraction -> Pathfinding -> SQL Generation -> Execution) using a stateful graph flow.
*   **LLM Integration:** Powered by **Google Gemini** for intent analysis and SQL generation.
*   **Dual Interface:**
    *   **Streamlit UI:** For interactive testing and demonstration.
    *   **FastAPI:** REST API for integration with other frontend applications (e.g., the included `presentation.html`).

## Architecture

The system follows a multi-step flow:

1.  **Intent Extraction:** The user's natural language query is analyzed by Gemini to identify key entities (Start Node, End Node) and conditions.
2.  **Pathfinding:** The system searches the **Semantic Graph** to find the optimal path between the identified nodes.
3.  **SQL Generation:** The schema details of only the tables/columns along the path are sent to Gemini to generate the SQL query.
4.  **Execution:** The generated SQL is executed against the MySQL database, and results are returned.

## Prerequisites

*   **Python 3.11+**
*   **MySQL Database**
*   **Google Gemini API Key**

## Local Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd nlq-enhancement
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory with the following credentials:
    ```env
    # Database Configuration
    MYSQL_HOST=
    MYSQL_USER=
    MYSQL_PASSWORD=
    MYSQL_DATABASE=ecommerce_marketplace
    
    # LLM API Keys
    GEMINI_API_KEY=
    OPENAI_API_KEY=
    
    # Optional: Advanced LLM Configuration
    LLM_API_BASE=
    LLM_MODEL=
    LLM_EMBED_MODEL=
    
    # Database Profiling (New!)
    ENABLE_DB_PROFILING=true
    CATEGORICAL_THRESHOLD=0.1
    PROFILING_SAMPLE_SIZE=10000
    
    # Data Governance
    DATA_MASKING_ENABLED=true
    SENSITIVE_COLUMNS_CSV=config/sensitive_keywords.csv
    
    # LLM Selection for Profiling
    LIGHT_LLM_PROVIDER=openai
    LIGHT_LLM_MODEL=gpt-4o-mini
    HEAVY_LLM_PROVIDER=gemini
    HEAVY_LLM_MODEL=gemini-2.5-flash
    ```

5.  **Database Setup**
    *   **Generate Data:** Run the data generation script to create realistic enterprise data in CSV format.
        ```bash
        python generate_data.py
        ```
        This creates an `enterprise_dataset_csv/` directory.
    *   **Initialize Database:**
        *   Create a MySQL database named `ecommerce_marketplace`.
        *   Create tables corresponding to the CSV files (e.g., `customers`, `orders`, `products`).
        *   Import the generated CSV data into these tables.
        *   *Important:* Ensure Foreign Keys are defined (e.g., `orders.customer_id` -> `customers.customer_id`) as the graph generation relies on them.

6.  **Generate Semantic Graph**
    This script reads your DB schema and creates an enriched `schemas/ecommerce_marketplace.json` file with business context and data governance.
    
    **Basic (Schema Only):**
    ```bash
    ENABLE_DB_PROFILING=false python init/generate_graph_for_db.py
    ```
    
    **Enhanced (With LLM-Powered Profiling):**
    ```bash
    ENABLE_DB_PROFILING=true python init/generate_graph_for_db.py
    ```
    
    The enhanced mode provides:
    - Business purpose and domain classification for tables
    - Semantic descriptions for columns
    - Categorical value detection (e.g., "books", "electronics" in product categories)
    - Virtual table suggestions for common queries
    - Automatic masking of sensitive columns (passwords, tokens, etc.)

## Database Profiling (New Feature)

The system now includes **LLM-powered database profiling** that enriches the semantic graph with business context:

### Features
- **Dual-LLM Architecture**: Uses lightweight (gpt-4o-mini) and heavyweight (Gemini) LLMs for cost optimization
- **Business Context**: Extracts business purpose, domain, and impact for each table
- **Semantic Analysis**: Generates human-readable descriptions for columns
- **Categorical Detection**: Identifies enum-like columns and their possible values
- **Virtual Tables**: LLM suggests useful views based on data patterns
- **Data Governance**: Automatically masks sensitive columns (passwords, tokens, keys)

### How It Helps
**Problem:** Query "show me all books" fails because system looks for a "books" table.
**Solution:** Profiling deteLLM service abstraction (Gemini, OpenAI, Ollama).
        *   `mysql_service.py`: Database connectivity.
        *   `schema_graph_service.py`: Logic for building the graph from DB schema.
        *   `db_profiling_service.py`: **NEW** - LLM-powered database profiling.
        *   `vector_service.py`: ChromaDB for semantic search.
*   `init/generate_graph_for_db.py`: Script to bootstrap the semantic graph JSON with optional profiling.
*   `config/`: Configuration files for data governance (sensitive keywords).
*   `schemas/`: Stores the serialized graph JSON files.
*   `docs/`: Architecture and service documentation
### Configuration
Edit `config/sensitive_keywords.csv` to customize which columns are masked:
```csv
keyword,mask_type
password,full
token,full
api_key,full
```

See [config/README.md](config/README.md) for details.

## How to Run

### 1. Streamlit UI
The interactive dashboard allows you to chat with your database.
```bash
PYTHONPATH=. streamlit run src/main.py
```

### 2. REST API
Start the backend server to expose the `/query` endpoint.
```bash
uvicorn src.api:app --reload
```
The API will be available at `http://localhost:8000`.

### 3. Presentation Demo
Open `presentation.html` in your browser. This standalone HTML file connects to the local API (`http://localhost:8000/query`) to demonstrate the project's capabilities in a slide deck format.

## Project Structure

*   `src/`
    *   `api.py`: FastAPI entry point.
    *   `main.py`: Streamlit UI entry point.
    *   `flows/`: Contains the `nl_to_sql` LangGraph flow definition.
    *   `modules/`: Core data structures like `SemanticGraph`.
    *   `services/`:
        *   `nlp.py`: Intent analysis using LLM.
        *   `sql_generation_service.py`: SQL generation logic.
        *   `inference.py`: Gemini API wrapper.
        *   `mysql_service.py`: Database connectivity.
        *   `schema_graph_service.py`: Logic for building the graph from DB schema.
*   `generate_graph_for_db.py`: Script to bootstrap the semantic graph JSON.
*   `schemas/`: Stores the serialized graph JSON files.

## Open Areas of Work

*   **Feedback Loop:** Implementing the "Self-Evolving" aspect where successful queries reinforce graph weights and failed ones penalize them.
*   **Complex Query Support:** Enhancing the graph and prompt engineering to handle complex aggregations, subqueries, and window functions more robustly.
*   **Real-time Schema Sync:** Creating a watcher service to update the graph automatically when the database schema changes.
*   **LLM Agnosticism:** Abstracting the inference layer to easily swap between Gemini, OpenAI, and local LLMs.
