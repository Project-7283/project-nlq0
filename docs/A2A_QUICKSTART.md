# A2A Protocol Quick Start Guide

Get your NLQ-to-SQL service running as an A2A agent in 5 minutes.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, for containerized deployment)
- MySQL running locally or in Docker

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
cd j:\projects\project-nlq0
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 2. Create `.env` Configuration

Create a file named `.env` in the project root:

```env
# A2A Agent Configuration
AGENT_ID=sql_query_agent_001
AGENT_TYPE=data
PLATFORM=sql
PORT=9022
PROTOCOL_INTERFACE_URL=http://localhost:8001
AUTO_REGISTER=true

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=nlq_database

# LLM Configuration (choose one)
GEMINI_API_KEY=your_gemini_api_key
# OR
OLLAMA_URL=http://localhost:11434
# OR
OPENAI_API_KEY=your_openai_api_key
```

### 3. Start Protocol Interface Mock (Terminal 1)

```bash
python protocol_interface_mock.py
```

You should see:
```
Starting Protocol Interface Mock on http://0.0.0.0:8001
API Documentation available at http://localhost:8001/docs
```

### 4. Start the A2A Agent (Terminal 2)

```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 9022 --reload
```

You should see:
```
Uvicorn running on http://0.0.0.0:9022
```

### 5. Verify Services Are Running

In another terminal:

```bash
# Check agent health
curl http://localhost:9022/health

# Check agent descriptor
curl http://localhost:9022/a2a/descriptor

# Check protocol interface
curl http://localhost:8001/a2a/agents
```

## Quick Start (Docker Compose)

### 1. Build and Run

```bash
docker-compose up --build
```

This automatically starts:
- SQL Agent (port 9022)
- MySQL Database (port 3306)
- Protocol Interface Mock (port 8001)

### 2. Verify Services

```bash
curl http://localhost:9022/health
curl http://localhost:9022/a2a/descriptor
curl http://localhost:8001/health
```

## Test the Agent

### Test 1: Generate a Query

```bash
curl -X POST http://localhost:9022/a2a/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "journey_id": "550e8400-e29b-41d4-a716-446655440001",
    "agent_id": "test_agent",
    "action": "generate_query",
    "parameters": {
      "natural_language": "Show all users where status is active",
      "platform": "sql"
    },
    "timeout_seconds": 60
  }'
```

Expected Response:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "journey_id": "550e8400-e29b-41d4-a716-446655440001",
  "agent_id": "sql_query_agent_001",
  "status": "success",
  "result": {
    "query_result": {
      "query": "SELECT * FROM users WHERE status = 'active'",
      "platform": "sql",
      "confidence": 0.85,
      "explanation": "Generated sql query from natural language input",
      "tables_involved": ["users"],
      "estimated_rows": null,
      "parameters": [],
      "optimizations": ["indexed_search"]
    }
  },
  "execution_time_ms": 450.5,
  "cost_info": {
    "llm_calls": 1,
    "llm_tokens": 0,
    "execution_time_ms": 450.5
  }
}
```

### Test 2: Validate a Query

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

Expected Response:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "result": {
    "validation_result": {
      "is_valid": true,
      "errors": [],
      "warnings": ["SELECT * detected - specify columns for better performance"],
      "suggestions": ["Consider adding LIMIT to prevent excessive data retrieval"],
      "performance_estimate": "Unknown"
    }
  },
  "execution_time_ms": 45.2
}
```

### Test 3: Check Protocol Interface Registration

```bash
# View all registered agents
curl http://localhost:8001/a2a/agents

# View specific agent
curl http://localhost:8001/a2a/agents/sql_query_agent_001

# View agents by platform
curl http://localhost:8001/a2a/agents/platform/sql
```

## Key Features

✅ **Agent Discovery** - Other services can discover this agent  
✅ **Task Processing** - Process tasks from Core Engine  
✅ **Cost Tracking** - Track API calls and tokens  
✅ **Error Handling** - Graceful error responses  
✅ **Health Checks** - Built-in health monitoring  
✅ **Docker Ready** - Production-ready containerization  
✅ **Protocol Interface** - Automatic registration with orchestrator  

## API Documentation

Full API documentation available at:
- Agent API: http://localhost:9022/docs
- Protocol Interface Mock: http://localhost:8001/docs

## Configuration Reference

All configuration via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_ID` | `sql_query_agent_001` | Unique agent identifier |
| `AGENT_TYPE` | `data` | Agent type |
| `PLATFORM` | `sql` | Query platform |
| `PORT` | `9022` | Service port |
| `PROTOCOL_INTERFACE_URL` | `http://localhost:8001` | Protocol Interface URL |
| `AUTO_REGISTER` | `true` | Auto-register on startup |

## Troubleshooting

### Port Already in Use

If port 9022 is already in use:
```bash
# Change port via environment variable
set PORT=9023  # Windows
export PORT=9023  # macOS/Linux
```

### Database Connection Error

Make sure MySQL is running:
```bash
# Docker
docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8.0

# Or use docker-compose
docker-compose up mysql
```

### Agent Not Registering

Check protocol interface is running:
```bash
curl http://localhost:8001/health

# If not running, start it
python protocol_interface_mock.py
```

### Import Errors

Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Next Steps

1. **Explore Full Documentation**: Read [docs/A2A_IMPLEMENTATION.md](A2A_IMPLEMENTATION.md)
2. **Test Integration**: Try different query types
3. **Deploy to Cloud**: Use Docker image for production
4. **Monitor**: Check logs and metrics
5. **Integrate**: Connect to LexiQuery Core Engine

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/a2a/descriptor` | GET | Agent discovery |
| `/health` | GET | Health check |
| `/a2a/task` | POST | Process A2A task |
| `/query` | POST | Legacy endpoint (still supported) |
| `/docs` | GET | API documentation |
| `/openapi.json` | GET | OpenAPI schema |

## Support

For detailed help, see:
- Full Implementation Guide: [docs/A2A_IMPLEMENTATION.md](A2A_IMPLEMENTATION.md)
- Troubleshooting Section: [docs/A2A_IMPLEMENTATION.md#troubleshooting](A2A_IMPLEMENTATION.md#troubleshooting)
- Original A2A Guide: [A2A_INTEGRATION_GUIDE.md](../A2A_INTEGRATION_GUIDE.md)
