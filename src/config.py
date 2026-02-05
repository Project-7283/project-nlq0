"""
A2A Protocol Configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class AgentConfig(BaseSettings):
    """Configuration for A2A protocol agent."""
    
    # Agent identification
    agent_id: str = "sql_query_agent_001"
    agent_name: str = "SQL Query Generator Agent"
    agent_version: str = "1.0.0"
    agent_type: str = "data"  # "data", "knowledge", "planner"
    
    # Platform
    platform: Optional[str] = "sql"  # "sql", "kql", "spl", or None for multi-platform
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 9022
    
    # A2A Protocol Interface (for agent registration)
    protocol_interface_url: str = "http://localhost:8001"
    auto_register: bool = True
    registration_retry_count: int = 3
    registration_retry_delay_seconds: int = 5
    
    # API configuration
    api_title: str = "NLQ to SQL Query Generator Agent"
    api_version: str = "1.0.0"
    api_docs_url: str = "/docs"
    api_openapi_url: str = "/openapi.json"
    
    # Health check configuration
    health_check_interval_seconds: int = 30
    
    # Database/service configuration
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "nlq_database"
    
    # LLM configuration
    gemini_api_key: Optional[str] = None
    ollama_url: Optional[str] = "http://localhost:11434"
    openai_api_key: Optional[str] = None
    
    # Vector database
    chroma_db_path: str = "./chroma_db"
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def get_agent_config() -> AgentConfig:
    """Get singleton agent configuration."""
    return AgentConfig()


config = get_agent_config()
