FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# A2A Protocol Configuration
ENV AGENT_ID=sql_query_agent_001
ENV AGENT_NAME="SQL Query Generator Agent"
ENV AGENT_VERSION=1.0.0
ENV AGENT_TYPE=data
ENV PLATFORM=sql
ENV PORT=9022
ENV HOST=0.0.0.0
ENV PROTOCOL_INTERFACE_URL=http://protocol-interface:8001
ENV AUTO_REGISTER=true

# Database Configuration
ENV MYSQL_HOST=mysql
ENV MYSQL_PORT=3306
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=
ENV MYSQL_DATABASE=nlq_database

# Expose port
EXPOSE 9022

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:9022/health', timeout=5)" || exit 1

# Run FastAPI app
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "9022", "--log-level", "info"]
