import sys
import os
sys.path.append(os.getcwd())

from src.utils.container import Container
from src.modules.semantic_graph import SemanticGraph

def main():
    print("Starting Evolution Flow Test...")
    
    # Mock API Key for test
    os.environ["OPENAI_API_KEY"] = "dummy"
    
    # 1. Initialize Container
    container = Container.get_instance()
    feedback_service = container.get_feedback_service()
    evolution_service = container.get_graph_evolution_service()
    graph = container.get_semantic_graph()
    
    # 2. Simulate a Query Result
    print("\n--- Simulating Query ---")
    query = "Show me users"
    sql = "SELECT * FROM users"
    context = {"tables": ["users", "orders"]} # Pretend we joined users and orders
    
    # Check initial weight
    if "users" in graph.graph and "orders" in graph.graph["users"]:
        initial_weight = graph.graph["users"]["orders"]["weight"]
        print(f"Initial Weight (users->orders): {initial_weight}")
    else:
        # Create edge for testing if not exists
        print("Creating temporary edge for testing...")
        graph.add_node("users", "table")
        graph.add_node("orders", "table")
        graph.add_edge("users", "orders", weight=1.0)
        initial_weight = 1.0
    
    # 3. Log Positive Feedback
    print("\n--- Logging Positive Feedback ---")
    feedback_service.log_feedback(query, sql, 1, graph_context=context)
    
    # 4. Trigger Evolution
    print("\n--- Triggering Evolution ---")
    evolution_service.process_positive_feedback({"graph_context": context})
    
    # 5. Verify Weight Change
    new_weight = graph.graph["users"]["orders"]["weight"]
    print(f"New Weight (users->orders): {new_weight}")
    
    if new_weight < initial_weight:
        print("\nSUCCESS: Edge weight decreased!")
    else:
        print("\nFAILURE: Edge weight did not change.")

if __name__ == "__main__":
    main()
