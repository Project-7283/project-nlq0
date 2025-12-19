#!/bin/bash

# Setup Data Script
# Generates additional datasets and semantic graph (schema and data loaded during MySQL startup)

set -e  # Exit on any error
export PYTHONPATH=./src:$PYTHONPATH

echo "Setting up additional data..."

# Generate semantic graph
echo "Generating semantic graph..."
python init/generate_graph_for_db.py

echo "Data setup complete!"