# 6. User Manual & Maintenance

## 6.1 Installation Guide

### Local Setup
1.  **Prerequisites**: Ensure Docker and Python 3.10+ are installed.
2.  **Database Setup**:
    ```bash
    # Start MySQL container
    docker run --name nlq-mysql -e MYSQL_ROOT_PASSWORD=root -d -p 3306:3306 mysql:8.0
    
    # Load Data
    ./init/setup_data.sh
    ```

### 6.1.1 Semantic Graph Initialization
Before running the app, you must build the semantic graph:
```bash
# Generates schemas/ecommerce_marketplace.json
python init/generate_graph_for_db.py
```

3.  **Application Setup**:
    ```bash
    # Install dependencies
    pip install -r requirements.txt
    
    # Configure Environment
    cp .env.example .env
    # Edit .env with your API keys
    ```
4.  **Run App**:
    ```bash
    streamlit run src/main.py
    ```

## 6.2 User Guide

### Step 1: Launch
Open your browser to `http://localhost:8501`. You will see the "AI SQL Agent" interface.

### Step 2: Ask a Question
In the text box, type a question like:
> "Show me the top 5 products by sales volume."

### Step 3: View Results
The system will:
1.  Display the **Thought Process** (identifying tables `products` and `order_items`).
2.  Show the **Generated SQL** query.
3.  Render the **Result Table** with the data.

### Step 4: Refine (Optional)
If the result isn't what you expected, you can type a follow-up correction:
> "I meant sales revenue, not volume."

## 6.3 Future Enhancements

If more time were available, the following features would be prioritized:

1.  **Multi-Database Support**: Abstracting the `DBReader` to support PostgreSQL and Snowflake.
2.  **User Authentication**: Implementing OAuth2 (Google/GitHub) to support multi-user sessions and role-based access control (RBAC).
3.  **Query Caching**: Implementing Redis caching for common queries to reduce LLM costs and latency.
4.  **Visualizations**: Automatically generating charts (Bar, Line, Pie) based on the result data types using a library like Plotly.
