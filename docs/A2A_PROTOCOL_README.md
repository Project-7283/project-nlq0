# A2A Protocol Integration - README

## Overview

Your NLQ-to-SQL service is now an **A2A (Agent-to-Agent) compatible service** that can integrate with the LexiQuery ecosystem and other agent-based systems.

## What's New

### ✅ Implemented Features

- **A2A Protocol Compliance**: Full support for A2A task protocol
- **Agent Discovery**: Services can discover your agent and its capabilities
- **Task Processing**: Handle tasks from Core Engine and other agents
- **Cost Tracking**: Automatic cost tracking for API calls
- **Health Monitoring**: Built-in health check endpoint
- **Auto-Registration**: Automatic registration with Protocol Interface
- **Docker Support**: Production-ready Docker configuration
- **Protocol Interface Mock**: Local testing without full LexiQuery system

### 📁 New Files & Directories

```
src/
├── config.py                          # A2A configuration management
├── models/
│   └── a2a.py                        # A2A protocol models & schemas
├── handlers/
│   └── a2a_handlers.py               # Task handlers
└── modules/
    └── agent_registration.py          # Protocol Interface integration

Root/
├── Dockerfile                         # Docker image
├── docker-compose.yml                 # Docker Compose setup
├── protocol_interface_mock.py         # Mock Protocol Interface
└── docs/
    ├── A2A_IMPLEMENTATION.md          # Full implementation guide
    ├── A2A_QUICKSTART.md              # Quick start guide
    └── A2A_PROTOCOL_README.md         # This file
```

### 🔄 Updated Files

- `src/api.py`: Added A2A endpoints while maintaining backward compatibility
- `requirements.txt`: Already includes pydantic-settings

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              LexiQuery Core Engine                       │
│  (or any other A2A-compatible orchestrator)              │
└────────────────────┬────────────────────────────────────┘
                     │ A2A Task Request
                     ▼
        ┌────────────────────────────┐
        │   Protocol Interface       │
        │  - Agent Discovery         │
        │  - Task Routing            │
        │  - Cost Tracking           │
        └────────────┬───────────────┘
                     │ Task Routing
                     ▼
    ┌────────────────────────────────────────┐
    │  SQL Query Agent (This Service)        │
    ├────────────────────────────────────────┤
    │ A2A Endpoints:                         │
    │  • GET /a2a/descriptor                │
    │  • GET /health                        │
    │  • POST /a2a/task                     │
    ├────────────────────────────────────────┤
    │ Task Handlers:                         │
    │  • generate_query                      │
    │  • validate_query                      │
    │  • explain_query                       │
    ├────────────────────────────────────────┤
    │ NLQ Processing:                        │
    │  • LLM Service (Gemini/Ollama/OpenAI) │
    │  • Vector DB (ChromaDB)                │
    │  • Database (MySQL)                    │
    └─────────────────────────────────────────┘
```

## Getting Started

### 🚀 Quick Start (5 minutes)

See [A2A_QUICKSTART.md](docs/A2A_QUICKSTART.md) for step-by-step instructions.

### 📖 Full Documentation

See [A2A_IMPLEMENTATION.md](docs/A2A_IMPLEMENTATION.md) for comprehensive documentation.

### 📋 Original A2A Guide

See [A2A_INTEGRATION_GUIDE.md](A2A_INTEGRATION_GUIDE.md) for the full A2A protocol specification.

## Running the Service

### Option 1: Local (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with configuration
cat > .env << EOF
AGENT_ID=sql_query_agent_001
PROTOCOL_INTERFACE_URL=http://localhost:8001
MYSQL_HOST=localhost
MYSQL_PASSWORD=your_password
EOF

# Terminal 1: Start Protocol Interface Mock
python protocol_interface_mock.py

# Terminal 2: Start the agent
python -m uvicorn src.api:app --port 9022
```

### Option 2: Docker (Production)

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build manually and run
docker build -t nlq-sql-agent:1.0.0 .
docker run -p 9022:9022 -e PROTOCOL_INTERFACE_URL=http://protocol-interface:8001 nlq-sql-agent:1.0.0
```

## API Endpoints

### A2A Protocol Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/a2a/descriptor` | GET | Agent discovery metadata | None |
| `/health` | GET | Health status check | None |
| `/a2a/task` | POST | Process A2A protocol task | None |

### Legacy Endpoints (Still Supported)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/query` | POST | Original NLQ endpoint |

