# Backend Dockerfile for Phase 4 Kubernetes Deployment
# Phase 3 Chatbot Backend with AI Agents and MCP Tools
# Build context: ../../phase3-chatbot/backend
# Usage: docker build -f phase4-k8/docker/backend-phase3.Dockerfile -t todo-chatbot-backend:latest phase3-chatbot/backend

# ---- Build stage: compile dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /install /usr/local

COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser mcp_server/ /app/mcp_server/
COPY --chown=appuser:appuser config/ /app/config/

RUN mkdir -p /app/logs /app/data && chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    API_HOST=0.0.0.0 \
    API_PORT=8002 \
    ENVIRONMENT=production

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
