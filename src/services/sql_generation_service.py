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

    def _format_properties(self, properties: Dict[str, Any], indent: int = 0) -> str:
        """
        Format node properties in a clean, readable markdown format.
        Handles nested structures, arrays, and various data types dynamically.
        
        Args:
            properties: Dictionary of properties to format
            indent: Current indentation level
            
        Returns:
            Formatted string representation
        """
        if not properties:
            return "(no properties)"
        
        lines = []
        indent_str = "  " * indent
        
        # Key properties to show first (if they exist)
        priority_keys = ['description', 'business_purpose', 'semantic_meaning', 'business_relevance', 
                        'Field', 'Type', 'Comment', 'row_count', 'data_domain', 'business_impact']
        
        # Separate priority and other keys
        priority_props = {k: properties[k] for k in priority_keys if k in properties}
        other_props = {k: v for k, v in properties.items() if k not in priority_keys}
        
        # Format priority properties first
        for key, value in priority_props.items():
            lines.append(self._format_property_line(key, value, indent_str))
        
        # Format other properties
        for key, value in other_props.items():
            lines.append(self._format_property_line(key, value, indent_str))
        
        return "\n".join(lines)
    
    def _format_property_line(self, key: str, value: Any, indent_str: str) -> str:
        """
        Format a single property line based on value type.
        """
        # Skip null/None values and masked values
        if value is None or value == "***MASKED***":
            return ""
        
        # Handle different value types
        if isinstance(value, bool):
            return f"{indent_str}• {key}: {value}"
        elif isinstance(value, (int, float)):
            return f"{indent_str}• {key}: {value}"
        elif isinstance(value, str):
            return f"{indent_str}• {key}: {value}"
        elif isinstance(value, list):
            if not value:
                return ""
            items = ", ".join([str(v) for v in value])
            return f"{indent_str}• {key}: [{items}]"
        elif isinstance(value, dict):
            if not value:
                return ""
            # For nested dicts, show key-value pairs inline if small
            if len(value) <= 3 and all(isinstance(v, (str, int, float, bool)) for v in value.values()):
                items = ", ".join([f"{k}={v}" for k, v in value.items()])
                return f"{indent_str}• {key}: {{{items}}}"
            else:
                # Show nested structure without truncation
                nested_lines = [f"{indent_str}• {key}:"]
                for k, v in value.items():
                    nested_lines.append(f"{indent_str}  - {k}: {v}")
                return "\n".join(nested_lines)
        else:
            return f"{indent_str}• {key}: {str(value)}"

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
            # Get node properties from graph
            node_data = graph.get_node_details(node)
            node_type = node_data.get('node_type', 'unknown')
            node_props = node_data.get('properties', {})
            
            # Format node information
            node_desc = [f"\n## {node} ({node_type})"]
            
            # Add formatted properties
            if node_props:
                formatted_props = self._format_properties(node_props)
                if formatted_props and formatted_props != "(no properties)":
                    node_desc.append(formatted_props)
            
            # Get associated columns/attributes
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
            
            # Add columns/attributes
            if neighbors:
                node_desc.append("\n### Columns:")
                for neighbor, edge_data in neighbors.items():
                    neighbor_data = graph.get_node_details(neighbor)
                    neighbor_props = neighbor_data.get('properties', {})
                    
                    # Format column with key properties only
                    col_name = neighbor.split('.')[-1] if '.' in neighbor else neighbor
                    col_desc = [f"- **{col_name}**"]
                    
                    # Add important column properties inline
                    col_type = neighbor_props.get('Type', '')
                    col_comment = neighbor_props.get('Comment', neighbor_props.get('description', ''))
                    
                    if col_type:
                        col_desc.append(f" ({col_type})")
                    if col_comment:
                        col_desc.append(f" - {col_comment}")
                    
                    # Add semantic/business info if available
                    semantic = neighbor_props.get('semantic_meaning', '')
                    business = neighbor_props.get('business_relevance', '')
                    if semantic or business:
                        extra_info = []
                        if semantic:
                            extra_info.append(f"Semantic: {semantic}")
                        if business:
                            extra_info.append(f"Business: {business}")
                        col_desc.append(f" [{'; '.join(extra_info)}]")
                    
                    node_desc.append("".join(col_desc))
                
            schema_descriptions.append("\n".join(node_desc))
        
        if schema_descriptions:
            schema_section = "Table schemas (sensitive columns filtered):\n" + "\n".join(schema_descriptions) + "\n"
        else:
            schema_section = ""
        prompt = (
            "Given the following path in a database schema graph, generate a SQL query that retrieves the relevant data.\n"
            "Table Joining Path: " + " -> ".join(path) + "\n"
            "Joining Edge details: " + "; ".join(edge_descriptions) + "\n"
            "When creating the SQL, follow these guidelines:\n"
            "1. Only select the columns needed to answer the question. Avoid 'SELECT *'.\n"
            "2. Name any aggregated fields using clear aliases (e.g., total_revenue, avg_rating).\n"
            "3. Include WHERE filters that match the user's intent and remove irrelevant rows.\n"
            "4. Use GROUP BY for aggregations and ensure all non-aggregated columns are grouped.\n"
            "5. Order the results in a way that makes the answer easy to read (e.g., ORDER BY totals DESC).\n"
            "6. Limit the number of rows when the user asks for top or specific counts.\n"
            "7. Use meaningful table aliases to keep the SQL readable.\n"
            "8. Avoid unnecessary joins or columns that are not referenced in the SELECT clause.\n"
            "9. Ensure all column references use the correct table aliases to prevent ambiguity.\n"
            "10. Use DISTINCT when the question implies unique values (e.g., unique users).\n"
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
            prompt = f"\n\nUser Query: {user_query} \n\n" + prompt
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
