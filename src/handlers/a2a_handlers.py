"""
A2A Protocol handlers for processing tasks.
"""

import time
from typing import Dict, Any
from uuid import UUID
import logging

from src.models.a2a import (
    A2ATaskRequest,
    A2ATaskResponse,
    QueryGenerationResult,
    ValidationResult,
    CostInfo,
    TaskResultContent,
)
from src.flows.nl_to_sql import process_nl_query_async
from src.utils.logging import app_logger

logger = logging.getLogger(__name__)


async def handle_generate_query(
    request: A2ATaskRequest, agent_id: str
) -> A2ATaskResponse:
    """
    Handle query generation task.
    
    Input parameters:
    - natural_language: The user's natural language query
    - platform: Target platform ('sql', 'kql', 'spl')
    - schema_hints: Optional schema context
    - knowledge_context: Optional knowledge from other agents
    
    Returns: A2ATaskResponse with generated query
    """
    start_time = time.time()
    
    try:
        params = request.parameters or {}
        natural_language = params.get("natural_language")
        platform = params.get("platform", "sql")
        schema_hints = params.get("schema_hints", {})
        knowledge_context = params.get("knowledge_context", {})
        
        if not natural_language:
            raise ValueError("Missing 'natural_language' parameter")
        
        app_logger.info(
            f"[A2A Task {request.task_id}] Generating {platform} query for: {natural_language[:100]}"
        )
        
        # Call the existing NLQ processing pipeline
        sql_query, results = await process_nl_query_async(natural_language)
        
        if not sql_query:
            raise ValueError("Failed to generate query from natural language")
        
        # Extract tables from results or query
        tables_involved = extract_tables_from_query(sql_query)
        
        # Create result
        query_result = QueryGenerationResult(
            query=sql_query,
            platform=platform,
            confidence=0.85,  # Default confidence, could be improved
            explanation=f"Generated {platform} query from natural language input",
            tables_involved=tables_involved,
            estimated_rows=None,
            parameters=[],
            optimizations=["indexed_search"],
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        result_content = TaskResultContent(query_result=query_result)
        
        app_logger.info(
            f"[A2A Task {request.task_id}] Query generated successfully in {elapsed_ms:.2f}ms"
        )
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="success",
            result=result_content.model_dump(exclude_none=True),
            execution_time_ms=elapsed_ms,
            cost_info=CostInfo(
                llm_calls=1,
                llm_tokens=0,  # Could track actual tokens
                execution_time_ms=elapsed_ms,
            ),
        )
    
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        app_logger.error(
            f"[A2A Task {request.task_id}] Query generation failed: {error_msg}"
        )
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="error",
            error_message=error_msg,
            execution_time_ms=elapsed_ms,
        )


async def handle_validate_query(
    request: A2ATaskRequest, agent_id: str
) -> A2ATaskResponse:
    """
    Handle query validation task.
    
    Input parameters:
    - query: The query to validate
    - platform: Query platform ('sql', 'kql', 'spl')
    
    Returns: A2ATaskResponse with validation results
    """
    start_time = time.time()
    
    try:
        params = request.parameters or {}
        query = params.get("query")
        platform = params.get("platform", "sql")
        
        if not query:
            raise ValueError("Missing 'query' parameter")
        
        app_logger.info(
            f"[A2A Task {request.task_id}] Validating {platform} query"
        )
        
        # Perform basic validation
        errors = []
        warnings = []
        suggestions = []
        
        # SQL-specific validation
        if platform == "sql":
            # Basic SQL validation
            query_upper = query.upper().strip()
            
            # Check for required keywords
            if not any(
                kw in query_upper for kw in ["SELECT", "INSERT", "UPDATE", "DELETE"]
            ):
                errors.append("Query must contain SELECT, INSERT, UPDATE, or DELETE")
            
            # Warnings
            if "SELECT *" in query_upper:
                warnings.append("SELECT * detected - specify columns for better performance")
            
            if "WHERE" not in query_upper and "SELECT" in query_upper:
                warnings.append("No WHERE clause - query may return all rows")
            
            # Suggestions
            if "SELECT" in query_upper and "LIMIT" not in query_upper:
                suggestions.append("Consider adding LIMIT to prevent excessive data retrieval")
        
        is_valid = len(errors) == 0
        
        validation_result = ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            performance_estimate="Unknown",
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        result_content = TaskResultContent(validation_result=validation_result)
        
        app_logger.info(
            f"[A2A Task {request.task_id}] Validation completed in {elapsed_ms:.2f}ms - Valid: {is_valid}"
        )
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="success",
            result=result_content.model_dump(exclude_none=True),
            execution_time_ms=elapsed_ms,
            cost_info=CostInfo(
                llm_calls=0,
                llm_tokens=0,
                execution_time_ms=elapsed_ms,
            ),
        )
    
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        app_logger.error(
            f"[A2A Task {request.task_id}] Query validation failed: {error_msg}"
        )
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="error",
            error_message=error_msg,
            execution_time_ms=elapsed_ms,
        )


