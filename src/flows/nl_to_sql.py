from typing import Any, List, Dict
from langgraph.graph import StateGraph, END
from src.services.inference import ModelInferenceService, OllamaService, OpenAIService
from src.services.mysql_service import MySQLService
from src.services.nlp import NLQIntentAnalyzer
from src.services.sql_generation_service import SQLGenerationService
from src.modules.semantic_graph import SemanticGraph
from src.services.vector_service import GraphVectorService

# Load the semantic graph from file or service
GRAPH_PATH = "schemas/ecommerce_marketplace.json"  # Update as needed
graph = SemanticGraph.load_from_json(GRAPH_PATH)

# Initialize services
# model = OpenAIService()
model = OllamaService(model="qwen2.5-coder:3b")
vector_service = GraphVectorService()
# Index the graph nodes for vector search
vector_service.index_graph(graph)

intent_analyzer = NLQIntentAnalyzer(model=model, vector_service=vector_service)
sql_generator = SQLGenerationService(db_name="ecommerce_marketplace", model=model)


def extract_intent(state: dict) -> dict:
    user_query = state["user_query"]
    print("Extracting user intent")
    intent = intent_analyzer.analyze_intent(user_query, graph)
    if not intent:
        raise ValueError("Could not extract intent from user query.")
    state.update(intent)
    print("Intent received: ", intent)
    return state

def find_path(state: dict) -> dict:
    cost, path, walk = graph.find_path(state["start_node"], state["end_node"], "foreign_key,association,reverse_foreign_key")
    print("path received: ", path, walk)
    if not path:
        raise ValueError("No path found in semantic graph.")
    
    state["path"] = path
    return state

def generate_sql(state: dict) -> dict:
    sql = sql_generator.generate_sql(state["path"], graph, state["user_query"])
    print("generated sql", sql)
    state["sql"] = sql
    state["retries"] = 0  # Initialize retries
    return state

def run_sql(state: dict) -> dict:
    sql = state["sql"]
    print("Executing Sql: ", sql)
    try:
        results = sql_generator.run_sql(sql)
        state["results"] = results
        state["error"] = None
    except Exception as e:
        print(f"SQL Execution Error: {e}")
        state["error"] = str(e)
        state["results"] = None
    return state

def correct_sql(state: dict) -> dict:
    print("Correcting SQL based on error...")
    invalid_sql = state["sql"]
    error = state["error"]
    user_query = state["user_query"]
    
    corrected_sql = sql_generator.correct_sql(invalid_sql, error, user_query)
    print("Corrected SQL: ", corrected_sql)
    
    state["sql"] = corrected_sql
    state["retries"] = state.get("retries", 0) + 1
    return state

def check_retry(state: dict) -> str:
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "correct_sql"
        else:
            print("Max retries reached. Stopping.")
            return END
    return END

# Build the LangGraph
builder = StateGraph(dict)
builder.add_node("extract_intent", extract_intent)
builder.add_node("find_path", find_path)
builder.add_node("generate_sql", generate_sql)
builder.add_node("run_sql", run_sql)
builder.add_node("correct_sql", correct_sql)

builder.set_entry_point("extract_intent")
builder.add_edge("extract_intent", "find_path")
builder.add_edge("find_path", "generate_sql")
builder.add_edge("generate_sql", "run_sql")

builder.add_conditional_edges(
    "run_sql",
    check_retry,
    {
        "correct_sql": "correct_sql",
        END: END
    }
)
builder.add_edge("correct_sql", "run_sql")

nlq_to_sql_graph = builder.compile()

def process_nl_query(user_query: str) -> tuple[str, dict]:
    """
    Main entry point for NLQ to SQL flow using langgraph state.
    """
    state = {"user_query": user_query}
    final_state = nlq_to_sql_graph.invoke(state)
    print(final_state)

    return (state['sql'], state['results'])
