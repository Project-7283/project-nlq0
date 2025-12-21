import pytest
from src.modules.semantic_graph import SemanticGraph

def test_semantic_graph_add_node():
    graph = SemanticGraph()
    graph.add_node("A", node_type="table", properties={"desc": "table A"})
    assert "A" in graph.node_properties
    assert graph.node_properties["A"]["type"] == "table"

def test_semantic_graph_add_edge():
    graph = SemanticGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_edge("A", "B", weight=1.0, condition="fk")
    
    assert "B" in graph.graph["A"]
    assert graph.graph["A"]["B"]["condition"] == "fk"

def test_semantic_graph_find_path():
    graph = SemanticGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")
    graph.add_edge("A", "B", weight=1.0)
    graph.add_edge("B", "C", weight=1.0)
    graph.add_edge("A", "C", weight=5.0)
    
    cost, path, edges = graph.find_path(["A"], ["C"], {})
    
    assert cost == 2.0
    assert path == ["A", "B", "C"]

def test_semantic_graph_get_neighbors_by_condition():
    graph = SemanticGraph()
    graph.add_node("A")
    graph.add_node("B")
    graph.add_edge("A", "B", condition="association")
    
    neighbors = graph.get_neighbors_by_condition("A", "association")
    assert "B" in neighbors
    assert neighbors["B"]["condition"] == "association"
