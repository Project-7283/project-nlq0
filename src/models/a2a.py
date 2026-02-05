"""
A2A Protocol models for agent-to-agent communication.
Based on LexiQuery A2A specification.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Any, Optional, Literal, List
from datetime import datetime


class A2ATaskRequest(BaseModel):
    """
    Request from Core Engine or other agent to this agent.
    """
    task_id: UUID = Field(description="Unique task identifier")
    journey_id: UUID = Field(description="Journey identifier for tracking")
    agent_id: str = Field(description="Requesting agent ID")
    action: str = Field(description="Action to perform: 'generate_query', 'validate_query', etc.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    timeout_seconds: int = Field(default=60, description="Task timeout in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "journey_id": "550e8400-e29b-41d4-a716-446655440001",
                "agent_id": "planner_agent_001",
                "action": "generate_query",
                "parameters": {
                    "natural_language": "Show all active users",
                    "platform": "sql",
                    "schema_hints": {"tables": ["users", "accounts"]},
                },
                "timeout_seconds": 60,
            }
        }


class QueryGenerationResult(BaseModel):
    """Result of query generation."""
    query: str = Field(description="Generated query string")
    platform: str = Field(description="Query platform: 'sql', 'kql', 'spl'")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    explanation: str = Field(description="Explanation of generated query")
    tables_involved: List[str] = Field(default_factory=list, description="Table names used")
    estimated_rows: Optional[int] = Field(None, description="Estimated row count")
    parameters: List[str] = Field(default_factory=list, description="Query parameters")
    optimizations: List[str] = Field(default_factory=list, description="Applied optimizations")


class ValidationResult(BaseModel):
    """Result of query validation."""
    is_valid: bool = Field(description="Whether query is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    performance_estimate: Optional[str] = Field(None, description="Performance estimate")


class TaskResultContent(BaseModel):
    """Container for task result content."""
    query_result: Optional[QueryGenerationResult] = None
    validation_result: Optional[ValidationResult] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_result": {
                    "query": "SELECT * FROM users WHERE status = 'active'",
                    "platform": "sql",
                    "confidence": 0.95,
                    "explanation": "Retrieved active users from users table",
                    "tables_involved": ["users"],
                    "estimated_rows": 5000,
                    "parameters": [],
                    "optimizations": ["indexed_search"],
                }
            }
        }


class CostInfo(BaseModel):
    """Cost tracking information."""
    llm_calls: int = Field(default=0, description="Number of LLM API calls")
    llm_tokens: int = Field(default=0, description="Total tokens used")
    execution_time_ms: float = Field(description="Execution time in milliseconds")


class A2ATaskResponse(BaseModel):
    """
    Response from this agent to Core Engine or requesting agent.
    """
    task_id: UUID = Field(description="Echo of request task_id")
    journey_id: UUID = Field(description="Echo of request journey_id")
    agent_id: str = Field(description="This agent's ID")
    status: Literal["success", "error", "timeout"] = Field(description="Task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    error_message: Optional[str] = Field(None, description="Error message if status=error")
    execution_time_ms: float = Field(description="Task execution time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    cost_info: Optional[CostInfo] = Field(None, description="Cost tracking information")

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "journey_id": "550e8400-e29b-41d4-a716-446655440001",
                "agent_id": "sql_query_agent_001",
                "status": "success",
                "result": {
                    "query_result": {
                        "query": "SELECT * FROM users WHERE status = 'active'",
                        "platform": "sql",
                        "confidence": 0.95,
                        "explanation": "Query generated successfully",
                        "tables_involved": ["users"],
                        "estimated_rows": 5000,
                        "parameters": [],
                        "optimizations": ["indexed_search"],
                    }
                },
                "execution_time_ms": 450.5,
                "cost_info": {
                    "llm_calls": 1,
                    "llm_tokens": 450,
                    "execution_time_ms": 450.5,
                },
            }
        }


class AgentMetadata(BaseModel):
    """Agent metadata."""
    knowledge_domain: str = Field(description="Domain of knowledge: 'query_generation', 'schema_analysis', etc.")
    supports_templates: bool = Field(default=False, description="Whether agent supports templates")
    supports_optimization: bool = Field(default=False, description="Whether agent can optimize queries")
    max_complexity: str = Field(default="medium", description="Max query complexity: 'low', 'medium', 'high'")
    supported_dialects: List[str] = Field(default_factory=list, description="Supported SQL dialects")
    version_compatibility: str = Field(default="1.0", description="A2A protocol version")


class AgentDescriptor(BaseModel):
    """
    Agent descriptor for discovery and registration.
    Returned by /a2a/descriptor endpoint.
    """
    agent_id: str = Field(description="Unique agent identifier")
    agent_name: str = Field(description="Human-readable agent name")
    agent_type: Literal["data", "knowledge", "planner"] = Field(description="Agent type")
    version: str = Field(description="Agent version")
    endpoint: str = Field(description="Agent HTTP endpoint URL")
    platform: Optional[str] = Field(None, description="Query platform: 'sql', 'kql', 'spl', or None for multi-platform")
    capabilities: List[str] = Field(description="Supported actions")
    metadata: AgentMetadata = Field(description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "sql_query_agent_001",
                "agent_name": "SQL Query Generator Agent",
                "agent_type": "data",
                "version": "1.0.0",
                "endpoint": "http://localhost:9022",
                "platform": "sql",
                "capabilities": ["generate_query", "validate_query"],
                "metadata": {
                    "knowledge_domain": "query_generation",
                    "supports_templates": True,
                    "supports_optimization": True,
                    "max_complexity": "high",
                    "supported_dialects": ["MySQL", "PostgreSQL", "T-SQL"],
                    "version_compatibility": "1.0",
                },
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "degraded", "unhealthy"] = Field(description="Health status")
    agent_id: str = Field(description="Agent ID")
    version: str = Field(description="Agent version")
    uptime_seconds: int = Field(description="Uptime in seconds")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Dependency health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class RegistrationRequest(BaseModel):
    """Agent registration request to Protocol Interface."""
    agent_descriptor: AgentDescriptor = Field(description="Agent descriptor")


class RegistrationResponse(BaseModel):
    """Response from Protocol Interface after registration."""
    status: Literal["success", "error"] = Field(description="Registration status")
    agent_id: str = Field(description="Registered agent ID")
    message: str = Field(description="Status message")
