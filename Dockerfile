# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

# Install curl for health checks (required for Docker format)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only installed packages
COPY --from=builder /install /usr/local

# Copy application
COPY lib/ ./lib/
COPY data/ ./data/
COPY docs/ ./docs/
COPY mcp/ ./mcp/
COPY web_ui.py ./
COPY start.sh ./

RUN touch /app/lib/__init__.py
RUN chmod +x /app/start.sh

ENV CHRONO_BASE=/app
ENV WEB_PORT=5000
ENV MCP_PORT=8080
ENV MCP_TRANSPORT=http

# Labels
LABEL maintainer="Chrono MCP"
LABEL description="Crono MCP - Chrono ROM analysis tools"
LABEL version="1.0.0"

# Resource limits should be set at runtime:
#   podman run --memory=512m --cpus=1.0 ...
# Or use docker-compose with resources limits

# Health checks
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000 8080

# Run both web UI and MCP server
CMD ["./start.sh"]
