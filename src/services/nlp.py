from typing import Dict, Any, Optional, Tuple, List
from src.modules.semantic_graph import SemanticGraph
from src.services.inference import InferenceServiceProtocol
from src.services.vector_service import GraphVectorService
from src.utils.logging import app_logger

class NLQIntentAnalyzer:
    """
    Service to analyze user intent and extract graph search parameters
    (start_node, end_node, condition) using LLM.
    """

    def __init__(self, model: InferenceServiceProtocol, vector_service: Optional[GraphVectorService] = None):
        self.model = model
        self.vector_service = vector_service
    
    def _format_node_context(self, node_id: str, graph: SemanticGraph) -> str:
        """
        Format a node with its key properties for LLM context.
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
        prompt = (
            "Refine the following user query to make it clearer for database schema search:\n"
            f"User Query: {user_query}\n"
            "Refined Query:"
        )
        refined = self.model.chat_completion(prompt)
        return refined.strip()

    async def refine_intent_async(self, user_query: str) -> str:
        prompt = (
            "Refine the following user query to make it clearer for database schema search:\n"
            f"User Query: {user_query}\n"
            "Refined Query:"
        )
        refined = await self.model.chat_completion_async(prompt)
        return refined.strip()

    def analyze_intent(self, user_query: str, graph: SemanticGraph) -> Optional[Dict[str, Any]]:
        """Sync version of analyze_intent"""
        schema = self._get_intent_schema()
        nodes_with_properties = self._get_context_nodes(user_query, graph)
        
        context = (
            "Available nodes in the schema graph:\n" +
            "\n".join(nodes_with_properties) +
            "\n\nGiven the following user query, extract the start_node, end_node, and condition for a path search."
        )

        content = f"{context}\n\nUser Query: {user_query}"
        app_logger.info(f"Analyzing intent for query: {user_query[:50]}...")

        result = self.model.get_structured_output(content, schema)
        return self._process_intent_result(result)

    async def analyze_intent_async(self, user_query: str, graph: SemanticGraph) -> Optional[Dict[str, Any]]:
        """Async version of analyze_intent"""
        schema = self._get_intent_schema()
        
        # Vector search is usually fast but we can wrap it if needed. 
        # For now, keeping it sync as it's local ChromaDB.
        nodes_with_properties = self._get_context_nodes(user_query, graph)
        
        context = (
            "Available nodes in the schema graph:\n" +
            "\n".join(nodes_with_properties) +
            "\n\nGiven the following user query, extract the start_node, end_node, and condition for a path search."
        )

        content = f"{context}\n\nUser Query: {user_query}"
        app_logger.info(f"Analyzing intent (async) for query: {user_query[:50]}...")

        result = await self.model.get_structured_output_async(content, schema)
        return self._process_intent_result(result)

    def _get_intent_schema(self) -> Dict[str, Any]:
        return {
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

    def _get_context_nodes(self, user_query: str, graph: SemanticGraph) -> List[str]:
        if self.vector_service:
            node_names = self.vector_service.search_nodes(user_query, k=16)
            app_logger.debug(f"Vector search found {len(node_names)} nodes")
        else:
            node_names = list(graph.node_properties.keys())
        
        return [self._format_node_context(node, graph) for node in node_names]

    def _process_intent_result(self, result: Any) -> Optional[Dict[str, Any]]:
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
