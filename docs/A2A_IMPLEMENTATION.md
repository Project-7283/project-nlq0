# A2A Protocol Implementation Guide

**Implementation Date**: February 6, 2026  
**Status**: Production Ready  

This document describes the A2A (Agent-to-Agent) protocol implementation in the NLQ-to-SQL service, enabling it to operate within the LexiQuery ecosystem.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components Implemented](#components-implemented)
4. [Running the Service](#running-the-service)
5. [API Endpoints](#api-endpoints)
6. [Testing](#testing)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The NLQ-to-SQL service has been enhanced with A2A protocol support, enabling:

- **Agent Discovery**: Other agents can discover this service's capabilities
- **Task Processing**: Receive and process tasks from the Core Engine or other agents
- **Cost Tracking**: Track API calls and resource usage
- **Protocol Interface Integration**: Register with the LexiQuery Protocol Interface

### Agent Identity

```
Agent ID:        sql_query_agent_001
Agent Name:      SQL Query Generator Agent
Agent Type:      data
Platform:        sql
Version:         1.0.0
Capabilities:    generate_query, validate_query, explain_query
```

---

## Architecture

### Data Flow

```
Core Engine / Other Agent
    ↓
/a2a/task endpoint
    ↓
Task Handler (validate, route, execute)
    ↓
NLQ Processing Pipeline
    ↓
A2ATaskResponse (with result/error)
    ↓
Core Engine / Other Agent
```

### Service Components

#### 1. A2A Models (`src/models/a2a.py`)
- `A2ATaskRequest`: Incoming task specification
- `A2ATaskResponse`: Task result with status
- `AgentDescriptor`: Agent information for discovery
- `QueryGenerationResult`: Generated query output
- `ValidationResult`: Query validation output

#### 2. A2A Configuration (`src/config.py`)
- `AgentConfig`: Centralized configuration using Pydantic Settings
- Environment variable based configuration
- Easy integration with Docker and cloud platforms

#### 3. A2A Handlers (`src/handlers/a2a_handlers.py`)
- `handle_generate_query()`: Generate SQL from natural language
- `handle_validate_query()`: Validate SQL syntax and logic
- `handle_explain_query()`: Explain query purpose
- Proper error handling and cost tracking

#### 4. Agent Registration (`src/modules/agent_registration.py`)
- `register_with_retry()`: Register with Protocol Interface with retries
- `build_agent_descriptor()`: Construct agent metadata
- Graceful fallback if Protocol Interface unavailable

#### 5. FastAPI Integration (`src/api.py`)
- `/a2a/descriptor`: Agent discovery endpoint
- `/health`: Health check endpoint
- `/a2a/task`: Task processing endpoint
- Backward compatible with existing `/query` endpoint

---

## Components Implemented

### File Structure

```
src/
├── api.py                          # Updated with A2A endpoints
├── config.py                       # NEW: A2A configuration
├── models/
│   └── a2a.py                     # NEW: A2A protocol models
├── handlers/
│   └── a2a_handlers.py            # NEW: Task handlers
└── modules/
    └── agent_registration.py       # NEW: Registration logic

Root/
├── Dockerfile                      # NEW: Docker image with A2A
├── docker-compose.yml              # NEW: Docker Compose setup
└── protocol_interface_mock.py      # NEW: Mock Protocol Interface
```

### Models

#### A2ATaskRequest
```python
{
    "task_id": "UUID",
    "journey_id": "UUID",
    "agent_id": "requesting_agent_001",
    "action": "generate_query",
    "parameters": {
        "natural_language": "Show all active users",
        "platform": "sql",
        "schema_hints": {...}
    },
    "timeout_seconds": 60
}
```

#### A2ATaskResponse
```python
{
    "task_id": "UUID",
    "journey_id": "UUID",
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

## Running the Service

### Option 1: Local Development

#### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Create `.env` file
```bash
# A2A Configuration
AGENT_ID=sql_query_agent_001
AGENT_TYPE=data
PLATFORM=sql
PORT=9022
PROTOCOL_INTERFACE_URL=http://localhost:8001
AUTO_REGISTER=true

# Database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=nlq_database

# LLM
GEMINI_API_KEY=your_gemini_key
```

#### 3. Start the service
```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 9022 --reload
```

#### 4. Start Protocol Interface Mock (in another terminal)
```bash
python protocol_interface_mock.py
```

### Option 2: Docker Compose

#### 1. Build and run
```bash
docker-compose up --build
```

This starts:
- SQL Agent on port 9022
- MySQL on port 3306
- Protocol Interface Mock on port 8001

#### 2. Verify services are running
```bash
curl http://localhost:9022/health
curl http://localhost:8001/health
```

### Option 3: Production Deployment

#### 1. Build image
```bash
docker build -t nlq-sql-agent:1.0.0 .
```

#### 2. Run with proper environment
```bash
docker run -d \
  --name sql-agent \
  -p 9022:9022 \
  -e PROTOCOL_INTERFACE_URL=https://protocol-interface.prod.com \
  -e MYSQL_HOST=prod-mysql.internal \
  -e GEMINI_API_KEY=$GEMINI_KEY \
  nlq-sql-agent:1.0.0
```

---

## API Endpoints

### Agent Discovery

**Endpoint**: `GET /a2a/descriptor`

Get agent information for discovery by the Protocol Interface.

**Response** (200 OK):
```json
{
    "agent_id": "sql_query_agent_001",
    "agent_name": "SQL Query Generator Agent",
    "agent_type": "data",
    "version": "1.0.0",
    "endpoint": "http://localhost:9022",
    "platform": "sql",
    "capabilities": ["generate_query", "validate_query", "explain_query"],
    "metadata": {
        "knowledge_domain": "query_generation",
        "supports_templates": false,
        "supports_optimization": true,
        "max_complexity": "high"
    }
}
```

### Health Check

**Endpoint**: `GET /health`

Verify agent is running and healthy.

**Response** (200 OK):
```json
{
    "status": "healthy",
    "agent_id": "sql_query_agent_001",
    "version": "1.0.0",
    "uptime_seconds": 3600,
    "dependencies": {
        "nlq_service": "healthy",
        "database": "healthy"
    }
}
```

### Task Processing

**Endpoint**: `POST /a2a/task`

Process an A2A protocol task.

**Request**:
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "journey_id": "550e8400-e29b-41d4-a716-446655440001",
    "agent_id": "core_engine_001",
    "action": "generate_query",
    "parameters": {
        "natural_language": "Show all orders from last month",
        "platform": "sql"
    },
    "timeout_seconds": 60
}
```

**Response** (200 OK):
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "journey_id": "550e8400-e29b-41d4-a716-446655440001",
    "agent_id": "sql_query_agent_001",
    "status": "success",
    "result": {
        "query_result": {
            "query": "SELECT * FROM orders WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)",
            "platform": "sql",
            "confidence": 0.92,
            "explanation": "Retrieved orders from the last month",
            "tables_involved": ["orders"],
            "estimated_rows": 2500,
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

**Actions Supported**:

| Action | Description | Input Parameters |
|--------|-------------|------------------|
| `generate_query` | Generate SQL from natural language | `natural_language`, `platform` |
| `validate_query` | Validate SQL syntax | `query`, `platform` |
| `explain_query` | Explain what a query does | `query`, `platform` |

---

## Testing

### 1. Basic Health Check

```bash
curl -X GET http://localhost:9022/health
```

### 2. Discover Agent

```bash
curl -X GET http://localhost:9022/a2a/descriptor
```

### 3. Generate Query

```bash
curl -X POST http://localhost:9022/a2a/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "journey_id": "550e8400-e29b-41d4-a716-446655440001",
    "agent_id": "test_agent",
    "action": "generate_query",
    "parameters": {
      "natural_language": "Show all users",
      "platform": "sql"
    },
    "timeout_seconds": 60
  }'
```

### 4. Validate Query

```bash
curl -X POST http://localhost:9022/a2a/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "journey_id": "550e8400-e29b-41d4-a716-446655440001",
    "agent_id": "test_agent",
    "action": "validate_query",
    "parameters": {
      "query": "SELECT * FROM users WHERE id = 1",
      "platform": "sql"
    }
  }'
```

### 5. Protocol Interface Registration

```bash
# List registered agents
curl http://localhost:8001/a2a/agents

# Get agent details
curl http://localhost:8001/a2a/agents/sql_query_agent_001

# Get agents by platform
curl http://localhost:8001/a2a/agents/platform/sql
```

### 6. Python Integration Test

```python
import httpx
import uuid

async def test_a2a_integration():
    """Test A2A protocol integration."""
    
    # Test health check
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9022/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    # Test agent discovery
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:9022/a2a/descriptor")
        assert response.status_code == 200
        descriptor = response.json()
        assert descriptor["agent_id"] == "sql_query_agent_001"
        assert "generate_query" in descriptor["capabilities"]
    
    # Test query generation
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9022/a2a/task",
            json={
                "task_id": str(uuid.uuid4()),
                "journey_id": str(uuid.uuid4()),
                "agent_id": "test_agent",
                "action": "generate_query",
                "parameters": {
                    "natural_language": "Show all users",
                    "platform": "sql"
                }
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "query_result" in result["result"]
        assert "query" in result["result"]["query_result"]
```

---

## Configuration

### Environment Variables

#### A2A Protocol Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_ID` | `sql_query_agent_001` | Unique agent identifier |
| `AGENT_NAME` | `SQL Query Generator Agent` | Human-readable name |
| `AGENT_VERSION` | `1.0.0` | Agent version |
| `AGENT_TYPE` | `data` | Agent type (data/knowledge/planner) |
| `PLATFORM` | `sql` | Query platform (sql/kql/spl) |
| `PORT` | `9022` | Service port |
| `HOST` | `0.0.0.0` | Service host |
| `PROTOCOL_INTERFACE_URL` | `http://localhost:8001` | Protocol Interface address |
| `AUTO_REGISTER` | `true` | Auto-register on startup |

#### Database Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `MYSQL_HOST` | `localhost` | MySQL host |
| `MYSQL_PORT` | `3306` | MySQL port |
| `MYSQL_USER` | `root` | MySQL user |
| `MYSQL_PASSWORD` | `` | MySQL password |
| `MYSQL_DATABASE` | `nlq_database` | Database name |

#### LLM Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (unset) | Google Gemini API key |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama service URL |
| `OPENAI_API_KEY` | (unset) | OpenAI API key |

### `.env` File Example

```env
# A2A Protocol
AGENT_ID=sql_query_agent_001
AGENT_TYPE=data
PLATFORM=sql
PORT=9022
PROTOCOL_INTERFACE_URL=http://protocol-interface:8001
AUTO_REGISTER=true

# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=secure_password
MYSQL_DATABASE=nlq_database

# LLM
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=your_openai_api_key_here

# Logging
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Agent Not Registering

**Problem**: Agent fails to register with Protocol Interface

**Solution**:
1. Verify Protocol Interface is running: `curl http://localhost:8001/health`
2. Check agent logs: `docker logs sql-agent`
3. Verify network connectivity: `curl -v http://protocol-interface:8001/health`
4. Disable auto-registration temporarily: `AUTO_REGISTER=false`

### Query Generation Fails

**Problem**: Tasks return error status

**Solution**:
1. Check database connection: Verify `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`
2. Check logs: `docker logs sql-agent`
3. Verify natural language is non-empty
4. Test with simpler queries first

### UUID Serialization Error

**Problem**: "Object of type UUID is not JSON serializable"

**Solution**:
- Already handled in A2A models with `model_dump(mode="json")`
- Ensure using latest Pydantic v2 config

### Health Check Fails

**Problem**: `/health` endpoint returns error

**Solution**:
1. Service may be starting - wait 10 seconds
2. Check if database is accessible
3. Check logs for initialization errors
4. Verify all required dependencies are installed

### Protocol Interface Connection Timeout

**Problem**: "Could not connect to Protocol Interface"

**Solution**:
1. Verify Protocol Interface URL is correct
2. Check Docker network: `docker network ls`
3. For Docker Compose, use service name: `http://protocol-interface:8001`
4. For local testing, use: `http://localhost:8001`

---

## Integration with LexiQuery Core Engine

When fully integrated with the LexiQuery system:

1. **Discovery Phase**: Core Engine discovers this agent via `/a2a/descriptor`
2. **Task Submission**: Core Engine submits tasks to `/a2a/task`
3. **Cost Tracking**: Cost information is collected from responses
4. **Result Processing**: Results are formatted and returned to user
5. **Agent Monitoring**: Health checks verify agent availability

### Example Core Engine Integration

```python
import httpx

async def invoke_sql_agent(natural_language: str) -> str:
    """
    Invoke SQL agent through A2A protocol.
    """
    async with httpx.AsyncClient() as client:
        # Discover agent
        descriptor = await client.get(
            "http://sql-agent:9022/a2a/descriptor"
        )
        
        # Invoke task
        response = await client.post(
            "http://sql-agent:9022/a2a/task",
            json={
                "task_id": uuid.uuid4(),
                "journey_id": uuid.uuid4(),
                "agent_id": "core_engine",
                "action": "generate_query",
                "parameters": {
                    "natural_language": natural_language,
                    "platform": "sql"
                }
            }
        )
        
        result = response.json()
        if result["status"] == "success":
            return result["result"]["query_result"]["query"]
        else:
            raise Exception(result["error_message"])
```

---

## Next Steps

1. **Deploy to Staging**: Test with LexiQuery staging environment
2. **Monitor Performance**: Track response times and error rates
3. **Optimize**: Improve query generation accuracy and speed
4. **Add More Capabilities**: Implement additional query platforms (KQL, SPL)
5. **Enhance Cost Tracking**: Implement detailed usage metrics

---

## Support

For issues or questions:

1. Check logs: `docker logs sql-agent`
2. Review API documentation: `http://localhost:9022/docs`
3. Check Protocol Interface status: `http://localhost:8001/docs`
4. Review this guide's troubleshooting section
