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
model = OpenAIService(model="gpt-4o")
# model = OllamaService(model="qwen2.5-coder:3b")
vector_service = GraphVectorService()
# Index the graph nodes for vector search
vector_service.index_graph(graph)

intent_analyzer = NLQIntentAnalyzer(model=model, vector_service=vector_service)
sql_generator = SQLGenerationService(db_name="ecommerce_marketplace", model=model)


def extract_intent(state: dict) -> dict:
    # Use refined query if available, otherwise fall back to original
    query_for_intent = state.get("refined_query", state["user_query"])
    
    print(f"Extracting user intent from: {query_for_intent}")
    intent = intent_analyzer.analyze_intent(query_for_intent, graph)
    if not intent:
        raise ValueError("Could not extract intent from user query.")
    state.update(intent)
    print("Intent received: ", intent)
    return state

def refine_query_as_analyst(state: dict) -> dict:
    """
    Refine the user query by thinking like a data analyst.
    Provides context about available tables and suggests which tables to look at,
    what joins might be needed, and clarifies any ambiguities.
    """
    user_query = state["user_query"]
    
    print("\n🔍 Refining query as data analyst...")
    
    # Get all table nodes with their descriptions
    table_nodes = []
    for node_id, node_data in graph.node_properties.items():
        if node_data.get('type') == 'table':
            properties = node_data.get('properties', {})
            description = properties.get('description') or properties.get('business_purpose') or properties.get('table_comment', '')
            
            table_info = f"- **{node_id}**"
            if description:
                # Truncate long descriptions
                if len(description) > 150:
                    description = description[:150] + "..."
                table_info += f": {description}"
            
            # Add domain info if available
            domain = properties.get('data_domain')
            if domain:
                table_info += f" (Domain: {domain})"
            
            table_nodes.append(table_info)
    
    # Create analyst prompt
    prompt = f"""You are an experienced data analyst reviewing a user's query request. Your job is to think through the query and provide guidance on how to approach it.

User Query: "{user_query}"

Available Tables in Database:
{chr(10).join(table_nodes)}

As a data analyst, provide:
1. **Clarified Intent**: Rephrase the query to remove any ambiguity
2. **Relevant Tables**: Which tables should be looked at (by name)?
3. **Potential Challenges**: Any ambiguities or edge cases to consider?

Respond in a structured format:

CLARIFIED QUERY: [Your refined version of the query]

TABLES NEEDED: [List of table names]

NOTES: [Any additional considerations or ambiguities to address]
"""
    
    try:
        analyst_guidance = model.chat_completion(prompt)
        print(f"\n📊 Data Analyst Guidance:\n{analyst_guidance}\n")
        
        # Store both original and refined query
        state["analyst_guidance"] = analyst_guidance
        state["original_query"] = user_query
        
        # Extract clarified query if present
        if "CLARIFIED QUERY:" in analyst_guidance:
            clarified = analyst_guidance.split("CLARIFIED QUERY:")[1].split("\n")[0].strip()
            if clarified and len(clarified) > 10:  # Basic validation
                print(f"✅ Using clarified query: {clarified}")
                state["refined_query"] = clarified
            else:
                state["refined_query"] = user_query
        else:
            state["refined_query"] = user_query
            
    except Exception as e:
        print(f"⚠️ Query refinement failed: {e}. Using original query.")
        state["refined_query"] = user_query
        state["analyst_guidance"] = None
    
    return state

def find_path(state: dict) -> dict:
    # If end_node is empty, the query is about a single entity
    if not state.get("end_node") or state["end_node"] == [""] or state["start_node"] == state["end_node"] or len(state["end_node"]) == 0:
        state["path"] = [state["start_node"][0], state["start_node"][0]]
        print("Single entity query detected. Path: ", state["path"])
        return state
    
    cost, path, walk = graph.find_path(state["start_node"], state["end_node"], "foreign_key,association,reverse_foreign_key")
    print("path received: ", path, walk)
    if not path:
        state["path"] = [state["start_node"][0], state["start_node"][0]]
    
    state["path"] = path
    return state

def generate_sql(state: dict) -> dict:
    # Use refined query if available, otherwise use original
    query_for_generation = state.get("refined_query", state["user_query"])
    
    # Include analyst guidance in SQL generation context
    if state.get("analyst_guidance"):
        query_context = f"{query_for_generation}\n\nData Analyst Notes:\n{state['analyst_guidance']}"
    else:
        query_context = query_for_generation
    
    sql = sql_generator.generate_sql(state["path"], graph, f"{query_context}\n\nIntent Condition: {state.get('condition', '')}")
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
builder.add_node("refine_query", refine_query_as_analyst)
builder.add_node("find_path", find_path)
builder.add_node("generate_sql", generate_sql)
builder.add_node("run_sql", run_sql)
builder.add_node("correct_sql", correct_sql)

builder.set_entry_point("refine_query")
builder.add_edge("refine_query", "extract_intent")
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
