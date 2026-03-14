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

# Start MCP server in background
echo "Starting MCP server on port ${MCP_PORT:-8080}..."
cd /app/mcp/src
MCP_TRANSPORT=http python main.py > /tmp/mcp.log 2>&1 &
MCP_PID=$!

# Give MCP a moment to start
sleep 2

# Start web UI
echo "Starting web UI on port 5000..."
cd /app
python web_ui_refactored.py > /tmp/web.log 2>&1 &
WEB_PID=$!

echo "Both services started. MCP PID: $MCP_PID, Web PID: $WEB_PID"

# Wait for either to exit
wait $MCP_PID $WEB_PID
