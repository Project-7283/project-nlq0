# A2A Deployment Checklist

Use this checklist to ensure your A2A service is properly deployed and ready for production use.

## Pre-Deployment

### Code Review
- [ ] All new files created correctly
  - [ ] `src/config.py` exists
  - [ ] `src/models/a2a.py` exists
  - [ ] `src/handlers/a2a_handlers.py` exists
  - [ ] `src/modules/agent_registration.py` exists
  - [ ] `Dockerfile` exists
  - [ ] `docker-compose.yml` exists
  - [ ] `protocol_interface_mock.py` exists

- [ ] `src/api.py` updated with A2A endpoints
- [ ] No syntax errors in Python files
- [ ] All imports resolvable

### Dependencies
- [ ] `requirements.txt` contains all needed packages
  - [ ] `fastapi`
  - [ ] `uvicorn`
  - [ ] `pydantic` (v2+)
  - [ ] `pydantic-settings`
  - [ ] `httpx` (for registration)
  - [ ] All existing dependencies preserved

## Development Testing

### Local Setup
- [ ] Python 3.11+ installed
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with required variables

### Service Testing
- [ ] Protocol Interface Mock starts: `python protocol_interface_mock.py`
  - [ ] Available at `http://localhost:8001`
  - [ ] Health check: `curl http://localhost:8001/health` returns 200

- [ ] Agent service starts: `python -m uvicorn src.api:app --port 9022`
  - [ ] Available at `http://localhost:9022`
  - [ ] Health check: `curl http://localhost:9022/health` returns 200
  - [ ] No Python errors in startup

### Endpoint Testing
- [ ] `/a2a/descriptor` returns agent metadata
- [ ] `/health` returns health status
- [ ] `/a2a/task` accepts POST requests
- [ ] `/docs` shows API documentation
- [ ] `/query` still works (legacy endpoint)

### Task Testing
- [ ] `generate_query` action works
  - [ ] Request accepted with natural_language parameter
  - [ ] Response has query in result
  - [ ] Execution time tracked
  - [ ] Cost info included

- [ ] `validate_query` action works
  - [ ] Request accepted with query parameter
  - [ ] Response shows validation results
  - [ ] Errors/warnings/suggestions provided

- [ ] `explain_query` action works
  - [ ] Request accepted with query parameter
  - [ ] Response contains explanation

### Protocol Interface Integration
- [ ] Agent auto-registers on startup
- [ ] Agent appears in: `curl http://localhost:8001/a2a/agents`
- [ ] Agent deregisters on shutdown

## Docker Testing

### Build & Run
- [ ] Docker image builds: `docker build -t nlq-sql-agent:1.0.0 .`
- [ ] No build errors
- [ ] Image size reasonable (~1-2GB)

- [ ] Docker container runs: `docker run -p 9022:9022 nlq-sql-agent:1.0.0`
- [ ] Container starts without errors
- [ ] Health check passes

### Docker Compose
- [ ] Compose file is valid: `docker-compose config`
- [ ] All services start: `docker-compose up --build`
  - [ ] sql-agent service running
  - [ ] mysql service running
  - [ ] protocol-interface service running
- [ ] Inter-service networking works
  - [ ] Agent can reach mysql
  - [ ] Agent can reach protocol-interface

## Configuration Testing

### Environment Variables
- [ ] `AGENT_ID` properly set
- [ ] `AGENT_TYPE` is "data"
- [ ] `PLATFORM` is "sql"
- [ ] `PORT` correctly configured
- [ ] `PROTOCOL_INTERFACE_URL` correctly set
- [ ] `AUTO_REGISTER` set to true

### Database Configuration
- [ ] `MYSQL_HOST` correct
- [ ] `MYSQL_PORT` correct
- [ ] `MYSQL_USER` correct
- [ ] `MYSQL_PASSWORD` correct
- [ ] `MYSQL_DATABASE` exists

### LLM Configuration
- [ ] At least one LLM provider configured
  - [ ] `GEMINI_API_KEY` valid, OR
  - [ ] `OLLAMA_URL` reachable, OR
  - [ ] `OPENAI_API_KEY` valid

## Load Testing

