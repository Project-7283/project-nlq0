import uvicorn
import json
import asyncio
import logging
import time
from decimal import Decimal
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.flows.nl_to_sql import process_nl_query_async
from src.utils.logging import app_logger, performance_logger
from src.config import config
from src.models.a2a import (
    A2ATaskRequest,
    A2ATaskResponse,
    AgentDescriptor,
    AgentMetadata,
    HealthCheckResponse,
)
from src.handlers.a2a_handlers import (
    handle_generate_query,
    handle_validate_query,
    handle_explain_query,
)
from src.modules.agent_registration import (
    register_with_retry,
    deregister_agent_with_interface,
    build_agent_descriptor,
)

logger = logging.getLogger(__name__)

# Create FastAPI app with A2A configuration
app = FastAPI(
    title=config.api_title,
    version=config.api_version,
    docs_url=config.api_docs_url,
    openapi_url=config.api_openapi_url,
)

# Track agent startup time
_startup_time = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


# ============================================================================
# TRADITIONAL ENDPOINTS
# ============================================================================

@app.post("/query")
async def query_endpoint(request: Request):
    data = await request.json()
    nl_query = data.get("query")
    
    if not nl_query:
        raise HTTPException(status_code=400, detail="Missing 'query' field")
    
    start_time = time.time()
    app_logger.info(f"Received query request: {nl_query}")
    
    try:
        sql, results = await process_nl_query_async(nl_query)
        
        duration = time.time() - start_time
        performance_logger.info(f"Query processed in {duration:.2f}s | Query: {nl_query[:50]}...")
        
        # Use custom encoder for Decimal
        json_str = json.dumps({"results": results, "sql": sql}, default=decimal_default)
        return JSONResponse(content=json.loads(json_str))
        
    except Exception as e:
        app_logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


# ============================================================================
# A2A PROTOCOL ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    global _startup_time
    _startup_time = datetime.utcnow()
    
    app_logger.info(f"Starting A2A Agent: {config.agent_id} v{config.agent_version}")
    
    # Register with Protocol Interface if enabled
    if config.auto_register:
        app_logger.info("Attempting to register with Protocol Interface...")
        success = await register_with_retry(
            max_retries=config.registration_retry_count,
            retry_delay_seconds=config.registration_retry_delay_seconds,
        )
        
        if success:
            app_logger.info("Agent successfully registered with Protocol Interface")
        else:
            app_logger.warning(
                "Agent registration with Protocol Interface failed - "
                "will operate in standalone mode"
            )


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up agent on shutdown."""
    app_logger.info(f"Shutting down A2A Agent: {config.agent_id}")
    
    if config.auto_register:
        await deregister_agent_with_interface()


@app.get("/a2a/descriptor")
async def get_agent_descriptor() -> AgentDescriptor:
    """
    Get agent descriptor for discovery by Protocol Interface.
    
    This endpoint is called during agent discovery to determine:
    - What capabilities the agent has
    - What platform(s) it supports
    - Where to send tasks
    
    Returns:
        AgentDescriptor: Complete agent information
    """
    descriptor = await build_agent_descriptor()
    return descriptor


@app.get("/health")
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns agent health status and dependency status.
    Called by orchestrator before invoking tasks.
    
    Returns:
        HealthCheckResponse: Health status information
    """
    global _startup_time
    
    uptime_seconds = 0
    if _startup_time:
        uptime_seconds = int((datetime.utcnow() - _startup_time).total_seconds())
    
    return HealthCheckResponse(
        status="healthy",
        agent_id=config.agent_id,
        version=config.agent_version,
        uptime_seconds=uptime_seconds,
        dependencies={
            "nlq_service": "healthy",  # Could implement actual health checks
            "database": "healthy",
        },
    )


@app.post("/a2a/task")
async def process_a2a_task(request: A2ATaskRequest) -> A2ATaskResponse:
    """
    Process A2A protocol task request.
    
    The action parameter determines what to do:
    - "generate_query": Create SQL from natural language
    - "validate_query": Validate generated query
    - "explain_query": Explain what a query does
    
    Args:
        request: A2A task request with task details
        
    Returns:
        A2ATaskResponse: Task result with status and output
        
    Raises:
        HTTPException: If action is unknown
    """
    action = request.action.lower()
    
    app_logger.info(
        f"[A2A Task {request.task_id}] Received action: {action} "
        f"from agent: {request.agent_id}"
    )
    
    try:
        if action == "generate_query":
            response = await handle_generate_query(request, config.agent_id)
        
        elif action == "validate_query":
            response = await handle_validate_query(request, config.agent_id)
        
        elif action == "explain_query":
            response = await handle_explain_query(request, config.agent_id)
        
        else:
            raise ValueError(f"Unknown action: {action}")
        
        return response
    
    except Exception as e:
        app_logger.error(f"[A2A Task {request.task_id}] Unhandled error: {e}")
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=config.agent_id,
            status="error",
            error_message=f"Unhandled error in agent: {str(e)}",
            execution_time_ms=0,
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/info")
async def get_agent_info():
    """
    Get detailed information about this agent.
    Useful for debugging and monitoring.
    """
    descriptor = await build_agent_descriptor()
    return {
        "agent": descriptor.model_dump(mode="json"),
        "config": {
            "host": config.host,
            "port": config.port,
            "auto_register": config.auto_register,
            "protocol_interface_url": config.protocol_interface_url,
        },
    }

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
