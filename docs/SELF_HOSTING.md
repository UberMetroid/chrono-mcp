# Self-Hosting Guide

## Crono MCP - Self-Hosted Deployment

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

**Note:** The MCP server uses the MCP protocol (streamable-http transport). Clients must use the MCP protocol to communicate with it. Direct HTTP requests without MCP client headers will receive a 406 response. Use an MCP-compatible client like Claude Desktop, Cursor, or other MCP clients.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHRONO_BASE` | `/app` | Base directory |
| `WEB_PORT` | `5000` | Web UI port |
| `MCP_PORT` | `8080` | MCP server port |
| `API_KEY` | (none) | Optional API key for authentication |

### Optional Authentication

To enable API authentication, set the `API_KEY` environment variable:

```bash
docker run -d -p 5000:5000 -e API_KEY=your-secret-key chrono-mcp
```

Then access the API with:
```bash
curl -H "Authorization: Bearer your-secret-key" http://localhost:5000/api/games
```

Health check and public endpoints remain accessible without authentication.

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
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
```

Or use `docker-compose.yml` in the repo for full configuration with healthchecks.

### Rate Limiting (Nginx)

Rate limiting is best handled at the reverse proxy level. Add to nginx.conf:

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
        }
    }
}
```

### Timeout Handling

Timeouts should be configured at the reverse proxy level:

```nginx
location / {
    proxy_pass http://chrono-mcp:5000;
    proxy_connect_timeout 30s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
}
```

### Connection Pooling

For high-traffic deployments, use a reverse proxy with connection pooling (nginx, haproxy, etc.). Flask's built-in server is single-threaded by default - use gunicorn for production:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_ui:app
```

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
