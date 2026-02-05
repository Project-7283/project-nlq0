"""
A2A Protocol agent registration module.
Handles registration with Protocol Interface.
"""

import asyncio
import logging
from typing import Optional

import httpx

from src.config import config
from src.models.a2a import AgentDescriptor, AgentMetadata, RegistrationRequest

logger = logging.getLogger(__name__)


async def build_agent_descriptor() -> AgentDescriptor:
    """Build the agent descriptor for discovery."""
    return AgentDescriptor(
        agent_id=config.agent_id,
        agent_name=config.agent_name,
        agent_type=config.agent_type,
        version=config.agent_version,
        endpoint=f"http://localhost:{config.port}",
        platform=config.platform,
        capabilities=[
            "generate_query",
            "execute_query",
            "validate_query",
            "explain_query",
        ],
        metadata=AgentMetadata(
            knowledge_domain="query_generation",
            supports_templates=False,
            supports_optimization=True,
            max_complexity="high",
            supported_dialects=["MySQL", "PostgreSQL", "T-SQL"],
            version_compatibility="1.0",
        ),
    )


async def register_agent_with_interface(
    descriptor: AgentDescriptor,
) -> bool:
    """
    Register this agent with the Protocol Interface.
    
    Args:
        descriptor: Agent descriptor to register
        
    Returns:
        True if registration successful, False otherwise
    """
    url = f"{config.protocol_interface_url}/a2a/agents/register"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=descriptor.model_dump(mode="json"),
                headers={"Content-Type": "application/json"},
            )
            
            if response.status_code == 200:
                logger.info(
                    f"Agent {config.agent_id} registered successfully with Protocol Interface"
                )
                return True
            else:
                logger.error(
                    f"Agent registration failed with status {response.status_code}: {response.text}"
                )
                return False
    
    except httpx.ConnectError as e:
        logger.warning(
            f"Could not connect to Protocol Interface at {config.protocol_interface_url}: {e}"
        )
        return False
    except Exception as e:
        logger.error(f"Agent registration error: {e}")
        return False


async def deregister_agent_with_interface() -> bool:
    """
    Deregister this agent from the Protocol Interface.
    
    Returns:
        True if deregistration successful, False otherwise
    """
    url = f"{config.protocol_interface_url}/a2a/agents/{config.agent_id}/deregister"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url)
            
            if response.status_code == 200:
                logger.info(f"Agent {config.agent_id} deregistered successfully")
                return True
            else:
                logger.warning(
                    f"Deregistration returned status {response.status_code}"
                )
                return False
    
    except Exception as e:
        logger.warning(f"Agent deregistration error: {e}")
        return False


async def register_with_retry(
    max_retries: int = 3,
    retry_delay_seconds: int = 5,
) -> bool:
    """
    Register agent with retry logic.
    
    Args:
        max_retries: Maximum number of registration attempts
        retry_delay_seconds: Delay between retries in seconds
        
    Returns:
        True if successful registration, False if all attempts failed
    """
    descriptor = await build_agent_descriptor()
    
    for attempt in range(max_retries):
        logger.info(f"Registration attempt {attempt + 1}/{max_retries}")
        
        success = await register_agent_with_interface(descriptor)
        if success:
            return True
        
        if attempt < max_retries - 1:
            logger.info(f"Retrying in {retry_delay_seconds} seconds...")
            await asyncio.sleep(retry_delay_seconds)
    
    logger.error(f"Failed to register agent after {max_retries} attempts")
    return False


async def get_agent_capability(capability: str) -> Optional[dict]:
    """
    Query Protocol Interface for agent capability details.
    
    Args:
        capability: Capability name
        
    Returns:
        Capability details or None if not found
    """
    url = (
        f"{config.protocol_interface_url}/a2a/agents/{config.agent_id}"
        f"/capabilities/{capability}"
    )
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Capability query returned status {response.status_code}")
                return None
    
    except Exception as e:
        logger.warning(f"Error querying capability: {e}")
        return None


async def update_agent_status(status: str, details: Optional[dict] = None) -> bool:
    """
    Update agent status in Protocol Interface.
    
    Args:
        status: Status string ('healthy', 'degraded', 'unhealthy')
        details: Optional status details
        
    Returns:
        True if update successful
    """
    url = f"{config.protocol_interface_url}/a2a/agents/{config.agent_id}/status"
    
    payload = {
        "status": status,
        "details": details or {},
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(url, json=payload)
            
            return response.status_code == 200
    
    except Exception as e:
        logger.warning(f"Error updating agent status: {e}")
        return False
