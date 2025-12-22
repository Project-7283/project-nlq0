import unittest
from unittest.mock import MagicMock
from src.services.graph_evolution_service import GraphEvolutionService
from src.modules.semantic_graph import SemanticGraph

class TestVirtualNodes(unittest.TestCase):
    def setUp(self):
        self.mock_graph = MagicMock(spec=SemanticGraph)
        self.mock_feedback_service = MagicMock()
        self.service = GraphEvolutionService(
            graph=self.mock_graph,
            feedback_service=self.mock_feedback_service,
            graph_path="dummy_path.json"
        )

    def test_virtual_node_creation(self):
        # Mock logs to simulate frequent pattern
        logs = [
            {"rating": 1, "graph_context": {"tables": ["A", "B"]}},
            {"rating": 1, "graph_context": {"tables": ["A", "B"]}},
            {"rating": 1, "graph_context": {"tables": ["A", "B"]}},
        ]
        self.mock_feedback_service.get_logs.return_value = logs
        self.mock_graph.get_node_details.return_value = None # Node doesn't exist yet

        # Trigger check
        self.service.check_for_virtual_node_creation(["A", "B"], "SELECT * FROM A JOIN B")

        # Verify add_node was called
        self.mock_graph.add_node.assert_called_once()
        args, kwargs = self.mock_graph.add_node.call_args
        self.assertEqual(kwargs['node_id'], "Virtual_A_B")
        self.assertEqual(kwargs['node_type'], "virtual")
        self.assertIn("sql_fragment", kwargs['properties'])

    def test_virtual_node_threshold_not_met(self):
        # Mock logs with insufficient frequency
        logs = [
            {"rating": 1, "graph_context": {"tables": ["A", "B"]}},
        ]
        self.mock_feedback_service.get_logs.return_value = logs

        self.service.check_for_virtual_node_creation(["A", "B"], "SELECT ...")

        # Verify add_node was NOT called
        self.mock_graph.add_node.assert_not_called()

if __name__ == '__main__':
    unittest.main()
