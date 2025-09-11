# AI Agent Instructions for NLQ Enhancement Project

## Project Overview
This is a Natural Language Query (NLQ) to SQL conversion system that allows users to query a relational database using natural language. The system uses vector embeddings for context retrieval and LLMs for SQL generation.

## Key Components and Architecture

### Data Flow
1. Natural language query → Vector DB context retrieval → LLM SQL generation → MySQL execution → Results display
2. Implementation in `src/flows/nl_to_sql.py`

### Core Services
- Vector Service (`src/services/vector_service.py`): ChromaDB-based context retrieval
- MySQL Service (`src/services/mysql_service.py`): Database connection and query execution
- LLM Service (`src/models/llm.py`): Multi-model SQL generation using:
  - Google Gemini (primary)
  - Ollama/llama2 (fallback)
  - OpenAI (secondary fallback)

### UI Layer
- Streamlit-based interface (`src/ui/app.py`)
- Entry point: `src/main.py`

## Development Workflow

### Environment Setup
1. Create Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Environment Variables (create `.env`):
```
MYSQL_HOST=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=
GEMINI_API_KEY=   # Optional, will fallback to Ollama/OpenAI
```

### Data Generation
- Use `generate_data.py` to create test datasets in CSV format
- Key tables: customers, departments, employees, orders, products, etc.
- Data is generated in `dataset/` directory (git-ignored)

## Project Conventions

### Code Organization
- Services: Isolated external integrations (DB, LLM, vector store)
- Models: Core business logic and data transformations
- Flows: Business process orchestration
- UI: Presentation layer

### Error Handling
- LLM service implements graceful fallbacks between models
- Database connections use proper resource cleanup
- Logging setup in `llm.py` for debugging

### Data Patterns
- All database operations go through mysql_service
- Vector embeddings handle context retrieval
- LLM prompt templates in llm.py

## Testing
- Sample NLQ queries available in `generate_data.py` comments
- Test datasets generated with realistic enterprise data
- Data covers: HR, Sales, Inventory, Marketing, Finance domains

## Common Tasks
- Adding new query patterns: Update LLM prompt templates in `models/llm.py`
- Database schema changes: Update `generate_data.py` and regenerate test data
- UI modifications: Edit `src/ui/app.py` Streamlit components
