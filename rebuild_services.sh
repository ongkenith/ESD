#!/bin/bash

echo "Rebuilding modified services..."

# Navigate to the composite directory
cd composite

# Set environment variable for local mode
export DOCKER_MODE=false

# Build and start the condition-check service
echo "Rebuilding condition-check service..."
docker-compose build condition-check
docker-compose up -d condition-check

# Build and start the processing-order service
echo "Rebuilding processing-order service..."
docker-compose build processing-order
docker-compose up -d processing-order

echo "Services rebuilt and started."
echo "You can now run your tests with:"
echo "python run_complete_tests.py" 