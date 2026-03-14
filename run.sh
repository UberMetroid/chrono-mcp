#!/bin/bash
# Helper script to run Chrono MCP with Podman and persistence

# Ensure storage directory exists
mkdir -p ./storage

# Stop existing container if it exists
podman stop chrono-mcp 2>/dev/null || true
podman rm chrono-mcp 2>/dev/null || true

# Run container with volume mount for persistence
# Note: Using :Z flag for SELinux context on the volume mount
podman run -d \
  --name chrono-mcp \
  --network host \
  -e DATABASE_URL="sqlite:////app/storage/chrono.db" \
  -e LOG_FILE="/app/storage/chrono.log" \
  -v "$(pwd)/storage:/app/storage:Z" \
  chrono-mcp:latest

echo "Container started with persistence."
echo "Web UI: http://localhost:5000"
echo "MCP API: http://localhost:8080"
