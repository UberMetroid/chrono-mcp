#!/bin/bash
# Start both web UI and MCP server with graceful shutdown

# Trap signals for graceful shutdown
cleanup() {
    echo "Shutting down gracefully..."
    if [ ! -z "$MCP_PID" ]; then
        kill -TERM $MCP_PID 2>/dev/null
    fi
    if [ ! -z "$WEB_PID" ]; then
        kill -TERM $WEB_PID 2>/dev/null
    fi
    wait
    echo "Shutdown complete"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Ensure directories exist
mkdir -p /tmp /app/data

# Start MCP server in background
echo "Starting MCP server on port ${MCP_PORT:-8080}..."
cd /app/mcp/src
MCP_TRANSPORT=http python main.py > /tmp/mcp.log 2>&1 &
MCP_PID=$!

# Give MCP a moment to start
sleep 2

# Start web UI (Using Gunicorn for production-grade performance and stability)
echo "Starting web UI on port 5000 using Gunicorn..."
cd /app

# Check if gunicorn is available, fallback to python if not
if command -v gunicorn &> /dev/null; then
    # We use sync workers with threads to handle SSE efficiently without complex async libraries
    gunicorn -w 2 --threads 4 -b 0.0.0.0:5000 --timeout 120 --access-logfile /tmp/web.log --error-logfile /tmp/web_error.log "app:create_app()" &
    WEB_PID=$!
else
    echo "Warning: Gunicorn not found, falling back to basic development server."
    python web_ui_refactored.py > /tmp/web.log 2>&1 &
    WEB_PID=$!
fi

echo "Both services started. MCP PID: $MCP_PID, Web PID: $WEB_PID"

# Wait for Web UI to exit (ignore MCP dying so web server can report it via the new SSE health stream)
wait $WEB_PID