def extract_tables_from_query(query: str) -> list:
    """
    Extract table names from SQL query.
    Basic implementation - could be enhanced.
    """
    import re
    
    tables = []
    
    # Pattern for FROM table_name
    from_pattern = r"FROM\s+(\w+)"
    from_matches = re.findall(from_pattern, query, re.IGNORECASE)
    tables.extend(from_matches)
    
    # Pattern for JOIN table_name
    join_pattern = r"JOIN\s+(\w+)"
    join_matches = re.findall(join_pattern, query, re.IGNORECASE)
    tables.extend(join_matches)
    
    # Remove duplicates and return
    return list(set(tables))


async def handle_explain_query(
    request: A2ATaskRequest, agent_id: str
) -> A2ATaskResponse:
    """
    Handle query explanation task.
    
    Input parameters:
    - query: The query to explain
    - platform: Query platform
    
    Returns: A2ATaskResponse with explanation
    """
    start_time = time.time()
    
    try:
        params = request.parameters or {}
        query = params.get("query")
        platform = params.get("platform", "sql")
        
        if not query:
            raise ValueError("Missing 'query' parameter")
        
        app_logger.info(
            f"[A2A Task {request.task_id}] Explaining {platform} query"
        )
        
        # Generate explanation
        explanation = generate_query_explanation(query, platform)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        result_content = {
            "explanation": explanation,
            "query": query,
            "platform": platform,
        }
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="success",
            result=result_content,
            execution_time_ms=elapsed_ms,
        )
    
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        app_logger.error(
            f"[A2A Task {request.task_id}] Query explanation failed: {error_msg}"
        )
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="error",
            error_message=error_msg,
            execution_time_ms=elapsed_ms,
        )


async def handle_execute_query(
    request: A2ATaskRequest, agent_id: str
) -> A2ATaskResponse:
    """
    Handle query execution task.
    
    Generate SQL from natural language AND execute it.
    
    Input parameters:
    - natural_language: The user's natural language query
    - platform: Target platform ('sql', 'kql', 'spl')
    - execute: Whether to execute the query (default: True)
    
    Returns: A2ATaskResponse with generated query and execution results
    """
    start_time = time.time()
    
    try:
        params = request.parameters or {}
        natural_language = params.get("natural_language")
        platform = params.get("platform", "sql")
        
        if not natural_language:
            raise ValueError("Missing 'natural_language' parameter")
        
        app_logger.info(
            f"[A2A Task {request.task_id}] Executing {platform} query for: {natural_language[:100]}"
        )
        
        # Call the existing NLQ processing pipeline which generates AND executes
        sql_query, results = await process_nl_query_async(natural_language)
        
        if not sql_query:
            raise ValueError("Failed to generate query from natural language")
        
        # Extract tables from query
        tables_involved = extract_tables_from_query(sql_query)
        
        # Create result
        result_content = {
            "query": sql_query,
            "platform": platform,
            "results": results,
            "row_count": len(results) if isinstance(results, list) else 0,
            "tables_involved": tables_involved,
            "executed": True,
        }
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        app_logger.info(
            f"[A2A Task {request.task_id}] Query executed successfully in {elapsed_ms:.2f}ms, "
            f"returned {len(results) if isinstance(results, list) else 0} rows"
        )
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="success",
            result=result_content,
            execution_time_ms=elapsed_ms,
            cost_info=CostInfo(
                llm_calls=1,
                llm_tokens=0,  # Could track actual tokens
                execution_time_ms=elapsed_ms,
            ),
        )
    
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        app_logger.error(
            f"[A2A Task {request.task_id}] Query execution failed: {error_msg}"
        )
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=agent_id,
            status="error",
            error_message=error_msg,
            execution_time_ms=elapsed_ms,
        )


def generate_query_explanation(query: str, platform: str) -> str:
    """
    Generate a human-readable explanation of the query.
    """
    explanation_parts = []
    
    query_upper = query.upper()
    
    # Identify main operation
    if "SELECT" in query_upper:
        explanation_parts.append("Retrieves data from tables")
    elif "INSERT" in query_upper:
        explanation_parts.append("Inserts new rows into table")
    elif "UPDATE" in query_upper:
        explanation_parts.append("Updates existing rows in table")
    elif "DELETE" in query_upper:
        explanation_parts.append("Deletes rows from table")
    
    # Identify tables
    import re
    
    from_pattern = r"FROM\s+(\w+)"
    tables = re.findall(from_pattern, query, re.IGNORECASE)
    if tables:
        explanation_parts.append(f"from {', '.join(tables)}")
    
    # Identify conditions
    if "WHERE" in query_upper:
        explanation_parts.append("with specified conditions")
    
    # Identify ordering
    if "ORDER BY" in query_upper:
        explanation_parts.append("ordered by specified columns")
    
    return ". ".join(explanation_parts) if explanation_parts else "Executes a database query"
