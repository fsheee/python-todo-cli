# Phase 4 Docker Build

Dockerfiles and build scripts for creating Docker images from Phase 3 source code.

## Directory Structure

```
phase4-k8/docker/
├── backend-phase3.Dockerfile   # Backend (FastAPI, Python 3.11, port 8002)
├── frontend.Dockerfile         # Frontend (Next.js standalone, Node 20, port 80)
├── build.sh                    # Automated build script
└── README.md
```

## Quick Start

```bash
# From phase4-k8/ directory
./docker/build.sh

# Without Minikube
./docker/build.sh --no-minikube

# Custom tags
./docker/build.sh --backend-tag todo-chatbot-backend:v1.0.0 --frontend-tag todo-chatbot-frontend:v1.0.0
```

## Manual Build

```bash
# Backend (build context: phase3-chatbot/backend/)
docker build \
  -f phase4-k8/docker/backend-phase3.Dockerfile \
  -t todo-chatbot-backend:latest \
  phase3-chatbot/backend/

# Frontend (build context: phase3-chatbot/frontend/)
docker build \
  -f phase4-k8/docker/frontend.Dockerfile \
  -t todo-chatbot-frontend:latest \
  phase3-chatbot/frontend/
```

## Image Specs

| Image | Base | Port | Size (approx) | Health Check |
|-------|------|------|----------------|--------------|
| Backend | `python:3.11-slim` | 8002 | ~250MB | `curl http://localhost:8002/health` |
| Frontend | `node:20-alpine` | 80 | ~160MB | `node -e "http.get(...)"` |

Both images use multi-stage builds, non-root users, and production-optimized layers.

## Prerequisites

- Docker Desktop running
- Minikube running (if loading images)
- Phase 3 source code present at `../phase3-chatbot/`

## Verify

```bash
docker images | grep todo-chatbot
minikube image ls | grep todo-chatbot
```

## Deploy

```bash
cd phase4-k8
helm install todo-app helm/gordon -f secrets.yaml
kubectl get pods
```
