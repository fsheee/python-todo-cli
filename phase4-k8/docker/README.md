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

## Current Status

✅ **Images built and deployed to Kubernetes (gordon namespace)**

| Image | Tag | Status |
|-------|-----|--------|
| todo-chatbot-backend | v18 | ✅ Running |
| todo-chatbot-frontend | v10 | ✅ Running |

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
# Check local Docker images
docker images | grep todo-chatbot

# Check images in Minikube
minikube image ls | grep todo-chatbot

# Check running pods
kubectl get pods -n gordon
```

## Deploy

```bash
# Using existing Helm release (gordon namespace)
kubectl get pods -n gordon

# Or reinstall
cd phase4-k8
helm upgrade gordon helm/gordon -n gordon
```

## Kubernetes Deployment

The app is deployed in the **gordon** namespace with:

- **Backend**: Service `gordon-todo-chatbot-backend:8002`
- **Frontend**: Service `gordon-todo-chatbot-frontend:80`
- **Database**: External Neon PostgreSQL (serverless)

### Access via Port Forward

```bash
# Backend
kubectl port-forward -n gordon svc/gordon-todo-chatbot-backend 8002:8002 &

# Frontend
kubectl port-forward -n gordon svc/gordon-todo-chatbot-frontend 8080:80 &
```

Then access:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8002/health
- API Docs: http://localhost:8002/docs

---

**Last Updated**: 2026-05-01