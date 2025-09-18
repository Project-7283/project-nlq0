import json
from typing import List, Dict, Any, Optional
from .inference import GeminiService, ModelInferenceService
from .mysql_service import MySQLService
from .db_reader import DBSchemaReaderService
from ..modules.semantic_graph import SemanticGraph

class SQLGenerationService:
    """
    Service to generate SQL from a semantic graph path and run it on the database.
    Utilizes Gemini LLM for SQL generation and MySQLService for execution.
    """
    def __init__(self, gemini_api_key: Optional[str] = None, db_name = "nlq0"):
        self.gemini = GeminiService() # GeminiService(api_key=gemini_api_key)
        self.sql_service = MySQLService(database=db_name)

    def path_to_sql_prompt(self, path: List[str], graph: SemanticGraph) -> str:
        """
        Compose a prompt for Gemini to generate SQL, embedding edge properties and node info.
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
        # get_neighbors_by_condition returns a dict: {neighbor_node: edge_data}
        schema_descriptions = []
        for node in path:
            # Assume table nodes are those with attribute connections
            attributes = []
            neighbors = graph.get_neighbors_by_condition(node_id=node, condition="association")
            schema_descriptions.append(f"{node}: " + ", " + json.dumps(neighbors))
        if schema_descriptions:
            schema_section = "Table schemas:\n" + "\n".join(schema_descriptions) + "\n"
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
        result = self.gemini.get_structured_output(prompt, schema)
        if isinstance(result, dict) and "sql" in result:
            return result["sql"]
        raise ValueError("Gemini did not return a valid SQL object.")

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
