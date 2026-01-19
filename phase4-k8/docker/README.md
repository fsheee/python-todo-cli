# Phase 4 Docker Build

This directory contains Dockerfiles and build scripts for creating Docker images from Phase 3 source code without modifying Phase 3 directories.

## Overview

**Strategy:** Build Context Approach
- Dockerfiles are located in `phase4-k8/docker/`
- Build context points to Phase 3 source directories
- Phase 3 code remains **completely untouched**

## Directory Structure

```
phase4-k8/docker/
├── backend.Dockerfile      # Backend Dockerfile
├── frontend.Dockerfile     # Frontend Dockerfile
├── build.sh                # Automated build script
└── README.md               # This file
```

## Quick Start

### Build Both Images

```bash
cd phase4-k8/docker
./build.sh
```

This will:
1. Build backend image: `todo-chatbot-backend:latest`
2. Build frontend image: `todo-chatbot-frontend:latest`
3. Load both images into Minikube
4. Generate build logs and status report

### Build Without Loading to Minikube

```bash
./build.sh --no-minikube
```

### Build with Custom Tags

```bash
./build.sh \
  --backend-tag todo-chatbot-backend:v1.0.0 \
  --frontend-tag todo-chatbot-frontend:v1.0.0
```

## Manual Build Commands

### Backend Image

```bash
docker build \
  -f phase4-k8/docker/backend.Dockerfile \
  -t todo-chatbot-backend:latest \
  phase3-chatbot/
```

**Build Context:** `phase3-chatbot/` (Phase 3 backend root)
**Dockerfile:** `phase4-k8/docker/backend.Dockerfile`

### Frontend Image

```bash
docker build \
  -f phase4-k8/docker/frontend.Dockerfile \
  -t todo-chatbot-frontend:latest \
  phase3-chatbot/frontend/
```

**Build Context:** `phase3-chatbot/frontend/` (Phase 3 frontend directory)
**Dockerfile:** `phase4-k8/docker/frontend.Dockerfile`

## Prerequisites

### System Requirements
- Docker Desktop installed and running
- Minikube running (if loading images)
- Bash shell (Git Bash on Windows)
- Minimum 2GB free disk space

### Verify Prerequisites

```bash
# Check Docker
docker --version
# Expected: Docker version 20.10+

# Check Minikube (optional)
minikube status
# Expected: Running

# Check Phase 3 code
ls ../phase3-chatbot/
ls ../phase3-chatbot/frontend/
```

## Build Script Options

```bash
./build.sh [OPTIONS]

Options:
  --backend-tag TAG       Backend image tag (default: todo-chatbot-backend:latest)
  --frontend-tag TAG      Frontend image tag (default: todo-chatbot-frontend:latest)
  --no-minikube           Don't load images into Minikube
  --help                  Show help message
```

## Output Files

### Logs Directory

After build, logs are saved to `phase4-k8/logs/`:

```
logs/
├── backend-build.log       # Backend Docker build output
├── frontend-build.log      # Frontend Docker build output
└── build-status.json       # Build summary (JSON)
```

### Prompt History Record (PHR)

Each build creates a PHR in `phase4-k8/history/prompts/`:

**Format:** `docker-build-YYYY-MM-DD-HH-MM-SS.md`

Contains:
- Build timestamp
- Image tags and sizes
- Build times
- Success/failure status
- Next steps
- Troubleshooting info (if failures)

## Verification

### Check Images in Docker

```bash
# List all images
docker images | grep todo-chatbot

# Expected output:
# todo-chatbot-backend    latest    abc123...   2 minutes ago   342MB
# todo-chatbot-frontend   latest    def456...   1 minute ago    156MB
```

### Check Images in Minikube

```bash
minikube image ls | grep todo-chatbot

# Expected output:
# docker.io/library/todo-chatbot-backend:latest
# docker.io/library/todo-chatbot-frontend:latest
```

### Inspect Image

```bash
# View image details
docker inspect todo-chatbot-backend:latest

# View image layers
docker history todo-chatbot-backend:latest
```

## Troubleshooting

### Build Fails with "No such file or directory"

**Cause:** Build context path is incorrect

**Solution:**
```bash
# Verify you're in the correct directory
cd phase4-k8/docker

# Verify Phase 3 exists
ls ../../phase3-chatbot/
```

### "Cannot connect to Docker daemon"

**Cause:** Docker Desktop not running

**Solution:**
1. Start Docker Desktop
2. Wait for it to fully start
3. Verify: `docker ps`

### "Minikube not running"

**Cause:** Minikube is not started

**Solution:**
```bash
# Start Minikube
minikube start --driver=docker

# Verify
minikube status
```

### Build Succeeds but Image Not in Minikube

**Cause:** Minikube load step failed

