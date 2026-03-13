# Self-Hosting Guide

## Chrono ROM Tools - Self-Hosted Deployment

### Quick Start

#### Option 1: Docker (Recommended)

```bash
# Pull from GitHub Container Registry (after first build)
docker pull ghcr.io/ubermetroid/chrono-mcp:latest

# Run web UI
docker run -d -p 5000:5000 ghcr.io/ubermetroid/chrono-mcp:latest

# Or run MCP server
docker run -d -p 8080:8080 ghcr.io/ubermetroid/chrono-mcp:latest python -c "import sys; sys.path.insert(0, '/app'); from lib.chrono import *; sys.path.insert(0, '/app/mcp'); from src import main; main.mcp.run(transport='streamable-http', host='0.0.0.0', port=8080)"
```

#### Option 2: Build Locally

```bash
# Clone and build
git clone https://github.com/UberMetroid/chrono-mcp.git
cd chrono-mcp

# Build image
docker build -t chrono-mcp .

# Run web UI
docker run -d -p 5000:5000 chrono-mcp
```

### Services

#### Web UI (Port 5000)
- Browse all game data
- Search across games
- View characters, items, locations
- Access extracted images/audio

**URL:** http://localhost:5000/

#### MCP Server (Port 8080)
- AI/LLM integration
- JSON-RPC protocol
- 60+ tools for data queries

**URL:** http://localhost:8080/mcp

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHRONO_BASE` | `/app` | Base directory |
| `WEB_PORT` | `5000` | Web UI port |
| `MCP_PORT` | `8080` | MCP server port |

### Docker Compose Example

```yaml
version: '3.8'

services:
  chronomcp:
    build: .
    ports:
      - "5000:5000"
      - "8080:8080"
    volumes:
      - ./data:/app/data:ro
    environment:
      - CHRONO_BASE=/app

  # Optional: Reverse proxy with HTTPS
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chrono-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chrono-mcp
  template:
    metadata:
      labels:
        app: chrono-mcp
    spec:
      containers:
      - name: chrono-mcp
        image: ghcr.io/ubermetroid/chrono-mcp:latest
        ports:
        - containerPort: 5000
        - containerPort: 8080
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Troubleshooting

#### Container won't start
```bash
# Check logs
docker logs chrono-mcp

# Verify data directory
docker exec chrono-mcp ls -la /app/data/
```

#### Port already in use
```bash
# Find what's using the port
lsof -i :5000
lsof -i :8080

# Change port mapping
docker run -d -p 5001:5000 chrono-mcp
```

#### Web UI not loading
```bash
# Check Flask is running
docker exec chrono-mcp ps aux

# Check network
docker exec chrono-mcp curl localhost:5000
```

### Security Notes

- No authentication by default
- Add reverse proxy (nginx, traefik) for production
- Use secrets for any sensitive data
- Keep image updated for security patches

### Updating

```bash
# Pull latest
docker pull ghcr.io/ubermetroid/chrono-mcp:latest

# Rebuild
docker build -t chrono-mcp .

# Restart
docker stop chrono-mcp && docker rm chrono-mcp
docker run -d -p 5000:5000 chrono-mcp
```
