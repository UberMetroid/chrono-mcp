# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /app

# Copy only installed packages
COPY --from=builder /install /usr/local

# Copy application
COPY lib/ ./lib/
COPY data/ ./data/
COPY docs/ ./docs/
COPY mcp/ ./mcp/
COPY web_ui.py ./

RUN touch /app/lib/__init__.py

ENV CHRONO_BASE=/app
ENV WEB_PORT=5000
ENV MCP_PORT=8080

# Labels
LABEL maintainer="Chrono MCP"
LABEL description="Crono MCP - Chrono ROM analysis tools"

EXPOSE 5000 8080

# Run web UI by default
CMD ["python", "web_ui.py"]
