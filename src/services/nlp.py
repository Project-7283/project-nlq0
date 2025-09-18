import os
from typing import Dict, Any, Optional, Tuple
from src.modules.semantic_graph import SemanticGraph
from src.services.inference import GeminiService, ModelInferenceService

class NLQIntentAnalyzer:
    """
    Service to analyze user intent and extract graph search parameters
    (start_node, end_node, condition) using Gemini LLM.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini = GeminiService()

    def analyze_intent(self, user_query: str, graph: SemanticGraph) -> Optional[Dict[str, Any]]:
        """
        Analyze the user query and extract start_node, end_node, and condition
        for semantic graph path search.

        Returns:
            dict with keys: start_node, end_node, condition
            or None if extraction fails.
        """
        # Prepare a schema for Gemini's structured output
        schema = {
            "type": "object",
            "properties": {
                "start_node": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The list of nodes in the schema graph where the search should start. Multiple nodes may be specified."
                },
                "end_node": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The list of nodes in the schema graph where the search should end. Multiple nodes may be specified."
                },
                "condition": {
                    "type": "string",
                    "description": "The condition or relationship to filter edges (can be empty if not specified)."
                }
            },
            "required": ["start_node", "end_node", "condition"]
        }

        # Optionally, provide node names/types as context for Gemini
        node_names = list(graph.node_properties.keys())
        context = (
            "Available nodes in the schema graph: " +
            ", ".join(node_names) +
            ".\nGiven the following user query, extract the start_node, end_node, and condition for a path search."
        )

        # Compose content for Gemini
        content = f"{context}\n\nUser Query: {user_query}"

        # Call Gemini for structured output
        result = self.gemini.get_structured_output(content, schema)
        # result = {
        #     'start_node': 'users',
        #     'end_node': 'orders',
        #     'condition': 'some'
        # }

        # Basic validation
        if (
            isinstance(result, dict)
            and "start_node" in result
            and "end_node" in result
            and "condition" in result
        ):
            return {
                "start_node": result["start_node"],
                "end_node": result["end_node"],
                "condition": result["condition"]
            }
        return None
    