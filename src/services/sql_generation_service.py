import json
import os
from typing import List, Dict, Any, Optional
from .inference import GeminiService, InferenceServiceProtocol, ModelInferenceService
from .mysql_service import MySQLService
from .db_reader import DBSchemaReaderService
from ..modules.semantic_graph import SemanticGraph

class SQLGenerationService:
    """
    Service to generate SQL from a semantic graph path and run it on the database.
    Utilizes Gemini LLM for SQL generation and MySQLService for execution.
    Now includes data governance to prevent generating queries that access sensitive columns.
    """
    def __init__(self, model: InferenceServiceProtocol, db_name="nlq0", governance_service=None):
        self.model = model  # GeminiService(api_key=gemini_api_key)
        self.sql_service = MySQLService(database=db_name, governance_service=governance_service)
        
        # Data governance integration
        self.governance = governance_service
        if self.governance is None:
            # Lazy import to avoid circular dependencies
            try:
                from .data_governance_service import DataGovernanceService
                self.governance = DataGovernanceService()
            except Exception:
                self.governance = None
        
        self.governance_enabled = os.getenv("DATA_GOVERNANCE_ENABLED", "true").lower() == "true"

    def path_to_sql_prompt(self, path: List[str], graph: SemanticGraph) -> str:
        """
        Compose a prompt for Gemini to generate SQL, embedding edge properties and node info.
        Filters out sensitive columns from schema context if governance is enabled.
        """
        if not path or len(path) < 2:
            raise ValueError("Path must have at least two nodes (start and end).")
        edge_descriptions = []
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i+1]
            edge = graph.get_edge_details(from_node, to_node)
            desc = f"{from_node} -> {to_node} (condition: {edge.get('condition')}, properties: {edge.get('properties', {})})"
            edge_descriptions.append(desc)
        
        # Gather table schema details for each table node in the path
        # Filter out sensitive columns if governance is enabled
        schema_descriptions = []
        for node in path:
            neighbors = graph.get_neighbors_by_condition(node_id=node, condition="association")
            
            # Filter sensitive columns from schema
            if self.governance_enabled and self.governance:
                filtered_neighbors = {}
                for neighbor, edge_data in neighbors.items():
                    # Extract column name from node ID (format: "table.column")
                    col_name = neighbor.split('.')[-1] if '.' in neighbor else neighbor
                    if not self.governance.is_sensitive_column(col_name):
                        filtered_neighbors[neighbor] = edge_data
                neighbors = filtered_neighbors
            
            schema_descriptions.append(f"{node}: " + ", " + json.dumps(neighbors))
        
        if schema_descriptions:
            schema_section = "Table schemas (sensitive columns filtered):\n" + "\n".join(schema_descriptions) + "\n"
        else:
            schema_section = ""
        prompt = (
            "Given the following path in a database schema graph, generate a SQL query that retrieves the relevant data.\n"
            "Path: " + " -> ".join(path) + "\n"
            "Edge details: " + "; ".join(edge_descriptions) + "\n"
            "Respond ONLY with a JSON object: { \"sql\": \"...\" }" + "\n"
            f"{schema_section}"
        )
        print("prompt", prompt)
        return prompt

    def generate_sql(self, path: List[str], graph: SemanticGraph, user_query: str = "") -> str:
        """
        Generate SQL using Gemini, given a path and the graph. Optionally include user query for context.
        Validates generated SQL against data governance policies.
        """
        prompt = self.path_to_sql_prompt(path, graph)
        if user_query:
            prompt += f"\nUser Query: {user_query}"
        schema = {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "The SQL query to run."}
            },
            "required": ["sql"]
        }
        result = self.model.get_structured_output(prompt, schema)
        if isinstance(result, dict) and "sql" in result:
            sql = result["sql"]
            
            # Validate generated SQL against governance policies
            if self.governance_enabled and self.governance:
                is_valid, error_msg = self.governance.validate_query(sql)
                if not is_valid:
                    # Try to sanitize the SQL instead of failing
                    print(f"⚠️  Generated SQL violates governance: {error_msg}")
                    print(f"   Attempting to sanitize...")
                    sanitized_sql = self.governance.sanitize_sql(sql)
                    print(f"   Sanitized SQL: {sanitized_sql}")
                    return sanitized_sql
            
            return sql
        raise ValueError("Gemini did not return a valid SQL object.")

    def correct_sql(self, invalid_sql: str, error_message: str, user_query: str) -> str:
        """
        Corrects an invalid SQL query based on the error message using the LLM.
        """
        prompt = f"""
        The following SQL query failed to execute.
        
        User Query: {user_query}
        Invalid SQL: {invalid_sql}
        Error Message: {error_message}
        
        Please correct the SQL query to fix the error. Ensure the logic still matches the user's intent.
        Respond ONLY with a JSON object: {{ "sql": "..." }}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "The corrected SQL query."}
            },
            "required": ["sql"]
        }
        
        result = self.model.get_structured_output(prompt, schema)
        if isinstance(result, dict) and "sql" in result:
            return result["sql"]
        raise ValueError("LLM did not return a valid corrected SQL object.")

    def run_sql(self, sql: str) -> List[Any]:
        """
        Run the SQL query using MySQLService and return the results.
        """
        return self.sql_service.execute_query(sql)

    def generate_and_run(self, path: List[str], graph: SemanticGraph, user_query: str = "") -> Dict[str, Any]:
        """
        Full pipeline: generate SQL from path, run it, and return both SQL and results.
        """
        sql = self.generate_sql(path, graph, user_query)
        results = self.run_sql(sql)
        return {"sql": sql, "results": results}
