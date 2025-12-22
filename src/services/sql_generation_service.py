import json
import os
import asyncio
from typing import List, Dict, Any, Optional
from .inference import InferenceServiceProtocol
from .mysql_service import MySQLService
from ..modules.semantic_graph import SemanticGraph
from src.utils.logging import app_logger

class SQLGenerationService:
    """
    Service to generate SQL from a semantic graph path and run it on the database.
    Utilizes LLM for SQL generation and MySQLService for execution.
    """
    def __init__(self, model: InferenceServiceProtocol, sql_service: MySQLService, governance_service=None):
        self.model = model
        self.sql_service = sql_service
        self.governance = governance_service
        self.governance_enabled = os.getenv("DATA_GOVERNANCE_ENABLED", "true").lower() == "true"

    def _format_properties(self, properties: Dict[str, Any], indent: int = 0) -> str:
        if not properties:
            return "(no properties)"
        
        lines = []
        indent_str = "  " * indent
        priority_keys = ['description', 'business_purpose', 'semantic_meaning', 'business_relevance', 
                        'Field', 'Type', 'Comment', 'row_count', 'data_domain', 'business_impact']
        
        priority_props = {k: properties[k] for k in priority_keys if k in properties}
        other_props = {k: v for k, v in properties.items() if k not in priority_keys}
        
        for key, value in priority_props.items():
            lines.append(self._format_property_line(key, value, indent_str))
        for key, value in other_props.items():
            lines.append(self._format_property_line(key, value, indent_str))
        
        return "\n".join([l for l in lines if l])
    
    def _format_property_line(self, key: str, value: Any, indent_str: str) -> str:
        if value is None or value == "***MASKED***":
            return ""
        
        if isinstance(value, (bool, int, float, str)):
            return f"{indent_str}• {key}: {value}"
        elif isinstance(value, list):
            if not value: return ""
            items = ", ".join([str(v) for v in value])
            return f"{indent_str}• {key}: [{items}]"
        elif isinstance(value, dict):
            if not value: return ""
            if len(value) <= 3 and all(isinstance(v, (str, int, float, bool)) for v in value.values()):
                items = ", ".join([f"{k}={v}" for k, v in value.items()])
                return f"{indent_str}• {key}: {{{items}}}"
            else:
                nested_lines = [f"{indent_str}• {key}:"]
                for k, v in value.items():
                    nested_lines.append(f"{indent_str}  - {k}: {v}")
                return "\n".join(nested_lines)
        return f"{indent_str}• {key}: {str(value)}"

    def path_to_sql_prompt(self, path: List[str], graph: SemanticGraph) -> str:
        if not path or len(path) < 2:
            raise ValueError("Path must have at least two nodes (start and end).")
        
        edge_descriptions = []
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i+1]
            edge = graph.get_edge_details(from_node, to_node)
            desc = f"{from_node} -> {to_node} (condition: {edge.get('condition')}, properties: {edge.get('properties', {})})"
            edge_descriptions.append(desc)
        
        schema_descriptions = []
        for node in path:
            node_data = graph.get_node_details(node)
            node_type = node_data.get('node_type', 'unknown')
            node_props = node_data.get('properties', {})
            
            node_desc = [f"\n## {node} ({node_type})"]
            
            # Handle Virtual Nodes
            if node_type == 'virtual':
                sql_fragment = node_props.get('sql_fragment')
                if sql_fragment:
                    node_desc.append(f"\n**MANDATORY SQL FRAGMENT**: `{sql_fragment}`")
                    node_desc.append("You MUST incorporate this fragment into your query logic.")

            if node_props:
                formatted_props = self._format_properties(node_props)
                if formatted_props and formatted_props != "(no properties)":
                    node_desc.append(formatted_props)
            
            neighbors = graph.get_neighbors_by_condition(node_id=node, condition="association")
            
            if self.governance_enabled and self.governance:
                filtered_neighbors = {}
                for neighbor, edge_data in neighbors.items():
                    col_name = neighbor.split('.')[-1] if '.' in neighbor else neighbor
                    if not self.governance.is_sensitive_column(col_name):
                        filtered_neighbors[neighbor] = edge_data
                neighbors = filtered_neighbors
            
            if neighbors:
                node_desc.append("\n### Columns:")
                for neighbor, edge_data in neighbors.items():
                    neighbor_data = graph.get_node_details(neighbor)
                    neighbor_props = neighbor_data.get('properties', {})
                    col_name = neighbor.split('.')[-1] if '.' in neighbor else neighbor
                    col_desc = [f"- **{col_name}**"]
                    col_type = neighbor_props.get('Type', '')
                    col_comment = neighbor_props.get('Comment', neighbor_props.get('description', ''))
                    
                    if col_type: col_desc.append(f" ({col_type})")
                    if col_comment: col_desc.append(f" - {col_comment}")
                    
                    semantic = neighbor_props.get('semantic_meaning', '')
                    business = neighbor_props.get('business_relevance', '')
                    if semantic or business:
                        extra_info = []
                        if semantic: extra_info.append(f"Semantic: {semantic}")
                        if business: extra_info.append(f"Business: {business}")
                        col_desc.append(f" [{'; '.join(extra_info)}]")
                    
                    node_desc.append("".join(col_desc))
            schema_descriptions.append("\n".join(node_desc))
        
        schema_section = "Table schemas (sensitive columns filtered):\n" + "\n".join(schema_descriptions) + "\n" if schema_descriptions else ""
        
        return (
            "Given the following path in a database schema graph, generate a SQL query that retrieves the relevant data.\n"
            "Table Joining Path: " + " -> ".join(path) + "\n"
            "Joining Edge details: " + "; ".join(edge_descriptions) + "\n"
            "When creating the SQL, follow these guidelines:\n"
            "1. Only select the columns needed to answer the question. Avoid 'SELECT *'.\n"
            "2. Name any aggregated fields using clear aliases.\n"
            "3. Include WHERE filters that match the user's intent.\n"
            "4. Use GROUP BY for aggregations.\n"
            "5. Order the results logically.\n"
            "6. Limit rows if requested.\n"
            "7. Use meaningful table aliases.\n"
            "8. Avoid unnecessary joins.\n"
            "9. Ensure correct table aliases for all columns.\n"
            "10. Use DISTINCT when appropriate.\n"
            "Respond ONLY with a JSON object: { \"sql\": \"...\" }" + "\n"
            f"{schema_section}"
        )

    def generate_sql(self, path: List[str], graph: SemanticGraph, user_query: str = "") -> str:
        prompt = self.path_to_sql_prompt(path, graph)
        if user_query:
            prompt = f"\n\nUser Query: {user_query} \n\n" + prompt
        
        schema = {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}
        result = self.model.get_structured_output(prompt, schema)
        
        if isinstance(result, dict) and "sql" in result:
            sql = result["sql"]
            return self._validate_and_sanitize(sql)
        raise ValueError("LLM did not return a valid SQL object.")

    async def generate_sql_async(self, path: List[str], graph: SemanticGraph, user_query: str = "") -> str:
        prompt = self.path_to_sql_prompt(path, graph)
        if user_query:
            prompt = f"\n\nUser Query: {user_query} \n\n" + prompt
        
        schema = {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}
        result = await self.model.get_structured_output_async(prompt, schema)
        
        if isinstance(result, dict) and "sql" in result:
            sql = result["sql"]
            return self._validate_and_sanitize(sql)
        raise ValueError("LLM did not return a valid SQL object.")

    def _validate_and_sanitize(self, sql: str) -> str:
        if self.governance_enabled and self.governance:
            is_valid, error_msg = self.governance.validate_query(sql)
            if not is_valid:
                app_logger.warning(f"SQL violates governance: {error_msg}. Sanitizing...")
                return self.governance.sanitize_sql(sql)
        return sql

    def correct_sql(self, invalid_sql: str, error_message: str, user_query: str) -> str:
        prompt = self._get_correction_prompt(invalid_sql, error_message, user_query)
        schema = {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}
        result = self.model.get_structured_output(prompt, schema)
        if isinstance(result, dict) and "sql" in result:
            return result["sql"]
        raise ValueError("LLM did not return a valid corrected SQL object.")

    async def correct_sql_async(self, invalid_sql: str, error_message: str, user_query: str) -> str:
        prompt = self._get_correction_prompt(invalid_sql, error_message, user_query)
        schema = {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}
        result = await self.model.get_structured_output_async(prompt, schema)
        if isinstance(result, dict) and "sql" in result:
            return result["sql"]
        raise ValueError("LLM did not return a valid corrected SQL object.")

    def _get_correction_prompt(self, invalid_sql: str, error_message: str, user_query: str) -> str:
        return f"""
        The following SQL query failed to execute.
        User Query: {user_query}
        Invalid SQL: {invalid_sql}
        Error Message: {error_message}
        Please correct the SQL query. Respond ONLY with a JSON object: {{ "sql": "..." }}
        """

    def run_sql(self, sql: str) -> List[Any]:
        return self.sql_service.execute_query(sql)

    async def run_sql_async(self, sql: str) -> List[Any]:
        return await self.sql_service.execute_query_async(sql)

    def generate_and_run(self, path: List[str], graph: SemanticGraph, user_query: str = "") -> Dict[str, Any]:
        sql = self.generate_sql(path, graph, user_query)
        results = self.run_sql(sql)
        return {"sql": sql, "results": results}

    async def generate_and_run_async(self, path: List[str], graph: SemanticGraph, user_query: str = "") -> Dict[str, Any]:
        sql = await self.generate_sql_async(path, graph, user_query)
        results = await self.run_sql_async(sql)
        return {"sql": sql, "results": results}
