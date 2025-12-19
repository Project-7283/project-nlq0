import os
from typing import Dict, Any, Optional, Tuple
from src.modules.semantic_graph import SemanticGraph
from src.services.inference import GeminiService, InferenceServiceProtocol, ModelInferenceService
from src.services.vector_service import GraphVectorService

class NLQIntentAnalyzer:
    """
    Service to analyze user intent and extract graph search parameters
    (start_node, end_node, condition) using Gemini LLM.
    """

    def __init__(self, model: InferenceServiceProtocol, vector_service: Optional[GraphVectorService] = None):
        self.model = model
        self.vector_service = vector_service
    
    def _format_node_context(self, node_id: str, graph: SemanticGraph) -> str:
        """
        Format a node with its key properties for LLM context.
        Includes node type, description, and comment fields.
        
        Args:
            node_id: The node identifier
            graph: The semantic graph
            
        Returns:
            Formatted string with node details
        """
        node_details = graph.get_node_details(node_id)
        node_type = node_details.get('node_type', 'unknown')
        properties = node_details.get('properties', {})
        
        parts = [f"{node_id} ({node_type})"]
        
        # Add description (prioritized)
        description = properties.get('description') or properties.get('Comment') or properties.get('table_comment')
        if description:
            # Truncate long descriptions
            if len(description) > 150:
                description = description[:150] + "..."
            parts.append(f"- {description}")
        
        # Add semantic meaning for columns
        if node_type == "attribute":
            semantic = properties.get('semantic_meaning')
            if semantic:
                parts.append(f"[{semantic}]")
            
            # Add data type
            data_type = properties.get('Type')
            if data_type:
                parts.append(f"Type: ({data_type})")
        
        # Add business purpose for tables
        if node_type == "table":
            business_purpose = properties.get('business_purpose')
            if business_purpose and not description:
                if len(business_purpose) > 150:
                    business_purpose = business_purpose[:150] + "..."
                parts.append(f"- {business_purpose}")
        
        return " ".join(parts)
        
    def refine_intent(self, user_query: str) -> str:
        # Simple refinement to clarify ambiguous queries
        prompt = (
            "Refine the following user query to make it clearer for database schema search:\n"
            f"User Query: {user_query}\n"
            "Refined Query:"
        )
        refined = self.model.chat_completion(prompt)
        return refined.strip()

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
                    "type": "string",
                    "description": "The node in the schema graph where the search should start."
                },
                "end_node": {
                    "type": "string",
                    "description": "The node in the schema graph where the search should end."
                },
                "condition": {
                    "type": "string",
                    "description": "The condition or relationship to filter edges (can be empty if not specified). Write full condition with values if available."
                }
            },
            "required": ["start_node", "end_node", "condition"]
        }

        # Optionally, provide node names/types as context for Gemini
        if self.vector_service:
            # Use vector service to filter relevant nodes
            # We assume the graph has been indexed previously
            refined_query = user_query

            node_names = self.vector_service.search_nodes(refined_query, k=16)
            nodes_with_properties = [
                self._format_node_context(node, graph)
                for node in node_names
            ]
            print(f"Filtered graph nodes using Vector DB. Retained {len(node_names)} nodes.")
            print(f"Nodes: {', '.join(node_names)}")
        else:
            node_names = list(graph.node_properties.keys())
            nodes_with_properties = [
                self._format_node_context(node, graph)
                for node in node_names
            ]
            
        context = (
            "Available nodes in the schema graph:\n" +
            "\n".join(nodes_with_properties) +
            "\n\nGiven the following user query, extract the start_node, end_node, and condition for a path search."
        )

        # Compose content for Gemini
        content = f"{context}\n\nUser Query: {user_query}"
        
        print(f"Getting intent from inference model for prompt: {content}")

        # Call Gemini for structured output
        result = self.model.get_structured_output(content, schema)
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
                "start_node": [result["start_node"]],
                "end_node": [result["end_node"]],
                "condition": result["condition"]
            }
        return None
    