**Solution:**
```bash
# Manually load images
minikube image load todo-chatbot-backend:latest
minikube image load todo-chatbot-frontend:latest

# Verify
minikube image ls | grep todo-chatbot
```

### Out of Disk Space

**Cause:** Docker images consuming too much space

**Solution:**
```bash
# Remove unused images
docker system prune -a

# Remove old todo-chatbot images
docker rmi $(docker images 'todo-chatbot-*' -q)
```

### Frontend Build Fails with "standalone not found"

**Cause:** Next.js standalone mode not configured

**Solution:** The Dockerfile handles this automatically by modifying `next.config.js` during build. No manual action needed.

### Backend Build Fails with "requirements.txt not found"

**Cause:** Phase 3 backend structure issue

**Solution:**
```bash
# Verify requirements.txt exists
ls ../phase3-chatbot/requirements.txt

# If missing, Phase 3 setup is incomplete
cd ../phase3-chatbot
# Follow Phase 3 setup instructions
```

## Image Specifications

### Backend Image

**Base:** `python:3.13-slim`
**Size:** ~340MB
**Port:** 8001
**Health Check:** `curl http://localhost:8001/health`

**Layers:**
1. Python 3.13 slim base
2. System dependencies (gcc, postgresql-client)
3. Python packages from requirements.txt
4. Application code from Phase 3
5. Non-root user (appuser)

**Environment Variables:**
- `PYTHONUNBUFFERED=1`
- `API_HOST=0.0.0.0`
- `API_PORT=8001`

### Frontend Image

**Base:** `node:20-alpine`
**Size:** ~160MB
**Port:** 80
**Health Check:** `node -e "require('http').get('http://localhost:80/', ...)"`

**Layers:**
1. Node 20 Alpine base
2. Dependencies from package.json
3. Next.js build (standalone mode)
4. Non-root user (nextjs)

**Environment Variables:**
- `NODE_ENV=production`
- `PORT=80`
- `HOSTNAME=0.0.0.0`

## Multi-Stage Build Benefits

Both Dockerfiles use multi-stage builds:

**Advantages:**
- ✅ Smaller final image size
- ✅ Faster builds (cached layers)
- ✅ Separate build and runtime dependencies
- ✅ More secure (no build tools in production)

**Example:**
```dockerfile
# Stage 1: Build (includes gcc, npm, etc.)
FROM python:3.13-slim AS builder
# ... install all dependencies

# Stage 2: Runtime (minimal)
FROM python:3.13-slim
# ... copy only necessary files
```

## Next Steps

After successful build:

1. **Verify Images**
   ```bash
   docker images | grep todo-chatbot
   minikube image ls | grep todo-chatbot
   ```

2. **Create Secrets**
   ```bash
   cd ../helm/gordon
   cp secrets.yaml.example secrets.yaml
   # Edit secrets.yaml with your credentials
   ```

3. **Deploy with Helm**
   ```bash
   helm install todo-app . -f secrets.yaml
   ```

4. **Verify Deployment**
   ```bash
   kubectl get pods
   kubectl get svc
   kubectl get ingress
   ```

5. **Access Application**
   ```bash
   # Add to /etc/hosts
   echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

   # Open browser
   open http://todo.local
   ```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build images
        run: |
          cd phase4-k8/docker
          ./build.sh --no-minikube

      - name: Push to registry
        run: |
          docker tag todo-chatbot-backend:latest $REGISTRY/todo-chatbot-backend:$VERSION
          docker push $REGISTRY/todo-chatbot-backend:$VERSION
```

## Best Practices

1. **Tag Images with Versions**
   ```bash
   ./build.sh --backend-tag todo-chatbot-backend:v1.0.0
   ```

2. **Use .dockerignore**
   - Exclude node_modules
   - Exclude .git directories
   - Exclude test files

3. **Layer Caching**
   - Docker caches layers
   - Rebuild is faster if dependencies haven't changed
   - Order matters: less frequently changed files first

4. **Security**
   - Always run as non-root user
   - Scan images: `docker scan todo-chatbot-backend:latest`
   - Keep base images updated

5. **Size Optimization**
   - Use Alpine base images where possible
   - Remove build dependencies in final image
   - Use multi-stage builds

## References

- **Skill Spec:** `../.claude/skills/phase4-docker-build.skill.md`
- **Phase 4 Spec:** `../specs/features/kubernetes-deployment.md`
- **Helm Chart:** `../helm/gordon/`
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/

## Support

For issues:
1. Check logs in `../logs/`
2. Review PHR in `../history/prompts/`
3. Consult troubleshooting section above
4. GitHub Issues: [your-repo]/issues

---

**Version:** 1.0.0
**Last Updated:** 2025-01-04
**Status:** Ready for use
