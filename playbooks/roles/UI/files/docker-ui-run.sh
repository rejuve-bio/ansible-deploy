#!/bin/bash
set -e

# Stop and remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -Eq '^ui$'; then
    echo "Stopping and removing existing 'ui' container..."
    docker stop ui
    docker rm ui
fi

# Free port 3000 if any process is using it
if lsof -i :3000 > /dev/null; then
    echo "Port 3000 is in use. Killing the process..."
    sudo kill -9 $(lsof -t -i :3000)
fi

# Check if Docker image exists
if docker images -q ui:latest > /dev/null 2>&1 && [ -n "$(docker images -q ui:latest)" ]; then
    echo "Docker image 'ui:latest' already exists. Skipping build."
else
    # Build the Docker image if it does not exist
    echo "Building Docker image 'ui:latest'..."
    docker build -t ui:latest .
fi

# Run the container with bridge networking and port 3000
echo "Running Docker container 'ui'..."
docker run -d -p 3000:3000 --env-file ./.env --network="host" --name ui ui:latest