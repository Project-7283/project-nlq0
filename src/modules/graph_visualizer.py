import networkx as nx
import matplotlib.pyplot as plt
from .semantic_graph import SemanticGraph

class GraphVisualizer:
    """
    Visualizes a SemanticGraph using networkx and matplotlib.
    """
    def __init__(self, semantic_graph: SemanticGraph):
        self.semantic_graph = semantic_graph
        self.G = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        # Add nodes with type as attribute
        for node_id, props in self.semantic_graph.node_properties.items():
            self.G.add_node(node_id, type=props.get('type', 'structural'))
        # Add edges with weight and condition as attributes
        for from_node, neighbors in self.semantic_graph.graph.items():
            for to_node, edge_data in neighbors.items():
                self.G.add_edge(from_node, to_node, weight=edge_data.get('weight', 1.0), condition=edge_data.get('condition'))

    def draw(self, with_labels=True, node_color_map=None, edge_label_attr=None, figsize=(12,8)):
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(self.G, seed=42)
        # Node colors by type
        if node_color_map is None:
            node_color_map = {'table': 'skyblue', 'column': 'lightgreen', 'view': 'orange', 'structural': 'gray'}
        node_colors = [node_color_map.get(self.G.nodes[n].get('type', 'structural'), 'gray') for n in self.G.nodes]
        nx.draw(self.G, pos, with_labels=with_labels, node_color=node_colors, node_size=700, font_size=8, arrows=True)
        # Edge labels
        if edge_label_attr:
            edge_labels = {(u, v): d.get(edge_label_attr, '') for u, v, d in self.G.edges(data=True)}
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=7)
        plt.title("Semantic Graph Visualization")
        plt.tight_layout()
        plt.savefig("semantic_graph.png", dpi=200)
        print("Graph saved as semantic_graph.png")
        plt.show()

    @classmethod
    def from_json(cls, file_path):
        sg = SemanticGraph.load_from_json(file_path)
        return cls(sg)
