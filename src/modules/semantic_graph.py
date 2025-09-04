import heapq
from collections import defaultdict

# The SemanticGraph class is included here for self-containment.
# This is the core data structure that will be built and expanded.
class SemanticGraph:
    """
    A class to represent and manage a semantic graph for an NLQ engine.

    The graph is a dictionary where keys are nodes and values are dictionaries
    of connected nodes, each with a weight and an optional condition.
    """
    def __init__(self):
        """Initializes an empty graph."""
        self.graph = defaultdict(dict)
        self.node_properties = {}

    def add_node(self, node_id, node_type="structural", properties=None):
        """
        Adds a new node to the graph with specified type and properties.
        """
        if node_id not in self.node_properties:
            self.node_properties[node_id] = {'type': node_type, 'properties': properties or {}}
            print(f"Node added: '{node_id}' ({node_type})")
        else:
            print(f"Warning: Node '{node_id}' already exists.")

    def add_edge(self, from_node, to_node, weight=1.0, condition=None):
        """
        Adds a directed edge between two nodes with a specified weight and optional condition.
        A lower weight indicates a more common or important relationship.
        """
        if from_node not in self.node_properties or to_node not in self.node_properties:
            print("Error: One or both nodes do not exist. Please add them first.")
            return

        self.graph[from_node][to_node] = {'weight': weight, 'condition': condition}
        print(f"Edge added: '{from_node}' -> '{to_node}' (Weight: {weight}, Condition: {condition})")

    def find_path(self, start_nodes, target_nodes, query_context):
        """
        Finds the lowest-cost path from any start node to any target node(s)
        using a modified Dijkstra's algorithm.
        """
        pq = [(0, start_node, [start_node]) for start_node in start_nodes]
        visited = set()

        while pq:
            cost, current_node, path = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node in target_nodes:
                return cost, path

            for neighbor, edge_data in self.graph.get(current_node, {}).items():
                edge_weight = edge_data['weight']
                edge_condition = edge_data['condition']

                if edge_condition and edge_condition not in query_context.lower():
                    continue

                new_cost = cost + edge_weight
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_cost, neighbor, new_path))
        
        return None, None

def build_initial_graph_from_schema(db_schema):
    """
    Constructs an initial semantic graph from a mock database schema.
    This simulates the initial data scraping phase.
    
    Args:
        db_schema (dict): A dictionary representing the database schema.
        
    Returns:
        SemanticGraph: The initialized graph with structural nodes and foreign key edges.
    """
    graph = SemanticGraph()
    print("--- Phase 1: Building Initial Graph from Schema ---")
    
    # Add nodes for each table and column
    for table_name, table_info in db_schema.items():
        graph.add_node(table_name, "structural", properties={'type': 'table'})
        if 'relationships' == table_name:
                continue  # Skip relationships here

        for column in table_info['columns']:
            
            column_id = f"{table_name}.{column['name']}"
            graph.add_node(column_id, "structural", properties={'type': 'column'})
            # Add edge from table to its columns
            graph.add_edge(table_name, column_id, weight=0.1)

    # Add edges based on foreign key relationships
    for fk_rel in db_schema['relationships']:
        from_table, from_col = fk_rel['from'].split('.')
        to_table, to_col = fk_rel['to'].split('.')
        
        # Add a low-weight edge for the JOIN relationship
        # Lower weight indicates a strong, structural relationship
        graph.add_edge(from_table, to_table, weight=0.5)
        # For bidirectional relationships (or if joins can go both ways)
        graph.add_edge(to_table, from_table, weight=0.5)
        
    print("\nInitial graph construction complete.")
    return graph

def grow_graph_with_semantic_knowledge(graph, semantic_relationships):
    """
    Grows the existing graph by adding conceptual nodes and semantic edges.
    This simulates the "self-evolving" phase based on user behavior or external knowledge.
    
    Args:
        graph (SemanticGraph): The graph to be expanded.
        semantic_relationships (list): A list of new relationships to add.
    """
    print("--- Phase 2: Growing Graph with Semantic Knowledge ---")
    
    for rel in semantic_relationships:
        from_node = rel['from']
        to_node = rel['to']
        rel_type = rel['type']
        
        # Add new nodes if they don't exist (e.g., conceptual nodes)
        if from_node not in graph.node_properties:
            graph.add_node(from_node, "conceptual")
        if to_node not in graph.node_properties:
            graph.add_node(to_node, "conceptual")

        # Add the semantic edge with a weight and optional condition
        graph.add_edge(from_node, to_node, weight=rel['weight'], condition=rel.get('condition'))
    
    print("\nGraph growth and enrichment complete.")

if __name__ == "__main__":
    # Mock Database Schema
    # In a real-world scenario, this would be retrieved programmatically.
    MOCK_DB_SCHEMA = {
        "Customers": {
            "columns": [{"name": "customer_id", "type": "INT"}, {"name": "state", "type": "STRING"}]
        },
        "Orders": {
            "columns": [{"name": "order_id", "type": "INT"}, {"name": "customer_id", "type": "INT"}, {"name": "product_id", "type": "INT"}, {"name": "order_date", "type": "DATE"}]
        },
        "Products": {
            "columns": [{"name": "product_id", "type": "INT"}, {"name": "product_name", "type": "STRING"}, {"name": "price", "type": "DECIMAL"}]
        },
        "relationships": [
            {"from": "Customers.customer_id", "to": "Orders.customer_id"},
            {"from": "Products.product_id", "to": "Orders.product_id"}
        ]
    }
    
    # Mock Semantic Relationships to be identified over time
    MOCK_SEMANTIC_RELATIONSHIPS = [
        {"from": "Customers.state", "to": "California", "type": "filter", "weight": 0.2},
        {"from": "Orders.order_date", "to": "Last Quarter", "type": "time_filter", "weight": 0.2},
        {"from": "Orders", "to": "Discounts", "type": "conditional_join", "weight": 0.7, "condition": "discount"}
    ]

    # --- Step 1: Build the initial graph from the database schema
    semantic_graph = build_initial_graph_from_schema(MOCK_DB_SCHEMA)

    # --- Step 2: Grow the graph with semantic knowledge
    grow_graph_with_semantic_knowledge(semantic_graph, MOCK_SEMANTIC_RELATIONSHIPS)
    
    print("\n--- Final Graph State ---")
    print("Nodes:", list(semantic_graph.node_properties.keys()))
    print("Edges:")
    for from_node, to_edges in semantic_graph.graph.items():
        for to_node, edge_data in to_edges.items():
            print(f"  '{from_node}' -> '{to_node}' (Weight: {edge_data['weight']}, Condition: {edge_data['condition']})")
    
    print("\n--- Example Search on the Grown Graph ---")
    query = "Show me products ordered by customers in California with a discount."
    start_nodes = ["Customers"]
    target_nodes = ["Products", "Discounts"]
    
    cost, path = semantic_graph.find_path(start_nodes, target_nodes, query)

    if path:
        print(f"Found path with cost {cost}: {' -> '.join(path)}")
    else:
        print("No path found.")