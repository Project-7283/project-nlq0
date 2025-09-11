import os
from typing import Dict, Any, Optional, Tuple
from src.modules.semantic_graph import SemanticGraph
from src.services.inference import GeminiService

class NLQIntentAnalyzer:
    """
    Service to analyze user intent and extract graph search parameters
    (start_node, end_node, condition) using Gemini LLM.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini = GeminiService(api_key=gemini_api_key)

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
            "start_node": {
                "type": "string",
                "description": "The node in the schema graph where the search should start."
            },
            "end_node": {
                "type": "string",
                "description": "The node in the schema graph where the search should end."
            },
            "condition": {
                "type": "string",
                "description": "The condition or relationship to filter edges (can be empty if not specified)."
            }
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
    