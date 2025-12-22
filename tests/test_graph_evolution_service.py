import unittest
from unittest.mock import MagicMock
from src.services.graph_evolution_service import GraphEvolutionService
from src.modules.semantic_graph import SemanticGraph

class TestGraphEvolutionService(unittest.TestCase):
    def setUp(self):
        self.mock_graph = MagicMock(spec=SemanticGraph)
        self.mock_feedback_service = MagicMock()
        self.service = GraphEvolutionService(
            graph=self.mock_graph,
            feedback_service=self.mock_feedback_service,
            graph_path="dummy_path.json"
        )

    def test_reinforce_path(self):
        # Setup mock graph to return an edge
        self.mock_graph.get_edge_details.return_value = {'weight': 1.0, 'condition': None}
        
        # Call reinforce_path
        self.service.reinforce_path(["A", "B", "C"])
        
        # Verify update_edge_weight was called twice (A->B, B->C)
        # And potentially reverse edges if they exist (mock returns edge for all calls)
        # Since we mock get_edge_details to always return something, it will try to update forward and reverse.
        # A->B, B->A, B->C, C->B = 4 updates
        self.assertEqual(self.mock_graph.update_edge_weight.call_count, 4)
        
        # Verify weight decay
        # 1.0 * 0.95 = 0.95
        self.mock_graph.update_edge_weight.assert_any_call("A", "B", 0.95)

    def test_process_positive_feedback(self):
        log_entry = {
            "graph_context": {
                "tables": ["users", "orders"]
            }
        }
        
        # Setup mock to return edge for users->orders
        self.mock_graph.get_edge_details.return_value = {'weight': 1.0}
        
        self.service.process_positive_feedback(log_entry)
        
        # Should reinforce users->orders
        self.mock_graph.update_edge_weight.assert_any_call("users", "orders", 0.95)

if __name__ == '__main__':
    unittest.main()