### Documentation Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/docs` | GET | Interactive API documentation (Swagger) |
| `/openapi.json` | GET | OpenAPI schema |
| `/info` | GET | Agent information and configuration |

## Task Actions

Your agent supports the following task actions:

### 1. `generate_query` - Generate SQL from Natural Language

**Request**:
```python
{
    "action": "generate_query",
    "parameters": {
        "natural_language": "Show all active users",
        "platform": "sql"
    }
}
```

**Response**:
```python
{
    "status": "success",
    "result": {
        "query_result": {
            "query": "SELECT * FROM users WHERE status = 'active'",
            "platform": "sql",
            "confidence": 0.95,
            "explanation": "Retrieved active users",
            "tables_involved": ["users"]
        }
    }
}
```

### 2. `validate_query` - Validate SQL Query

**Request**:
```python
{
    "action": "validate_query",
    "parameters": {
        "query": "SELECT * FROM users",
        "platform": "sql"
    }
}
```

**Response**:
```python
{
    "status": "success",
    "result": {
        "validation_result": {
            "is_valid": true,
            "errors": [],
            "warnings": ["SELECT * - specify columns"],
            "suggestions": ["Add LIMIT clause"]
        }
    }
}
```

### 3. `explain_query` - Explain Query Purpose

**Request**:
```python
{
    "action": "explain_query",
    "parameters": {
        "query": "SELECT * FROM users WHERE created_at > NOW() - INTERVAL 7 DAY",
        "platform": "sql"
    }
}
```

**Response**:
```python
{
    "status": "success",
    "result": {
        "explanation": "Retrieves all users created in the last 7 days"
    }
}
```

## Configuration

### Environment Variables

All configuration is done via environment variables (see `.env`):

```env
# A2A Agent Configuration
AGENT_ID=sql_query_agent_001              # Unique identifier
AGENT_NAME=SQL Query Generator            # Display name
AGENT_TYPE=data                           # Type: data/knowledge/planner
PLATFORM=sql                              # Platform: sql/kql/spl
PORT=9022                                 # Service port
HOST=0.0.0.0                              # Service host
PROTOCOL_INTERFACE_URL=http://...        # Protocol Interface URL
AUTO_REGISTER=true                        # Auto-register on startup

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=nlq_database

# LLM Configuration
GEMINI_API_KEY=your_key
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=your_key
```

## Integration Examples

### Python Integration

```python
import httpx
import uuid

async def query_nlq_agent(natural_language: str) -> str:
    """Query the NLQ agent via A2A protocol."""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9022/a2a/task",
            json={
                "task_id": str(uuid.uuid4()),
                "journey_id": str(uuid.uuid4()),
                "agent_id": "my_agent",
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

# Use it
query = await query_nlq_agent("Show all orders from last month")
print(query)  # SELECT * FROM orders WHERE ...
```

### cURL Integration

```bash
# Generate query
curl -X POST http://localhost:9022/a2a/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "journey_id": "550e8400-e29b-41d4-a716-446655440001",
    "agent_id": "core_engine",
    "action": "generate_query",
    "parameters": {
      "natural_language": "Show all users",
      "platform": "sql"
    }
  }' | jq .
```

### JavaScript/Node.js Integration

```javascript
async function queryNLQAgent(naturalLanguage) {
    const response = await fetch('http://localhost:9022/a2a/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            task_id: crypto.randomUUID(),
            journey_id: crypto.randomUUID(),
            agent_id: 'my_agent',
            action: 'generate_query',
            parameters: {
                natural_language: naturalLanguage,
                platform: 'sql'
            }
        })
    });
    
    const result = await response.json();
    if (result.status === 'success') {
        return result.result.query_result.query;
    } else {
        throw new Error(result.error_message);
    }
}

// Use it
const query = await queryNLQAgent('Show all active customers');
console.log(query);
```

## Testing

### Health Check

```bash
curl http://localhost:9022/health
```

### Agent Discovery

```bash
curl http://localhost:9022/a2a/descriptor
```

### Run a Task

```bash
curl -X POST http://localhost:9022/a2a/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test-uuid",
    "journey_id": "test-uuid",
    "agent_id": "test_agent",
    "action": "generate_query",
    "parameters": {"natural_language": "Show all users", "platform": "sql"}
  }'
```

### Check Protocol Interface

```bash
# List all agents
curl http://localhost:8001/a2a/agents

# Get specific agent
curl http://localhost:8001/a2a/agents/sql_query_agent_001

# Get agents by platform
curl http://localhost:8001/a2a/agents/platform/sql
```

