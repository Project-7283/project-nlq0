"""
Mock Protocol Interface for local testing of A2A protocol.

In production, this would be the actual LexiQuery Protocol Interface.
For development, this mock allows testing without the full LexiQuery system.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Protocol Interface Mock",
    version="1.0.0",
    docs_url="/docs",
)

# In-memory registry of agents
agent_registry: Dict[str, dict] = {}


class AgentDescriptor(BaseModel):
    """Agent descriptor."""
    agent_id: str
    agent_name: str
    agent_type: str
    version: str
    endpoint: str
    platform: Optional[str] = None
    capabilities: List[str] = []
    metadata: dict = {}


class RegistrationRequest(BaseModel):
    """Agent registration request."""
    agent_descriptor: AgentDescriptor


class RegistrationResponse(BaseModel):
    """Registration response."""
    status: str
    agent_id: str
    message: str


class TaskRequest(BaseModel):
    """Task request from agent."""
    task_id: str
    journey_id: str
    agent_id: str
    action: str
    parameters: dict = {}


class TaskResponse(BaseModel):
    """Task response."""
    task_id: str
    journey_id: str
    status: str
    result: Optional[dict] = None
    error_message: Optional[str] = None


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    logger.info("Protocol Interface Mock starting up...")
    logger.info("Agent registry initialized")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "protocol_interface_mock",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/a2a/agents/register")
async def register_agent(descriptor: AgentDescriptor) -> RegistrationResponse:
    """
    Register a new agent.
    
    Called by agents on startup to advertise their capabilities.
    """
    agent_id = descriptor.agent_id
    
    # Store agent descriptor
    agent_registry[agent_id] = descriptor.model_dump()
    
    logger.info(
        f"Agent registered: {agent_id} ({descriptor.agent_type}) - {descriptor.endpoint}"
    )
    logger.info(f"  Capabilities: {', '.join(descriptor.capabilities)}")
    logger.info(f"  Platform: {descriptor.platform}")
    
    return RegistrationResponse(
        status="success",
        agent_id=agent_id,
        message=f"Agent {agent_id} registered successfully",
    )


@app.post("/a2a/agents/{agent_id}/deregister")
async def deregister_agent(agent_id: str) -> dict:
    """
    Deregister an agent.
    
    Called when agents shut down.
    """
    if agent_id in agent_registry:
        del agent_registry[agent_id]
        logger.info(f"Agent deregistered: {agent_id}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "message": f"Agent {agent_id} deregistered",
        }
    else:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")


@app.get("/a2a/agents")
async def list_agents() -> dict:
    """
    List all registered agents.
    """
    return {
        "agents": agent_registry,
        "count": len(agent_registry),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/a2a/agents/{agent_id}")
async def get_agent(agent_id: str) -> dict:
    """
    Get details of a specific agent.
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return agent_registry[agent_id]


@app.get("/a2a/agents/type/{agent_type}")
async def get_agents_by_type(agent_type: str) -> dict:
    """
    Get all agents of a specific type.
    """
    matching_agents = {
        agent_id: info
        for agent_id, info in agent_registry.items()
        if info.get("agent_type") == agent_type
    }
    
    return {
        "agent_type": agent_type,
        "agents": matching_agents,
        "count": len(matching_agents),
    }


@app.get("/a2a/agents/platform/{platform}")
async def get_agents_by_platform(platform: str) -> dict:
    """
    Get all agents supporting a specific platform.
    """
    matching_agents = {
        agent_id: info
        for agent_id, info in agent_registry.items()
        if info.get("platform") == platform or info.get("platform") is None
    }
    
    return {
        "platform": platform,
        "agents": matching_agents,
        "count": len(matching_agents),
    }


@app.get("/a2a/agents/{agent_id}/capabilities/{capability}")
async def get_capability(agent_id: str, capability: str) -> dict:
    """
    Get details about a specific capability of an agent.
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent = agent_registry[agent_id]
    if capability not in agent.get("capabilities", []):
        raise HTTPException(
            status_code=404,
            detail=f"Capability {capability} not found for agent {agent_id}",
        )
    
    return {
        "agent_id": agent_id,
        "capability": capability,
        "supported": True,
        "metadata": agent.get("metadata", {}),
    }


@app.put("/a2a/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, request_body: dict) -> dict:
    """
    Update agent status.
    """
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    status = request_body.get("status")
    details = request_body.get("details", {})
    
    logger.info(f"Agent {agent_id} status update: {status}")
    if details:
        logger.info(f"  Details: {details}")
    
    # Store status (could be persisted to database in production)
    agent_registry[agent_id]["last_status"] = status
    agent_registry[agent_id]["last_status_update"] = datetime.utcnow().isoformat()
    
    return {
        "agent_id": agent_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/a2a/tasks/{task_id}/result")
async def submit_task_result(task_id: str, result: TaskResponse) -> dict:
    """
    Submit task result.
    """
    logger.info(f"Task result submitted: {task_id} - Status: {result.status}")
    
    return {
        "task_id": task_id,
        "acknowledged": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/a2a/agents/discover")
async def discover_agents(agent_type: Optional[str] = None, platform: Optional[str] = None) -> dict:
    """
    Discover agents based on criteria.
    """
    agents = agent_registry.copy()
    
    if agent_type:
        agents = {
            k: v for k, v in agents.items() if v.get("agent_type") == agent_type
        }
    
    if platform:
        agents = {
            k: v
            for k, v in agents.items()
            if v.get("platform") == platform or v.get("platform") is None
        }
    
    return {
        "agents": agents,
        "count": len(agents),
        "filters": {
            "agent_type": agent_type,
            "platform": platform,
        },
    }


@app.get("/stats")
async def get_stats() -> dict:
    """
    Get protocol interface statistics.
    """
    agent_types = {}
    platforms = {}
    
    for agent_id, agent_info in agent_registry.items():
        agent_type = agent_info.get("agent_type", "unknown")
        platform = agent_info.get("platform", "multi")
        
        agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
        platforms[platform] = platforms.get(platform, 0) + 1
    
    return {
        "total_agents": len(agent_registry),
        "by_type": agent_types,
        "by_platform": platforms,
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Protocol Interface Mock on http://0.0.0.0:8001")
    logger.info("API Documentation available at http://localhost:8001/docs")
    
    uvicorn.run(
        "protocol_interface_mock:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info",
    )
