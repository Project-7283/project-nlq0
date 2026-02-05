# A2A Protocol Integration Guide for NLQ-to-SQL/KQL Services

**Version**: 1.0  
**Date**: February 6, 2026  
**Target**: Integrating existing NLQ (Natural Language Query) services with LexiQuery A2A ecosystem

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture & Concepts](#architecture--concepts)
3. [Core Requirements](#core-requirements)
4. [Implementation Steps](#implementation-steps)
5. [Data Models](#data-models)
6. [Endpoint Specifications](#endpoint-specifications)
7. [Agent Registration](#agent-registration)
8. [Testing & Validation](#testing--validation)
9. [Examples](#examples)

---

## Overview

### What is A2A Protocol?

**A2A (Agent-to-Agent)** is a lightweight HTTP-based protocol for agents to coordinate and share work in the LexiQuery ecosystem. It enables:

- Agent discovery and capability advertisement
- Task invocation between agents
- Cost tracking and accounting
- Context propagation across workflow steps

### Your Service's Role

Your existing NLQ-to-SQL/KQL service will become a **Data Agent** in the LexiQuery system:

```
User Query
    ↓
Core Engine (Orchestrator)
    ↓
Planner Agent (decides workflow)
    ↓
Knowledge Agents (provide context) ← Your Service Here (as Data Agent)
    ↓
Your Service (generates query)
    ↓
Response
```

---

## Architecture & Concepts

### Agent Types in LexiQuery

| Type | Role | Example |
|------|------|---------|
| **Planner** | Creates workflow plans | Determines which knowledge/data agents to use |
| **Knowledge** | Provides context | SOP procedures, error patterns, schema info |
| **Data** | Generates queries | Your SQL/KQL generation service |

Your service is a **Data Agent**.

### Key Concepts

#### 1. Capabilities

Declare what your agent can do:

```python
capabilities = [
    "generate_query",      # Core capability
    "execute_query",       # Optional: if you can execute
    "validate_query",      # Optional: if you validate
    "explain_query"        # Optional: if you can explain
]
```

#### 2. Platforms

Which platforms can your service generate queries for?

```python
platform = "sql"  # "sql", "kql", "spl"
# OR support multiple with separate agent instances
```

#### 3. Metadata

Additional context about your agent:

```python
metadata = {
    "knowledge_domain": "data_generation",  # For data agents
    "supports_multi_platform": False,
    "max_query_complexity": "high",
    "version": "1.0.0"
}
```

#### 4. Endpoints

Your service must expose HTTP endpoints:

```
GET  /a2a/descriptor        # Agent information
GET  /health               # Health check
POST /a2a/task             # Task invocation
```

---

## Core Requirements

### 1. HTTP Server

Your service must be an HTTP server (FastAPI recommended):

```python
from fastapi import FastAPI

app = FastAPI(
    title="SQL Query Generator Agent",
    version="1.0.0"
)
```

### 2. Required Models

You'll need Pydantic models for A2A communication:

```python
from pydantic import BaseModel
from uuid import UUID
from typing import Dict, Any, Optional

class A2ATaskRequest(BaseModel):
    task_id: UUID
    journey_id: UUID
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    timeout_seconds: int = 60

class A2ATaskResponse(BaseModel):
    task_id: UUID
    journey_id: UUID
    agent_id: str
    status: str  # "success", "error"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float
    cost_info: Optional[Dict[str, Any]] = None
```

### 3. Port Assignment

Pick an unused port for your agent:

```
9020 - KQL Data Agent
9021 - SPL Data Agent
9022 - SQL Data Agent
```

---

## Implementation Steps

### Step 1: Add A2A Model Imports

Create or update your models to match LexiQuery's A2A protocol:

**`models/a2a.py`**:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Any, Optional, Literal
from datetime import datetime

class A2ATaskRequest(BaseModel):
    task_id: UUID
    journey_id: UUID
    agent_id: str
    action: str  # "generate_query", "validate_query"
    parameters: Dict[str, Any]
    timeout_seconds: int = 60

class A2ATaskResponse(BaseModel):
    task_id: UUID
    journey_id: UUID
    agent_id: str
    status: Literal["success", "error", "timeout"]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cost_info: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
```

### Step 2: Create Agent Configuration

**`config.py`**:
```python
from pydantic_settings import BaseSettings

class AgentConfig(BaseSettings):
    # Agent identification
    agent_id: str = "sql_query_agent_001"
    agent_name: str = "SQL Query Generator Agent"
    agent_version: str = "1.0.0"
    agent_type: str = "data"
    
    # Platform
    platform: str = "sql"  # "sql", "kql", "spl"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 9022
    
    # Protocol Interface (for registration)
    protocol_interface_url: str = "http://localhost:8001"
    
    # Your existing NLQ service config
    nlq_service_url: str = "http://localhost:5000"
    nlq_model: str = "sql-generator-v1"
    
    class Config:
        env_file = ".env"

config = AgentConfig()
```

### Step 3: Implement Agent Descriptor Endpoint

**`main.py`**:
```python
from fastapi import FastAPI
from config import config

app = FastAPI(
    title=config.agent_name,
    version=config.agent_version
)

@app.get("/a2a/descriptor")
async def agent_descriptor():
    """
    Return agent information.
    
    This is called by the Protocol Interface during discovery.
    """
    return {
        "agent_id": config.agent_id,
        "agent_name": config.agent_name,
        "agent_type": config.agent_type,
        "version": config.agent_version,
        "endpoint": f"http://localhost:{config.port}",
        "platform": config.platform,
        "capabilities": [
            "generate_query",
            "validate_query"
        ],
        "metadata": {
            "knowledge_domain": "query_generation",
            "supports_templates": True,
            "supports_optimization": True,
            "max_complexity": "high"
        }
    }
```

### Step 4: Implement Health Check

```python
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_id": config.agent_id,
        "version": config.agent_version,
        "uptime_seconds": 0  # Add actual uptime tracking
    }
```

### Step 5: Implement Task Endpoint

This is where your NLQ service does its work:

```python
import time
from models.a2a import A2ATaskRequest, A2ATaskResponse

@app.post("/a2a/task")
async def process_task(request: A2ATaskRequest) -> A2ATaskResponse:
    """
    Process A2A task request.
    
    The action parameter determines what to do:
    - "generate_query": Create SQL/KQL from natural language
    - "validate_query": Validate generated query
    """
    start_time = time.time()
    
    try:
        if request.action == "generate_query":
            result = await handle_generate_query(request)
        elif request.action == "validate_query":
            result = await handle_validate_query(request)
        else:
            raise ValueError(f"Unknown action: {request.action}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=config.agent_id,
            status="success",
            result=result,
            execution_time_ms=elapsed_ms,
            cost_info={
                "llm_calls": 1,
                "llm_tokens": 450,  # Track actual usage
                "execution_time_ms": elapsed_ms
            }
        )
    
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=config.agent_id,
            status="error",
            error_message=str(e),
            execution_time_ms=elapsed_ms
        )
```

### Step 6: Implement Action Handlers

**`handlers.py`**:
```python
from typing import Dict, Any
from models.a2a import A2ATaskRequest

async def handle_generate_query(request: A2ATaskRequest) -> Dict[str, Any]:
    """
    Generate query from natural language.
    
    Input parameters:
    {
        "natural_language": "Show all users created in the last week",
        "platform": "sql",
        "schema_hints": {...},
        "knowledge_context": {...}  # Optional context from knowledge agents
    }
    
    Output:
    {
        "query_result": {
            "query": "SELECT * FROM users WHERE created_at > ...",
            "platform": "sql",
            "confidence": 0.92,
            "explanation": "Filtered users table by creation date",
            "tables_involved": ["users"],
            "estimated_rows": 1500
        }
    }
    """
    params = request.parameters or {}
    natural_language = params.get("natural_language")
    platform = params.get("platform", config.platform)
    schema_hints = params.get("schema_hints", {})
    knowledge_context = params.get("knowledge_context", {})
    
    # Call your existing NLQ service
    query = await your_nlq_service.generate_query(
        natural_language=natural_language,
        platform=platform,
        schema_hints=schema_hints,
        context=knowledge_context
    )
    
    return {
        "query_result": {
            "query": query.sql,
            "platform": platform,
            "confidence": query.confidence_score,
            "explanation": query.reasoning,
            "tables_involved": query.tables,
            "estimated_rows": query.estimated_rows,
            "parameters": query.bind_params,
            "optimizations": query.optimizations_applied
        }
    }

async def handle_validate_query(request: A2ATaskRequest) -> Dict[str, Any]:
    """
    Validate a generated query.
    
    Input:
    {
        "query": "SELECT * FROM users",
        "platform": "sql"
    }
    
    Output:
    {
        "validation_result": {
            "is_valid": True,
            "errors": [],
            "warnings": ["No WHERE clause specified"],
            "suggestions": ["Add date filter to improve performance"]
        }
    }
    """
    params = request.parameters or {}
    query = params.get("query")
    platform = params.get("platform", config.platform)
    
    # Call your validation service
    validation = await your_nlq_service.validate_query(
        query=query,
        platform=platform
    )
    
    return {
        "validation_result": {
            "is_valid": validation.is_valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "suggestions": validation.suggestions,
            "performance_estimate": validation.estimated_rows
        }
    }
```

### Step 7: Register with Protocol Interface

**`registration.py`**:
```python
import httpx
from config import config

async def register_agent():
    """
    Register this agent with the Protocol Interface.
    
    This makes your agent discoverable by the Core Engine.
    """
    descriptor = {
        "agent_id": config.agent_id,
        "agent_name": config.agent_name,
        "agent_type": config.agent_type,
        "version": config.agent_version,
        "endpoint": f"http://localhost:{config.port}",
        "platform": config.platform,
        "capabilities": [
            "generate_query",
            "validate_query"
        ],
        "metadata": {
            "knowledge_domain": "query_generation",
            "supports_templates": True,
            "max_complexity": "high"
        }
    }
    
    url = f"{config.protocol_interface_url}/a2a/agents/register"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=descriptor)
        
        if response.status_code == 200:
            print(f"Agent {config.agent_id} registered successfully")
        else:
            print(f"Registration failed: {response.text}")

# Call on startup
@app.on_event("startup")
async def startup():
    await register_agent()
```

---

## Data Models

### Agent Descriptor (Discovery)

```python
{
    "agent_id": "sql_query_agent_001",
    "agent_type": "data",
    "agent_name": "SQL Query Generator",
    "endpoint": "http://localhost:9022",
    "version": "1.0.0",
    "platform": "sql",
    "capabilities": [
        "generate_query",
        "validate_query",
        "explain_query"
    ],
    "metadata": {
        "knowledge_domain": "query_generation",
        "supports_templates": true,
        "supports_optimization": true,
        "max_complexity": "high",
        "supported_dialects": ["T-SQL", "MySQL", "PostgreSQL"]
    }
}
```

### Task Request

```python
{
    "task_id": "uuid",
    "journey_id": "uuid",
    "agent_id": "sql_query_agent_001",
    "action": "generate_query",
    "parameters": {
        "natural_language": "Show all active users",
        "platform": "sql",
        "schema_hints": {
            "tables": ["users", "accounts"],
            "columns": {
                "users": ["id", "name", "status", "created_at"]
            }
        },
        "knowledge_context": {
            "sop": {
                "procedures": [...]
            }
        }
    },
    "timeout_seconds": 60
}
```

### Task Response

```python
{
    "task_id": "uuid",
    "journey_id": "uuid",
    "agent_id": "sql_query_agent_001",
    "status": "success",
    "result": {
        "query_result": {
            "query": "SELECT * FROM users WHERE status = 'active'",
            "platform": "sql",
            "confidence": 0.92,
            "explanation": "Queried users table filtering by active status",
            "tables_involved": ["users"],
            "estimated_rows": 5000,
            "parameters": [],
            "optimizations": ["indexed_search"]
        }
    },
    "execution_time_ms": 450.5,
    "cost_info": {
        "llm_calls": 1,
        "llm_tokens": 450,
        "execution_time_ms": 450.5
    }
}
```

---

## Endpoint Specifications

### 1. Agent Descriptor Endpoint

**Endpoint**: `GET /a2a/descriptor`

**Purpose**: Allow Protocol Interface to discover agent capabilities

**Response**:
```json
{
    "agent_id": "string",
    "agent_type": "data|knowledge|planner",
    "agent_name": "string",
    "version": "string",
    "endpoint": "http://...",
    "platform": "sql|kql|spl",
    "capabilities": ["string"],
    "metadata": {}
}
```

**Usage**:
- Called by Protocol Interface during agent discovery
- Called by Core Engine to validate agent capabilities
- Called before invoking agent to check version

### 2. Health Check Endpoint

**Endpoint**: `GET /health`

**Purpose**: Verify agent is running and ready

**Response**:
```json
{
    "status": "healthy|degraded|unhealthy",
    "agent_id": "string",
    "version": "string",
    "uptime_seconds": 0,
    "dependencies": {
        "nlq_service": "healthy",
        "database": "healthy"
    }
}
```

**Usage**:
- Called by orchestrator to check agent health before invocation
- Used for monitoring and alerting
- Can be called frequently (add caching if needed)

### 3. Task Invocation Endpoint

**Endpoint**: `POST /a2a/task`

**Purpose**: Execute agent task

**Request Body**:
```json
{
    "task_id": "uuid",
    "journey_id": "uuid",
    "agent_id": "string",
    "action": "string",
    "parameters": {},
    "timeout_seconds": 60
}
```

**Response**:
```json
{
    "task_id": "uuid",
    "journey_id": "uuid",
    "agent_id": "string",
    "status": "success|error|timeout",
    "result": {},
    "error_message": null,
    "execution_time_ms": 0,
    "cost_info": {
        "llm_calls": 1,
        "llm_tokens": 450,
        "execution_time_ms": 450.5
    }
}
```

**Error Handling**:
```json
{
    "task_id": "uuid",
    "journey_id": "uuid",
    "agent_id": "string",
    "status": "error",
    "error_message": "Query generation failed: Invalid table reference",
    "execution_time_ms": 150.0
}
```

---

## Agent Registration

### Method 1: Manual Registration (Development)

Post to Protocol Interface manually:

```bash
curl -X POST http://localhost:8001/a2a/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "sql_query_agent_001",
    "agent_type": "data",
    "agent_name": "SQL Query Generator",
    "endpoint": "http://localhost:9022",
    "platform": "sql",
    "capabilities": ["generate_query"]
  }'
```

### Method 2: Automatic Registration (Startup)

Register on service startup:

```python
@app.on_event("startup")
async def startup_event():
    await register_with_protocol_interface()
    
@app.on_event("shutdown")
async def shutdown_event():
    await deregister_from_protocol_interface()
```

### Method 3: Environment-Based (Production)

Use environment variables for registration:

**`.env`**:
```
AGENT_ID=sql_query_agent_001
AGENT_NAME=SQL Query Generator
AGENT_TYPE=data
PLATFORM=sql
PROTOCOL_INTERFACE_URL=http://protocol-interface:8001
AUTO_REGISTER=true
```

---

## Testing & Validation

### 1. Test Agent Discovery

```bash
# Get agent descriptor
curl http://localhost:9022/a2a/descriptor

# Expected output:
{
    "agent_id": "sql_query_agent_001",
    "agent_type": "data",
    "capabilities": ["generate_query", "validate_query"]
}
```

### 2. Test Health Check

```bash
curl http://localhost:9022/health

# Expected output:
{
    "status": "healthy",
    "agent_id": "sql_query_agent_001"
}
```

### 3. Test Query Generation

```bash
curl -X POST http://localhost:9022/a2a/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "journey_id": "550e8400-e29b-41d4-a716-446655440001",
    "agent_id": "sql_query_agent_001",
    "action": "generate_query",
    "parameters": {
      "natural_language": "Show all users created in the last week",
      "platform": "sql"
    }
  }'
```

### 4. Integration Test with Core Engine

```python
import httpx

async def test_with_core_engine():
    """Test integration with core engine."""
    
    # Step 1: Submit query to core engine
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/query",
            json={
                "natural_language": "Show all users",
                "platform": "sql"
            }
        )
    
    assert response.status_code == 200
    result = response.json()
    
    # Step 2: Verify your agent was used
    assert "sql" in result["queries"]
    assert len(result["queries"]["sql"]) > 0
    
    # Step 3: Check cost tracking
    assert result["cost_summary"]["total_cost_usd"] > 0
```

---

## Examples

### Example 1: Basic SQL Agent

**`sql_agent/main.py`**:
```python
from fastapi import FastAPI
from datetime import datetime
import time
from uuid import UUID
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

# Models
class A2ATaskRequest(BaseModel):
    task_id: UUID
    journey_id: UUID
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    timeout_seconds: int = 60

class A2ATaskResponse(BaseModel):
    task_id: UUID
    journey_id: UUID
    agent_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float

# App
app = FastAPI(
    title="SQL Query Generator Agent",
    version="1.0.0"
)

AGENT_CONFIG = {
    "agent_id": "sql_query_agent_001",
    "agent_name": "SQL Query Generator",
    "agent_type": "data",
    "version": "1.0.0",
    "platform": "sql",
    "capabilities": ["generate_query"],
    "endpoint": "http://localhost:9022"
}

@app.get("/a2a/descriptor")
async def descriptor():
    return AGENT_CONFIG

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_id": AGENT_CONFIG["agent_id"]}

@app.post("/a2a/task")
async def process_task(request: A2ATaskRequest) -> A2ATaskResponse:
    start_time = time.time()
    
    try:
        if request.action == "generate_query":
            # Your NLQ logic here
            query = f"SELECT * FROM table WHERE condition='value'"
            
            result = {
                "query_result": {
                    "query": query,
                    "platform": "sql",
                    "confidence": 0.95,
                    "explanation": "Generated query from natural language"
                }
            }
        else:
            raise ValueError(f"Unknown action: {request.action}")
        
        elapsed_ms = (time.time() - start_time) * 1000
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=AGENT_CONFIG["agent_id"],
            status="success",
            result=result,
            execution_time_ms=elapsed_ms
        )
    
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return A2ATaskResponse(
            task_id=request.task_id,
            journey_id=request.journey_id,
            agent_id=AGENT_CONFIG["agent_id"],
            status="error",
            error_message=str(e),
            execution_time_ms=elapsed_ms
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9022)
```

### Example 2: KQL Agent with Templates

**`kql_agent/main.py`**:
```python
from fastapi import FastAPI

app = FastAPI(title="KQL Query Generator Agent", version="1.0.0")

TEMPLATES = {
    "failed_logins": "SigninLogs | where ResultType == 'Failure' | summarize Count=count() by UserPrincipalName",
    "user_activity": "AADUserRiskEvents | where TimeGenerated > ago({timerange})",
    "system_errors": "Event | where EventLevelName == 'Error' | summarize Count=count() by Source"
}

@app.get("/a2a/descriptor")
async def descriptor():
    return {
        "agent_id": "kql_query_agent_001",
        "agent_type": "data",
        "agent_name": "KQL Query Generator",
        "version": "1.0.0",
        "platform": "kql",
        "capabilities": ["generate_query", "use_templates"],
        "endpoint": "http://localhost:9020",
        "metadata": {
            "supports_templates": True,
            "template_count": len(TEMPLATES)
        }
    }

async def generate_query_from_nlq(natural_language: str) -> str:
    """
    Your NLQ-to-KQL logic here.
    For demo: check for keywords and use templates.
    """
    nl_lower = natural_language.lower()
    
    if "failed" in nl_lower and "login" in nl_lower:
        return TEMPLATES["failed_logins"]
    elif "activity" in nl_lower:
        return TEMPLATES["user_activity"]
    else:
        return f"let query = {{\"{natural_language}\"}}; query"
```

### Example 3: Multi-Platform Agent

**`universal_agent/main.py`**:
```python
@app.get("/a2a/descriptor")
async def descriptor():
    return {
        "agent_id": "universal_nlq_agent",
        "agent_type": "data",
        "agent_name": "Universal NLQ Agent",
        "version": "1.0.0",
        "platform": None,  # Multi-platform
        "capabilities": ["generate_query"],
        "endpoint": "http://localhost:9030",
        "metadata": {
            "supports_multi_platform": True,
            "supported_platforms": ["sql", "kql", "spl"]
        }
    }

async def handle_generate_query(request: A2ATaskRequest):
    params = request.parameters
    natural_language = params.get("natural_language")
    platform = params.get("platform", "sql")
    
    if platform == "sql":
        query = generate_sql(natural_language)
    elif platform == "kql":
        query = generate_kql(natural_language)
    elif platform == "spl":
        query = generate_spl(natural_language)
    else:
        raise ValueError(f"Unsupported platform: {platform}")
    
    return {"query_result": {"query": query, "platform": platform}}
```

---

## Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV AGENT_ID=sql_query_agent_001
ENV AGENT_TYPE=data
ENV PLATFORM=sql
ENV PROTOCOL_INTERFACE_URL=http://protocol-interface:8001

EXPOSE 9022

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD curl -f http://localhost:9022/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9022"]
```

### Docker Compose Integration

```yaml
version: "3.8"

services:
  sql-agent:
    build: ./sql_agent
    container_name: sql-agent
    ports:
      - "9022:9022"
    environment:
      AGENT_ID: sql_query_agent_001
      PLATFORM: sql
      PROTOCOL_INTERFACE_URL: http://protocol-interface:8001
    depends_on:
      - protocol-interface
    networks:
      - lexiquery-net

  kql-agent:
    build: ./kql_agent
    container_name: kql-agent
    ports:
      - "9020:9020"
    environment:
      AGENT_ID: kql_query_agent_001
      PLATFORM: kql
      PROTOCOL_INTERFACE_URL: http://protocol-interface:8001
    depends_on:
      - protocol-interface
    networks:
      - lexiquery-net

networks:
  lexiquery-net:
    driver: bridge
```

---

## Checklist

Before going live with your A2A integration:

- [ ] Agent descriptor endpoint returns correct metadata
- [ ] Health check endpoint is responsive
- [ ] Task endpoint correctly processes `generate_query` action
- [ ] UUID and datetime serialization handled (use `mode="json"`)
- [ ] Error responses follow A2A protocol
- [ ] Cost information tracked in responses
- [ ] Agent registers with Protocol Interface on startup
- [ ] Integration tested with Core Engine
- [ ] Logging/monitoring configured
- [ ] Docker image builds and runs
- [ ] Security: API rate limiting configured
- [ ] Documentation: README with setup instructions

---

## Troubleshooting

### Agent Not Discoverable

**Problem**: Core Engine can't find your agent

**Solution**:
1. Check `/a2a/descriptor` returns valid JSON
2. Verify `agent_type` is "data"
3. Check Protocol Interface can reach your endpoint
4. Verify registration endpoint was called

### UUID Serialization Errors

**Problem**: "Object of type UUID is not JSON serializable"

**Solution**:
```python
# In Pydantic models, use:
class Config:
    json_encoders = {
        UUID: str,
        datetime: lambda v: v.isoformat()
    }

# Or in model_dump() calls:
result = model.model_dump(mode="json")
```

### Timeout Errors

**Problem**: Tasks timing out when calling your service

**Solution**:
1. Increase `timeout_seconds` in task request
2. Optimize your NLQ service (add caching, batching)
3. Check network latency to Protocol Interface
4. Monitor your service for slow operations

### Wrong Query Generated

**Problem**: Your agent generates incorrect queries

**Solution**:
1. Add logging to your query generation logic
2. Validate schema_hints and knowledge_context
3. Test with Core Engine's test query suite
4. Implement `validate_query` action for self-validation

---

## Next Steps

1. **Implement basic A2A endpoints** on your existing service
2. **Register with Protocol Interface**
3. **Test with Core Engine** using sample queries
4. **Add monitoring and logging**
5. **Optimize for production** (caching, rate limiting)
6. **Document your agent** for other teams

---

## References

- [A2A Protocol Specification](../docs/A2A_PROTOCOL.md)
- [LexiQuery Architecture](../docs/architecture/system_architecture.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)

