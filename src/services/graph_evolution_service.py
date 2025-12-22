from typing import List, Dict, Any
from src.modules.semantic_graph import SemanticGraph
from src.services.feedback_service import FeedbackService
from src.services.inference import InferenceServiceProtocol
from src.utils.logging import app_logger
import json

class GraphEvolutionService:
    def __init__(self, graph: SemanticGraph, feedback_service: FeedbackService, inference_service: InferenceServiceProtocol, graph_path: str):
        self.graph = graph
        self.feedback_service = feedback_service
        self.inference_service = inference_service
        self.graph_path = graph_path
        self.decay_factor = 0.95  # Reduce weight by 5% for positive feedback

    def evolve_from_feedback(self):
        """
        Process new feedback logs and update the graph.
        """
        logs = self.feedback_service.get_logs()
        # In a real system, we would track processed logs. 
        # For now, we'll just process the last one if it hasn't been processed (simplified).
        
        # TODO: Implement log tracking to avoid re-processing.
        # For this MVP, we assume this is called immediately after feedback.
        pass

    def reinforce_path(self, path_nodes: List[str]):
        """
        Decreases the weight of edges along the successful path.
        """
        if not path_nodes or len(path_nodes) < 2:
            return

        updates = 0
        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i+1]
            
            # Update forward edge
            edge = self.graph.get_edge_details(u, v)
            if edge:
                new_weight = edge['weight'] * self.decay_factor
                self.graph.update_edge_weight(u, v, new_weight)
                updates += 1
            
            # Update reverse edge if exists (undirected semantic relationship)
            edge_rev = self.graph.get_edge_details(v, u)
            if edge_rev:
                new_weight = edge_rev['weight'] * self.decay_factor
                self.graph.update_edge_weight(v, u, new_weight)
                updates += 1

        if updates > 0:
            self.graph.save_to_json(self.graph_path)
            app_logger.info(f"Reinforced {updates} edges along path: {path_nodes}")

    def process_positive_feedback(self, log_entry: Dict[str, Any]):
        """
        Handles a positive feedback entry.
        """
        context = log_entry.get("graph_context")
        if not context:
            return

        # 1. Reinforce Path
        tables = context.get("tables", [])
        if len(tables) > 1:
            self.reinforce_clique(tables)
            
        # 2. Check for Virtual Node Creation
        self.check_for_virtual_node_creation(tables, log_entry.get("generated_sql"))

    def check_for_virtual_node_creation(self, tables: List[str], generated_sql: str):
        """
        Checks if a pattern is frequent enough to become a virtual node.
        """
        if not tables or len(tables) < 2:
            return

        # Canonical key for the pattern
        pattern_key = tuple(sorted(tables))
        
        # Count occurrences in logs
        logs = self.feedback_service.get_logs()
        count = 0
        for log in logs:
            if log.get("rating") == 1:
                ctx = log.get("graph_context", {})
                log_tables = ctx.get("tables", [])
                if tuple(sorted(log_tables)) == pattern_key:
                    count += 1
        
        # Threshold (low for demo purposes)
        THRESHOLD = 3
        if count >= THRESHOLD:
            self.create_virtual_node(pattern_key, generated_sql)

    def create_virtual_node(self, tables: tuple, sql_fragment: str):
        """
        Creates a virtual node representing the frequent pattern.
        """
        node_name = f"Virtual_{'_'.join(tables)}"
        
        # Check if already exists
        if self.graph.get_node_details(node_name):
            return

        # Create Node
        self.graph.add_node(
            node_id=node_name,
            node_type="virtual",
            properties={
                "description": f"Frequent join pattern between {', '.join(tables)}",
                "sql_fragment": sql_fragment, # In reality, we'd want to extract the WHERE/JOIN clause, not full SQL
                "source_tables": list(tables)
            }
        )
        
        # Connect to constituent tables
        for table in tables:
            self.graph.add_edge(node_name, table, weight=0.1, condition="virtual_link")
            self.graph.add_edge(table, node_name, weight=0.1, condition="virtual_link")
            
        self.graph.save_to_json(self.graph_path)
        app_logger.info(f"Created Virtual Node: {node_name}")

    def reinforce_clique(self, nodes: List[str]):
        """
        Reinforces edges between all pairs of nodes in the list if they exist.
        """
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                u, v = nodes[i], nodes[j]
                self.reinforce_path([u, v])

    def process_negative_feedback(self, log_entry: Dict[str, Any]):
        """
        Handles a negative feedback entry by analyzing the failure with LLM.
        """
        user_query = log_entry.get("user_query")
        generated_sql = log_entry.get("generated_sql")
        user_comment = log_entry.get("user_comment")
        
        if not user_comment:
            return

        try:
            analysis = self.analyze_failure(user_query, generated_sql, user_comment)
            
            if analysis.get("action") == "add_synonym":
                term = analysis.get("term")
                target = analysis.get("target")
                app_logger.info(f"Evolution Action: Add synonym '{term}' -> '{target}'")
                # TODO: Call VectorService to update metadata
                
            elif analysis.get("action") == "penalize_path":
                app_logger.info("Evolution Action: Penalize path (not yet implemented)")
                
        except Exception as e:
            app_logger.error(f"Error analyzing failure: {e}")

    def analyze_failure(self, query: str, sql: str, comment: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze this SQL generation failure.
        User Query: "{query}"
        Generated SQL: "{sql}"
        User Feedback: "{comment}"
        
        Determine the root cause.
        - If the user used a term that wasn't understood (e.g., "clients" for "users"), action is "add_synonym".
        - If the join path was wrong, action is "penalize_path".
        - Otherwise, "unknown".
        
        Return JSON with keys: "action", "term" (optional), "target" (optional).
        """
        
        # Simple schema for structured output
        schema = {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add_synonym", "penalize_path", "unknown"]},
                "term": {"type": "string"},
                "target": {"type": "string"}
            },
            "required": ["action"]
        }
        
        return self.inference_service.get_structured_output(prompt, schema)
