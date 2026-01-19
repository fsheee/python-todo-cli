# Backend Dockerfile for Phase 4 Kubernetes Deployment
# Phase 3 Chatbot Backend with AI Agents and MCP Tools
# Build context: ../../phase3-chatbot
# Usage: docker build -f phase4-k8/docker/backend-phase3.Dockerfile -t todo-chatbot-backend:latest phase3-chatbot

# Multi-stage build for Phase 3 FastAPI backend with AI chatbot
# Stage 1: Build stage
FROM python:3.13-slim AS builder

WORKDIR /build

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (Phase 3 structure)
# Note: Build context is phase3-chatbot/, so app/ is phase3-chatbot/app/
COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser mcp_server/ /app/mcp_server/
COPY --chown=appuser:appuser config/ /app/config/
COPY --chown=appuser:appuser .env.example /app/.env.example

# Create necessary directories
RUN mkdir -p /app/logs /app/data/chat-history && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8002 (Phase 3 chatbot API port)
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8002/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV API_HOST=0.0.0.0
ENV API_PORT=8002
ENV ENVIRONMENT=production

# Start the Phase 3 FastAPI chatbot application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]
