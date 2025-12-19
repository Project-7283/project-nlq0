#!/bin/bash

# Main Project Initialization Script
# Orchestrates the complete setup by calling component scripts

set -e  # Exit on any error

echo "Starting project initialization..."

# Run component scripts
bash init/prepare_env.sh
bash init/setup_mysql.sh
bash init/setup_data.sh

echo "Project initialization complete!"
echo ""
echo "You can now run the application with: source venv/bin/activate && python src/main.py"