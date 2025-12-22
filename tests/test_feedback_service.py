import unittest
import os
import json
from src.services.feedback_service import FeedbackService

class TestFeedbackService(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_feedback_logs.json"
        self.service = FeedbackService(log_file=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_log_feedback(self):
        log_id = self.service.log_feedback(
            user_query="Show me users",
            generated_sql="SELECT * FROM users",
            rating=1,
            user_comment="Good job",
            graph_context={"nodes": ["users"]}
        )
        
        self.assertIsNotNone(log_id)
        
        logs = self.service.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["user_query"], "Show me users")
        self.assertEqual(logs[0]["rating"], 1)
        self.assertEqual(logs[0]["graph_context"]["nodes"], ["users"])

    def test_persistence(self):
        self.service.log_feedback("Q1", "SQL1", 1)
        
        # Re-instantiate service to check persistence
        new_service = FeedbackService(log_file=self.test_file)
        logs = new_service.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["user_query"], "Q1")

if __name__ == '__main__':
    unittest.main()