### Concurrent Requests
- [ ] Can handle 10 concurrent requests
- [ ] Can handle 50 concurrent requests
- [ ] Response times reasonable (< 5 seconds)
- [ ] No memory leaks over time

### Long-Running
- [ ] Service runs for 1 hour without issues
- [ ] No gradual memory growth
- [ ] No connection pooling issues

## Monitoring & Observability

### Logging
- [ ] Logs are written to stdout/stderr
- [ ] Log level appropriate (INFO for production)
- [ ] No excessive logging that impacts performance
- [ ] Error logs captured with stack traces

### Health Checks
- [ ] Health endpoint responsive
- [ ] Health endpoint checks dependencies
- [ ] Health status correctly reflects service state

### Metrics
- [ ] Response times tracked
- [ ] Error rates tracked
- [ ] Cost metrics included in responses
- [ ] Agent startup time tracked

## Security Checks

### Input Validation
- [ ] A2A task requests validated
- [ ] UUID fields properly validated
- [ ] String parameters sanitized
- [ ] No SQL injection risks from NLQ input

### Error Handling
- [ ] Error responses don't leak sensitive info
- [ ] Stack traces not exposed in API responses
- [ ] Database errors handled gracefully

### Network
- [ ] CORS configured appropriately
- [ ] No hardcoded credentials in code
- [ ] Secrets from environment variables only

## Documentation

### User Documentation
- [ ] README updated or created
- [ ] Quick start guide created
- [ ] Implementation guide created
- [ ] Configuration guide complete
- [ ] Troubleshooting section provided

### API Documentation
- [ ] Swagger UI available at `/docs`
- [ ] All endpoints documented
- [ ] Request/response examples provided
- [ ] Error codes documented

### Deployment Documentation
- [ ] Docker instructions provided
- [ ] Docker Compose instructions provided
- [ ] Environment variable documentation complete
- [ ] Configuration examples provided

## Production Deployment

### Pre-Production
- [ ] All tests passing
- [ ] Load testing completed
- [ ] Security review completed
- [ ] Performance benchmarks acceptable

### Staging Deployment
- [ ] Deploy to staging environment
- [ ] Connect to staging Protocol Interface
- [ ] Connect to staging database
- [ ] Run smoke tests
- [ ] Monitor for 24 hours

### Production Deployment
- [ ] Backup existing system (if applicable)
- [ ] Deploy to production
- [ ] Connect to production Protocol Interface
- [ ] Monitor closely for first hour
- [ ] Verify agent registered and discoverable
- [ ] Test critical workflows end-to-end
- [ ] Monitor error rates and response times

### Post-Deployment
- [ ] Agent properly registered in Protocol Interface
- [ ] Agent discoverable by other services
- [ ] Sample queries processed successfully
- [ ] Cost tracking working correctly
- [ ] Logs monitoring configured
- [ ] Alerts configured for errors/timeouts

## Rollback Plan

In case of issues:

- [ ] Previous version ready to restore
- [ ] Rollback procedure documented
- [ ] Quick rollback possible (< 5 minutes)
- [ ] Communication plan if issues occur

## Sign-Off

- [ ] Code review completed
  - Reviewer: _________________ Date: _______
  
- [ ] QA testing completed
  - Tester: _________________ Date: _______
  
- [ ] Product owner approval
  - Approver: _________________ Date: _______
  
- [ ] Deployment authorized
  - Authorizer: _________________ Date: _______

## Notes

```
[Space for deployment notes, issues, workarounds, etc.]
```

---

## Post-Deployment Verification

After deployment, verify these items within first 24 hours:

- [ ] Agent running and healthy
- [ ] Agent registered with Protocol Interface
- [ ] Sample queries execute successfully
- [ ] No error spikes in logs
- [ ] Response times acceptable
- [ ] Database connections stable
- [ ] Memory usage stable
- [ ] CPU usage acceptable
- [ ] Network connectivity reliable
- [ ] All dependencies healthy

---

## Troubleshooting Reference

If issues occur, refer to:
1. Logs: `docker logs sql-agent` or application logs
2. Health check: `curl http://localhost:9022/health`
3. API docs: http://localhost:9022/docs
4. Documentation: `docs/A2A_IMPLEMENTATION.md#troubleshooting`

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Environment**: _______________  
**Version**: _______________
