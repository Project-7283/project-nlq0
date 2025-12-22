import unittest
from unittest.mock import MagicMock
from src.services.graph_evolution_service import GraphEvolutionService
from src.modules.semantic_graph import SemanticGraph
from src.services.inference import InferenceServiceProtocol

class TestNegativeFeedback(unittest.TestCase):
    def setUp(self):
        self.mock_graph = MagicMock(spec=SemanticGraph)
        self.mock_feedback_service = MagicMock()
        self.mock_inference = MagicMock(spec=InferenceServiceProtocol)
        
        self.service = GraphEvolutionService(
            graph=self.mock_graph,
            feedback_service=self.mock_feedback_service,
            inference_service=self.mock_inference,
            graph_path="dummy_path.json"
        )

    def test_analyze_failure_synonym(self):
        # Mock LLM response
        self.mock_inference.get_structured_output.return_value = {
            "action": "add_synonym",
            "term": "clients",
            "target": "users"
        }
        
        log_entry = {
            "user_query": "Show clients",
            "generated_sql": "SELECT * FROM orders",
            "user_comment": "I meant users, not orders"
        }
        
        self.service.process_negative_feedback(log_entry)
        
        # Verify LLM was called
        self.mock_inference.get_structured_output.assert_called_once()
        
        # In a real test, we'd verify the side effect (e.g., vector service call)
        # Here we just ensure no exception and logic flow

if __name__ == '__main__':
    unittest.main()
