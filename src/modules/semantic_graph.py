import heapq
from collections import defaultdict
import json
import copy

# The SemanticGraph class is included here for self-containment.
# This is the core data structure that will be built and expanded.
class SemanticGraph:


    def grow_reverse_edges(self, condition_filter=None, new_condition=None):
        """
        For every edge, add a reverse edge if not already present.
        Optionally filter by edge condition, and set a new condition for reverse edges.
        """
        new_edges = []
        for from_node, neighbors in self.graph.items():
            for to_node, edge_data in neighbors.items():
                if condition_filter and edge_data.get('condition') != condition_filter:
                    continue
                if from_node not in self.graph.get(to_node, {}):
                    reverse_props = edge_data.get('properties', {}).copy() if edge_data.get('properties') else None
                    new_edges.append((to_node, from_node, edge_data['weight'], new_condition or edge_data.get('condition'), reverse_props))
        for from_node, to_node, weight, condition, properties in new_edges:
            self.add_edge(from_node, to_node, weight=weight, condition=condition, properties=properties)
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

    def add_edge(self, from_node, to_node, weight=1.0, condition=None, properties=None):
        """
        Adds a directed edge between two nodes with a specified weight, optional condition, and properties.
        A lower weight indicates a more common or important relationship.
        """
        if from_node not in self.node_properties or to_node not in self.node_properties:
            print("Error: One or both nodes do not exist. Please add them first.")
            return

        edge_data = {'weight': weight, 'condition': condition}
        if properties:
            edge_data['properties'] = properties
        self.graph[from_node][to_node] = edge_data
        print(f"Edge added: '{from_node}' -> '{to_node}' (Weight: {weight}, Condition: {condition}, Properties: {properties})")

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
    
    def get_node_details(self, node_id):
        """
        Returns a deep copy of the properties and details of the specified node.
        """
        if node_id not in self.node_properties:
            print(f"Node '{node_id}' does not exist.")
            return None
        return copy.deepcopy(self.node_properties[node_id])

    def get_edge_details(self, from_node, to_node):
        """
        Returns a deep copy of the properties and details of the edge between two nodes.
        """
        if from_node not in self.graph or to_node not in self.graph[from_node]:
            print(f"Edge from '{from_node}' to '{to_node}' does not exist.")
            return None
        return copy.deepcopy(self.graph[from_node][to_node])
    
    def save_to_json(self, file_path):
        """
        Saves the current state of the semantic graph to a JSON file.
        """
        data = {
            "graph": {k: v for k, v in self.graph.items()},
            "node_properties": self.node_properties
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Semantic graph saved to {file_path}")

    @classmethod
    def load_from_json(cls, file_path):
        """
        Loads a semantic graph state from a JSON file and returns a SemanticGraph instance.
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        instance = cls()
        instance.graph = defaultdict(dict, {k: v for k, v in data["graph"].items()})
        instance.node_properties = data["node_properties"]
        print(f"Semantic graph loaded from {file_path}")
        return instance
