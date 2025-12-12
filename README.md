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
    MYSQL_HOST=localhost
    MYSQL_USER=your_user
    MYSQL_PASSWORD=your_password
    MYSQL_DATABASE=ecommerce_marketplace
    GEMINI_API_KEY=your_gemini_api_key
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
    This script reads your DB schema and creates the `schemas/ecommerce_marketplace.json` file used by the application.
    ```bash
    python generate_graph_for_db.py
    ```

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
