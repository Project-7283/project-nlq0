import unittest
import os
import json
from unittest.mock import MagicMock
from src.services.feedback_service import FeedbackService
from src.services.graph_evolution_service import GraphEvolutionService
from src.modules.semantic_graph import SemanticGraph

class TestIntegrationEvolution(unittest.TestCase):
    def setUp(self):
        self.test_log = "test_integration_feedback.json"
        self.test_graph = "test_integration_graph.json"
        
        # Create a dummy graph
        self.graph = SemanticGraph()
        self.graph.add_node("A", "table")
        self.graph.add_node("B", "table")
        self.graph.add_edge("A", "B", weight=1.0)
        self.graph.save_to_json(self.test_graph)
        
        self.feedback_service = FeedbackService(log_file=self.test_log)
        self.inference_service = MagicMock()
        
        self.evolution_service = GraphEvolutionService(
            graph=self.graph,
            feedback_service=self.feedback_service,
            inference_service=self.inference_service,
            graph_path=self.test_graph
        )

    def tearDown(self):
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_graph):
            os.remove(self.test_graph)

    def test_full_feedback_loop(self):
        # 1. Log Feedback
        context = {"tables": ["A", "B"]}
        self.feedback_service.log_feedback("Q1", "SQL1", 1, graph_context=context)
        
        # 2. Trigger Evolution
        self.evolution_service.process_positive_feedback({"graph_context": context})
        
        # 3. Verify Graph Updated in Memory
        edge = self.graph.get_edge_details("A", "B")
        self.assertLess(edge['weight'], 1.0) # Should be 0.95
        
        # 4. Verify Graph Saved to Disk
        # Reload from disk
        loaded_graph = SemanticGraph.load_from_json(self.test_graph)
        edge_loaded = loaded_graph.get_edge_details("A", "B")
        self.assertAlmostEqual(edge_loaded['weight'], 0.95)

if __name__ == '__main__':
    unittest.main()
