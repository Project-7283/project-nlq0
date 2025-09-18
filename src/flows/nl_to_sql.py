from typing import Any, List, Dict
from langgraph.graph import StateGraph, END
from src.services.mysql_service import MySQLService
from src.services.nlp import NLQIntentAnalyzer
from src.services.sql_generation_service import SQLGenerationService
from src.modules.semantic_graph import SemanticGraph

# Load the semantic graph from file or service
GRAPH_PATH = "schemas/ecommerce_marketplace.json"  # Update as needed
graph = SemanticGraph.load_from_json(GRAPH_PATH)

# Initialize services
intent_analyzer = NLQIntentAnalyzer()
sql_generator = SQLGenerationService(db_name="ecommerce_marketplace")


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
    return state

def run_sql(state: dict) -> dict:
    sql = state["sql"]
    print("Executing Sql: ", sql)
    results = sql_generator.run_sql(sql)
    state["results"] = results
    return state

# Build the LangGraph
builder = StateGraph(dict)
builder.add_node("extract_intent", extract_intent)
builder.add_node("find_path", find_path)
builder.add_node("generate_sql", generate_sql)
builder.add_node("run_sql", run_sql)

builder.set_entry_point("extract_intent")
builder.add_edge("extract_intent", "find_path")
builder.add_edge("find_path", "generate_sql")
builder.add_edge("generate_sql", "run_sql")
builder.add_edge("run_sql", END)

nlq_to_sql_graph = builder.compile()

def process_nl_query(user_query: str) -> tuple[str, dict]:
    """
    Main entry point for NLQ to SQL flow using langgraph state.
    """
    state = {"user_query": user_query}
    final_state = nlq_to_sql_graph.invoke(state)
    print(final_state)

    return (state['sql'], state['results'])
