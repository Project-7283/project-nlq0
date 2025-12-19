#!/bin/bash

# Project Initialization Script
# This script sets up the NLQ project environment including Python dependencies and MySQL database

set -e  # Exit on any error

# Configuration
MYSQL_ALLOW_EMPTY_PASSWORD=yes
MYSQL_USER="nlq_user"
MYSQL_PASSWORD="nlq_pass"
DB_NAME="ecommerce_marketplace"
CONTAINER_NAME="mysql-nlq"
MYSQL_PORT=3306

echo "Starting project initialization..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

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

# Start MySQL container
echo "Starting MySQL container..."
docker run --name ${CONTAINER_NAME} \
    -e MYSQL_ALLOW_EMPTY_PASSWORD=${MYSQL_ALLOW_EMPTY_PASSWORD} \
    -e MYSQL_DATABASE=${DB_NAME} \
    -p ${MYSQL_PORT}:3306 \
    -d mysql:8.0

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker exec ${CONTAINER_NAME} mysqladmin ping -u root --silent; then
        echo "MySQL is ready!"
        break
    fi
    echo "Attempt $attempt/$max_attempts: MySQL not ready yet..."
    sleep 2
    ((attempt++))
done

if [ $attempt -gt $max_attempts ]; then
    echo "Error: MySQL failed to start within expected time."
    exit 1
fi

# Create SQL script to create database user
echo "Creating database user setup script..."
cat > create_user.sql << EOF
-- Create database if not exists
CREATE DATABASE IF NOT EXISTS ${DB_NAME};

-- Create user with native password authentication
CREATE USER '${MYSQL_USER}'@'%' IDENTIFIED WITH mysql_native_password BY '${MYSQL_PASSWORD}';

-- Grant DBA-level privileges on the database
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${MYSQL_USER}'@'%' WITH GRANT OPTION;

-- Flush privileges
FLUSH PRIVILEGES;
EOF

# Execute the SQL script using root account
echo "Executing user creation script..."
docker exec -i ${CONTAINER_NAME} mysql -u root < create_user.sql

# Clean up
rm create_user.sql

# Set up database schema and data
echo "Setting up database schema..."
# Modify schema.sql to remove CREATE DATABASE (since Docker already created it)
sed '1,2d' tests/database/ecommerce_marketplace_schema.sql > temp_schema.sql  # Remove CREATE DATABASE and USE lines
docker exec -i ${CONTAINER_NAME} mysql -u root ${DB_NAME} < temp_schema.sql
rm temp_schema.sql

echo "Inserting sample data..."
docker exec -i ${CONTAINER_NAME} mysql -u root ${DB_NAME} < tests/database/ecommerce_marketplace_data.sql

# Generate enterprise dataset
echo "Generating enterprise dataset..."
python generate_data.py

# Generate semantic graph
echo "Generating semantic graph..."
python generate_graph_for_db.py

# Create .env file
echo "Creating .env file..."
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

echo "Project initialization complete!"
echo ""
echo "Database connection details:"
echo "Host: localhost"
echo "Port: ${MYSQL_PORT}"
echo "Database: ${DB_NAME}"
echo "User: ${MYSQL_USER}"
echo "Password: ${MYSQL_PASSWORD}"
echo ""
echo "You can now run the application with: source venv/bin/activate && python src/main.py"
# End of script