## Cost Tracking

Each task response includes cost information:

```json
{
  "cost_info": {
    "llm_calls": 1,
    "llm_tokens": 450,
    "execution_time_ms": 450.5
  }
}
```

This enables the orchestrator to:
- Track cumulative costs across agents
- Implement cost-based routing
- Generate billing reports
- Optimize expensive operations

## Monitoring & Logging

### Logs

The service logs all important events to console and optional file:

```
[2024-02-06 10:30:45] INFO - Starting A2A Agent: sql_query_agent_001 v1.0.0
[2024-02-06 10:30:46] INFO - Agent successfully registered with Protocol Interface
[2024-02-06 10:30:50] INFO - [A2A Task abc123] Received action: generate_query
[2024-02-06 10:30:52] INFO - [A2A Task abc123] Query generated successfully in 450.5ms
```

### Health Monitoring

Use the `/health` endpoint for health checks:

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 9022
  initialDelaySeconds: 10
  periodSeconds: 30

# Docker health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:9022/health || exit 1
```

## Deployment

### Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` file with configuration
3. Run: `python -m uvicorn src.api:app --port 9022`

### Docker

```bash
docker build -t nlq-sql-agent:1.0.0 .
docker run -p 9022:9022 nlq-sql-agent:1.0.0
```

### Docker Compose

```bash
docker-compose up --build
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sql-query-agent
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: agent
        image: nlq-sql-agent:1.0.0
        ports:
        - containerPort: 9022
        env:
        - name: PROTOCOL_INTERFACE_URL
          value: "http://protocol-interface:8001"
        livenessProbe:
          httpGet:
            path: /health
            port: 9022
          initialDelaySeconds: 10
          periodSeconds: 30
```

## Troubleshooting

### Common Issues

See [docs/A2A_IMPLEMENTATION.md#troubleshooting](docs/A2A_IMPLEMENTATION.md#troubleshooting) for detailed troubleshooting guide.

### Quick Diagnostics

```bash
# Check service is running
curl http://localhost:9022/health

# Check agent is discoverable
curl http://localhost:9022/a2a/descriptor

# Check registration with Protocol Interface
curl http://localhost:8001/a2a/agents/sql_query_agent_001

# Check logs (Docker)
docker logs sql-agent
docker logs protocol-interface
```

## Performance Considerations

- **Response Times**: Typical response: 400-800ms (depends on LLM)
- **Concurrency**: Supports concurrent requests (limited by thread pool)
- **Memory**: ~500MB base + buffers for concurrent requests
- **Database**: Requires MySQL connection

## Security

### Current Implementation

- No authentication on A2A endpoints (assumes internal network)
- CORS allows all origins (suitable for development)

### Production Recommendations

1. **Authentication**: Implement API key or JWT authentication
2. **CORS**: Restrict to known hosts
3. **Rate Limiting**: Implement per-agent rate limiting
4. **Network**: Use service mesh (Istio) or network policies
5. **TLS**: Enable HTTPS for Protocol Interface communication
6. **Secrets**: Use managed secrets (K8s secrets, Vault)

## Roadmap

- [ ] Support for KQL (Kusto Query Language)
- [ ] Support for SPL (Splunk Processing Language)
- [ ] Multi-platform agent (sql + kql + spl)
- [ ] Query optimization recommendations
- [ ] Cost estimation before execution
- [ ] Interactive query refinement
- [ ] A/B testing for query generation
- [ ] Performance profiling endpoint

## Support & Documentation

### Documentation Files

- **Quick Start**: [docs/A2A_QUICKSTART.md](docs/A2A_QUICKSTART.md) - Get running in 5 minutes
- **Implementation Guide**: [docs/A2A_IMPLEMENTATION.md](docs/A2A_IMPLEMENTATION.md) - Full details
- **A2A Specification**: [A2A_INTEGRATION_GUIDE.md](A2A_INTEGRATION_GUIDE.md) - Protocol specification

### API Documentation

- Agent API: http://localhost:9022/docs
- Protocol Interface: http://localhost:8001/docs

## License

Same as parent project.

## Questions?

Refer to:
1. This README
2. Quick Start Guide: docs/A2A_QUICKSTART.md
3. Implementation Guide: docs/A2A_IMPLEMENTATION.md
4. Original A2A Guide: A2A_INTEGRATION_GUIDE.md
