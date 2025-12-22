import asyncio
from typing import Any, List, Dict
from langgraph.graph import StateGraph, END
from src.utils.container import Container
from src.utils.logging import app_logger, performance_logger
import time

# Get services from Container
container = Container.get_instance()
graph = container.get_semantic_graph()
model = container.get_inference_service()
intent_analyzer = container.get_intent_analyzer()
sql_generator = container.get_sql_generator()

async def extract_intent(state: dict) -> dict:
    query_for_intent = state.get("refined_query", state["user_query"])
    app_logger.info(f"Extracting user intent from: {query_for_intent}")
    
    intent = await intent_analyzer.analyze_intent_async(query_for_intent, graph)
    if not intent:
        raise ValueError("Could not extract intent from user query.")
    
    state.update(intent)
    app_logger.debug(f"Intent received: {intent}")
    return state

async def refine_query_as_analyst(state: dict) -> dict:
    user_query = state["user_query"]
    app_logger.info("Refining query as data analyst...")
    
    table_nodes = []
    for node_id, node_data in graph.node_properties.items():
        if node_data.get('type') == 'table':
            properties = node_data.get('properties', {})
            description = properties.get('description') or properties.get('business_purpose') or properties.get('table_comment', '')
            table_info = f"- **{node_id}**"
            if description:
                if len(description) > 150: description = description[:150] + "..."
                table_info += f": {description}"
            table_nodes.append(table_info)
    
    prompt = f"""You are an experienced data analyst reviewing a user's query request.
User Query: "{user_query}"
Available Tables:
{chr(10).join(table_nodes)}
Provide:
1. **Clarified Intent**: Rephrase the query
2. **Relevant Tables**: List table names
3. **Potential Challenges**: Ambiguities
Respond in format:
CLARIFIED QUERY: [refined query]
TABLES NEEDED: [table names]
NOTES: [considerations]
"""
    try:
        analyst_guidance = await model.chat_completion_async(prompt)
        state["analyst_guidance"] = analyst_guidance
        state["original_query"] = user_query
        
        if "CLARIFIED QUERY:" in analyst_guidance:
            clarified = analyst_guidance.split("CLARIFIED QUERY:")[1].split("\n")[0].strip()
            if clarified and len(clarified) > 10:
                state["refined_query"] = clarified
            else:
                state["refined_query"] = user_query
        else:
            state["refined_query"] = user_query
    except Exception as e:
        app_logger.error(f"Query refinement failed: {e}")
        state["refined_query"] = user_query
        state["analyst_guidance"] = None
    
    return state

def find_path(state: dict) -> dict:
    if not state.get("end_node") or state["end_node"] == [""] or state["start_node"] == state["end_node"] or len(state["end_node"]) == 0:
        state["path"] = [state["start_node"][0], state["start_node"][0]]
        return state
    
    cost, path, walk = graph.find_path(state["start_node"], state["end_node"], "foreign_key,association,reverse_foreign_key")
    if not path:
        state["path"] = [state["start_node"][0], state["start_node"][0]]
    else:
        state["path"] = path
    return state

async def generate_sql(state: dict) -> dict:
    query_for_generation = state.get("refined_query", state["user_query"])
    if state.get("analyst_guidance"):
        query_context = f"{query_for_generation}\n\nData Analyst Notes:\n{state['analyst_guidance']}"
    else:
        query_context = query_for_generation
    
    sql = await sql_generator.generate_sql_async(
        state["path"], 
        graph, 
        f"{query_context}\n\nIntent Condition: {state.get('condition', '')}"
    )
    state["sql"] = sql
    state["retries"] = 0
    return state

async def run_sql(state: dict) -> dict:
    sql = state["sql"]
    app_logger.info(f"Executing SQL: {sql}")
    try:
        results = await sql_generator.run_sql_async(sql)
        state["results"] = results
        state["error"] = None
    except Exception as e:
        app_logger.error(f"SQL Execution Error: {e}")
        state["error"] = str(e)
        state["results"] = None
    return state

async def correct_sql(state: dict) -> dict:
    app_logger.info("Correcting SQL based on error...")
    corrected_sql = await sql_generator.correct_sql_async(state["sql"], state["error"], state["user_query"])
    state["sql"] = corrected_sql
    state["retries"] = state.get("retries", 0) + 1
    return state

def check_retry(state: dict) -> str:
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "correct_sql"
        else:
            app_logger.warning("Max retries reached.")
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

async def process_nl_query_async(user_query: str) -> tuple[str, Any, dict]:
    start_time = time.time()
    state = {"user_query": user_query}
    final_state = await nlq_to_sql_graph.ainvoke(state)
    
    duration = time.time() - start_time
    performance_logger.info(f"Flow execution completed in {duration:.2f}s | Query: {user_query[:50]}...")
    
    # Extract context for feedback (tables, joins, etc.)
    context = {
        "tables": final_state.get("tables", []),
        "joins": final_state.get("joins", []),
        "intent": final_state.get("intent", "")
    }
    
    return (final_state.get('sql'), final_state.get('results'), context)

def process_nl_query(user_query: str) -> tuple[str, Any, dict]:
    return asyncio.run(process_nl_query_async(user_query))
