import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Import the module under test
try:
    import inference
except ImportError:
    # If running as script, add current dir to sys.path
    import os
    sys.path.append(os.path.dirname(__file__))
    import inference

class TestInference(unittest.TestCase):

    def setUp(self):
        self.api_key = "test-key"
        self.gemini = inference.GeminiService(api_key=self.api_key)

    @patch("inference.requests.post")
    def test_call_gemini_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "response text"}]}}
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        result = self.gemini._call_gemini("prompt")
        self.assertEqual(result, "response text")

    @patch("inference.requests.post")
    def test_call_gemini_bad_format(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        with self.assertRaises(RuntimeError):
            self.gemini._call_gemini("prompt")

    @patch("inference.requests.post")
    def test_get_summary(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "summary text"}]}}
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        summary = self.gemini.get_summary("content", max_words=10)
        self.assertEqual(summary, "summary text")

    @patch("inference.requests.post")
    def test_get_structured_output_valid_json(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": '{"a": 1, "b": 2}' }]}}
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        schema = {"a": int, "b": int}
        result = self.gemini.get_structured_output("content", schema)
        self.assertEqual(result, {"a": 1, "b": 2})

    @patch("inference.requests.post")
    def test_get_structured_output_json_with_extra_text(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": 'Here is your result: {"a": 1, "b": 2}' }]}}
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        schema = {"a": int, "b": int}
        result = self.gemini.get_structured_output("content", schema)
        self.assertEqual(result, {"a": 1, "b": 2})

    @patch("inference.requests.post")
    def test_get_structured_output_invalid_json(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": 'not a json' }]}}
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        schema = {"a": int}
        with self.assertRaises(ValueError):
            self.gemini.get_structured_output("content", schema)

    @patch("inference.requests.post")
    def test_analyze_intent(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "intent text"}]}}
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        result = self.gemini.analyze_intent("query")
        self.assertEqual(result, "intent text")

    @patch("inference.requests.post")
    def test_chat_completion(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "chat response"}]}}
            ]
        }
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        result = self.gemini.chat_completion("hello", context="ctx")
        self.assertEqual(result, "chat response")

   

if __name__ == "__main__":
    unittest.main()
