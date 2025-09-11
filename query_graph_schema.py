
import copy
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'modules'))
from src.modules.semantic_graph import SemanticGraph

def main():
    dbname = "ecommerce_marketplace"
    schema_path = f"schemas/{dbname}.json"
    if not os.path.exists(schema_path):
        print(f"Schema file not found: {schema_path}")
        return
    graph = SemanticGraph.load_from_json(schema_path)
    print(f"Loaded graph with {len(graph.node_properties)} nodes.")

    print(" \n ".join([copy.deepcopy(item) for item in graph.node_properties if graph.get_node_details(item)['type'] == 'table']))

    # Example queries:
    start = input("Enter start node (e.g. table or table.column): ").strip()
    end = input("Enter end node (e.g. table or table.column): ").strip()
    if start not in graph.node_properties:
        print(f"Start node '{start}' not found.")
        return
    if end not in graph.node_properties:
        print(f"End node '{end}' not found.")
        return
    
    def desc(nd):
        return f"{nd.get('type', '')}({nd})"
    context = input("Enter query context (optional, for condition-aware edges): ").strip()
    cost, path = graph.find_path([start], [end], context)
    if path:
        print(f"Path found (cost={cost}):")
        for node in path:
            det = graph.get_node_details(node)
            print(f"next node: [{det}] - {node}")
    else:
        print("No path found between the nodes.")

if __name__ == "__main__":
    main()
