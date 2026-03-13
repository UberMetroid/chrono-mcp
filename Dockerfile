FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lib/ ./lib/
COPY data/ ./data/
COPY docs/ ./docs/
COPY mcp/ ./mcp/

RUN touch /app/lib/__init__.py

ENV CHRONO_BASE=/app
ENV MCP_TRANSPORT=http
ENV MCP_PORT=8080

EXPOSE 8080

CMD ["python", "-c", "import sys; sys.path.insert(0, '/app'); from lib.chrono import *; sys.path.insert(0, '/app/mcp'); from src import main; main.mcp.run(transport='streamable-http', host='0.0.0.0', port=8080)"]
