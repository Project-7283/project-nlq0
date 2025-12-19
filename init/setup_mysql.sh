#!/bin/bash

# Setup MySQL Service Script
# Starts MySQL Docker container and creates database user

set -e  # Exit on any error

# Configuration
MYSQL_ALLOW_EMPTY_PASSWORD=yes
MYSQL_USER="nlq_user"
MYSQL_PASSWORD="nlq_pass"
DB_NAME="ecommerce_marketplace"
CONTAINER_NAME="mysql-nlq"
MYSQL_PORT=3306

echo "Setting up MySQL service..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and run this script again."
    exit 1
fi

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping and removing existing MySQL container..."
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
fi

# Prepare initialization SQL files
echo "Preparing database initialization files..."
INIT_DIR="/tmp/mysql-init-${CONTAINER_NAME}"
mkdir -p ${INIT_DIR}

# Modify schema.sql to remove CREATE DATABASE (since Docker already created it)
sed '1,2d' tests/database/ecommerce_marketplace_schema.sql > ${INIT_DIR}/01_schema.sql

# Copy data file
cp tests/database/ecommerce_marketplace_data.sql ${INIT_DIR}/02_data.sql

# Copy user creation file
cp init/create_user.sql ${INIT_DIR}/03_create_user.sql

# Start MySQL container with volume mount for initialization
echo "Starting MySQL container with initialization files..."
docker run --name ${CONTAINER_NAME} \
    -e MYSQL_ALLOW_EMPTY_PASSWORD=${MYSQL_ALLOW_EMPTY_PASSWORD} \
    -e MYSQL_DATABASE=${DB_NAME} \
    -v ${INIT_DIR}:/docker-entrypoint-initdb.d \
    -p ${MYSQL_PORT}:3306 \
    -d mysql:latest

# Wait for MySQL to be ready (longer wait since init files need to run)
echo "Waiting for MySQL to be ready and initialization to complete..."
max_attempts=60  # Increased timeout for init files
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker exec ${CONTAINER_NAME} mysqladmin ping -u root --silent; then
        echo "MySQL is ready!"
        break
    fi
    echo "Attempt $attempt/$max_attempts: MySQL not ready yet..."
    sleep 3
    ((attempt++))
done

if [ $attempt -gt $max_attempts ]; then
    echo "Error: MySQL failed to start within expected time."
    exit 1
fi

echo "MySQL setup complete!"
echo ""
echo "Database connection details:"
echo "Host: localhost"
echo "Port: ${MYSQL_PORT}"
echo "Database: ${DB_NAME}"
echo "User: ${MYSQL_USER}"
echo "Password: ${MYSQL_PASSWORD}"


# Create .env file
echo "Creating .env file..."
MYSQL_USER="nlq_user"
MYSQL_PASSWORD="nlq_pass"
DB_NAME="ecommerce_marketplace"
cat > .env << EOF
MYSQL_HOST=localhost
MYSQL_USER=${MYSQL_USER}
MYSQL_PASSWORD=${MYSQL_PASSWORD}
MYSQL_DATABASE=${DB_NAME}
GEMINI_API_KEY=
OPENAI_API_KEY=
LLM_API_BASE=
LLM_MODEL=
LLM_EMBED_MODEL=
EOF
