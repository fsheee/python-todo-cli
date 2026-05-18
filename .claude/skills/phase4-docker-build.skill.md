# Skill: phase4-docker-build

**Version:** 1.0.0
**Author:** Claude Code AI Agent
**Date:** 2025-01-04
**Phase:** Phase 4 - Kubernetes Deployment

---

## Purpose

Build Docker images for Todo Chatbot application components (frontend and backend) from Phase 3 source code without modifying Phase 3 directories. Images are built with Phase 4-specific Dockerfiles and loaded into Minikube for Kubernetes deployment.

---

## Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source_backend_dir` | Path | Yes | `../phase3-chatbot` | Phase 3 backend source directory |
| `source_frontend_dir` | Path | Yes | `../phase3-chatbot/frontend` | Phase 3 frontend source directory |
| `backend_image_tag` | String | Yes | `todo-chatbot-backend:latest` | Docker image tag for backend |
| `frontend_image_tag` | String | Yes | `todo-chatbot-frontend:latest` | Docker image tag for frontend |
| `dockerfile_backend` | Path | Yes | `phase4-k8/docker/backend.Dockerfile` | Backend Dockerfile location |
| `dockerfile_frontend` | Path | Yes | `phase4-k8/docker/frontend.Dockerfile` | Frontend Dockerfile location |
| `load_to_minikube` | Boolean | No | `true` | Whether to load images into Minikube |
| `registry` | String | No | `""` | Docker registry URL (empty for local) |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `backend_image` | Docker Image | Backend Docker image built and tagged |
| `frontend_image` | Docker Image | Frontend Docker image built and tagged |
| `build_logs` | Log File | Build output logs for both images |
| `status` | JSON | Build status with success/failure for each component |
| `image_info` | JSON | Image details (size, layers, created timestamp) |

**Status JSON Format:**
```json
{
  "backend": {
    "success": true,
    "image": "todo-chatbot-backend:latest",
    "size": "342MB",
    "build_time": "45s",
    "loaded_to_minikube": true
  },
  "frontend": {
    "success": true,
    "image": "todo-chatbot-frontend:latest",
    "size": "156MB",
    "build_time": "38s",
    "loaded_to_minikube": true
  }
}
```

---

## Preconditions

### System Requirements
- ✅ Docker installed and running (`docker --version`)
- ✅ Minikube running if `load_to_minikube=true` (`minikube status`)
- ✅ Sufficient disk space (>2GB free)

### Code Requirements
- ✅ Phase 3 backend code exists at `../phase3-chatbot/`
- ✅ Phase 3 frontend code exists at `../phase3-chatbot/frontend/`
- ✅ Backend `requirements.txt` present
- ✅ Frontend `package.json` present

### Phase 4 Requirements
- ✅ Dockerfile templates exist in `phase4-k8/docker/`
- ✅ Build script exists: `phase4-k8/docker/build.sh`

---

## Postconditions

### Docker Images
- ✅ Backend image available: `docker images | grep todo-chatbot-backend`
- ✅ Frontend image available: `docker images | grep todo-chatbot-frontend`
- ✅ Images tagged correctly with specified tags

### Minikube (if `load_to_minikube=true`)
- ✅ Images loaded into Minikube: `minikube image ls | grep todo-chatbot`
- ✅ Images ready for Helm deployment

### Logs
- ✅ Build logs saved to `phase4-k8/logs/docker-build-YYYY-MM-DD-HH-MM-SS.log`
- ✅ PHR (Prompt History Record) created in `phase4-k8/history/prompts/`

---

## Steps / Logic

### Step 1: Validate Preconditions
```bash
# Check Docker
if ! docker --version &> /dev/null; then
    echo "ERROR: Docker not installed"
    exit 1
fi

# Check Minikube (if loading)
if [ "$load_to_minikube" = true ]; then
    if ! minikube status &> /dev/null; then
        echo "ERROR: Minikube not running"
        exit 1
    fi
fi

# Check source directories
if [ ! -d "$source_backend_dir" ]; then
    echo "ERROR: Backend source not found at $source_backend_dir"
    exit 1
fi

if [ ! -d "$source_frontend_dir" ]; then
    echo "ERROR: Frontend source not found at $source_frontend_dir"
    exit 1
fi
```

### Step 2: Build Backend Image
```bash
echo "Building backend image..."
docker build \
    -f phase4-k8/docker/backend.Dockerfile \
    -t $backend_image_tag \
    $source_backend_dir \
    --progress=plain \
    2>&1 | tee logs/backend-build.log

# Capture exit code
backend_exit_code=$?
```

### Step 3: Build Frontend Image
```bash
echo "Building frontend image..."
docker build \
    -f phase4-k8/docker/frontend.Dockerfile \
    -t $frontend_image_tag \
    $source_frontend_dir \
    --progress=plain \
    2>&1 | tee logs/frontend-build.log

# Capture exit code
frontend_exit_code=$?
```

### Step 4: Verify Images Built
```bash
# Check backend image
if docker images | grep -q "$backend_image_tag"; then
    echo "✅ Backend image built successfully"
    backend_size=$(docker images $backend_image_tag --format "{{.Size}}")
else
    echo "❌ Backend image build failed"
fi

# Check frontend image
if 
docker images | grep -q "$frontend_image_tag"; then
    echo "✅ Frontend image built successfully"
    frontend_size=$(docker images $frontend_image_tag --format "{{.Size}}")
else
    echo "❌ Frontend image build failed"
fi
```

### Step 5: Load Images into Minikube (Optional)
```bash
if [ "$load_to_minikube" = true ]; then
    echo "Loading images into Minikube..."

    # Load backend
    minikube image load $backend_image_tag

    # Load frontend
    minikube image load $frontend_image_tag

    # Verify loaded
    minikube image ls | grep todo-chatbot

    echo "✅ Images loaded into Minikube"
fi
```

### Step 6: Generate Status Report
```bash
# Create status JSON
cat > logs/build-status.json <<EOF
{
  "backend": {
    "success": $([ $backend_exit_code -eq 0 ] && echo "true" || echo "false"),
    "image": "$backend_image_tag",
    "size": "$backend_size",
    "loaded_to_minikube": $load_to_minikube
  },
  "frontend": {
    "success": $([ $frontend_exit_code -eq 0 ] && echo "true" || echo "false"),
    "image": "$frontend_image_tag",
    "size": "$frontend_size",
    "loaded_to_minikube": $load_to_minikube
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

cat logs/build-status.json
```

### Step 7: Create PHR (Prompt History Record)
```bash
cat > history/prompts/docker-build-$(date +%Y-%m-%d-%H-%M-%S).md <<EOF
# Docker Build Execution

**Date:** $(date)
**Skill:** phase4-docker-build
**Status:** $([ $backend_exit_code -eq 0 ] && [ $frontend_exit_code -eq 0 ] && echo "SUCCESS" || echo "FAILURE")

## Summary
- Backend: $backend_image_tag (Exit Code: $backend_exit_code)
- Frontend: $frontend_image_tag (Exit Code: $frontend_exit_code)

## Logs
- Backend: logs/backend-build.log
- Frontend: logs/frontend-build.log

## Next Steps
- Verify images: \`docker images | grep todo-chatbot\`
- Deploy with Helm: \`helm install todo-app helm/gordon\`
EOF
```

---

## Error Handling

### Build Failures

**Error:** Docker build fails with exit code != 0

**Handling:**
1. Capture full build logs
2. Parse logs for specific error (missing dependency, syntax error, etc.)
3. Create error PHR with troubleshooting steps
4. Return status JSON with `success: false`
5. DO NOT proceed to Minikube load step

**Example Error Messages:**
```bash
ERROR: Backend build failed (Exit Code: 1)
Check logs at: logs/backend-build.log

Common issues:
- Missing requirements.txt
- Python dependency conflict
- Out of disk space

Troubleshooting:
1. Review build logs
2. Verify Phase 3 code integrity
3. Check Docker daemon status
```

### Minikube Load Failures

**Error:** Image fails to load into Minikube

**Handling:**
1. Verify Minikube is running: `minikube status`
2. Check available disk space in Minikube
3. Try loading again with verbose output
4. Document error in PHR
5. Suggest alternative: push to registry instead

### Disk Space Issues

**Error:** Insufficient disk space during build

**Handling:**
1. Check available space: `df -h`
2. Prune unused Docker images: `docker system prune`
3. Retry build
4. Document in PHR

---

## Logging

### Log Files

All logs stored in `phase4-k8/logs/`:

```
logs/
├── backend-build.log               # Backend Docker build output
├── frontend-build.log              # Frontend Docker build output
├── build-status.json               # Build status summary
└── docker-build-YYYY-MM-DD.log     # Combined log with timestamps
```

### PHR (Prompt History Record)

Created in `phase4-k8/history/prompts/`:

**Format:** `docker-build-YYYY-MM-DD-HH-MM-SS.md`

**Contents:**
- Execution timestamp
- Input parameters
- Build status (success/failure)
- Image details (tags, sizes)
- Error messages (if any)
- Next steps

---

## Versioning

**Skill Version:** 1.0.0

**Changelog:**
- **1.0.0** (2025-01-04): Initial skill definition
  - Backend and frontend image building
  - Minikube image loading
  - Status reporting and logging
  - Error handling

**Dependencies:**
- Docker 20.10+
- Minikube 1.30+
- Bash 4.0+

**Author:** Claude Code AI Agent
**Maintained By:** Phase 4 Development Team

---

## Usage Examples

### Example 1: Build Both Images and Load to Minikube
```bash
# Execute skill
./phase4-k8/docker/build.sh

# Expected output:
# Building backend image...
# [+] Building 45.2s (12/12) FINISHED
# ✅ Backend image built successfully
# Building frontend image...
# [+] Building 38.5s (15/15) FINISHED
# ✅ Frontend image built successfully
# Loading images into Minikube...
# ✅ Images loaded into Minikube
```

### Example 2: Build Only (No Minikube Load)
```bash
# Execute with parameter
./phase4-k8/docker/build.sh --no-minikube

# Or set environment variable
export LOAD_TO_MINIKUBE=false
./phase4-k8/docker/build.sh
```

### Example 3: Custom Image Tags
```bash
# Build with version tags
./phase4-k8/docker/build.sh \
    --backend-tag todo-chatbot-backend:v1.0.0 \
    --frontend-tag todo-chatbot-frontend:v1.0.0
```

---

## Integration with Phase 4 Workflow

### Pre-Deployment Checklist

Before running this skill:
- [ ] Phase 3 code is complete and tested
- [ ] Docker is running
- [ ] Minikube is started
- [ ] Helm chart is configured

### Post-Build Next Steps

After successful build:
1. **Verify images:** `docker images | grep todo-chatbot`
2. **Inspect images:** `docker inspect todo-chatbot-backend:latest`
3. **Check Minikube:** `minikube image ls | grep todo-chatbot`
4. **Deploy with Helm:** `cd phase4-k8 && helm install todo-app helm/gordon -f secrets.yaml`
5. **Verify deployment:** `kubectl get pods`

---

## References

- **Phase 4 Spec:** `phase4-k8/specs/features/kubernetes-deployment.md`
- **Phase 4 Plan:** `phase4-k8/specs/features/plan.md`
- **Phase 4 Tasks:** `phase4-k8/specs/features/tasks.md` (T024-T034)
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/
- **Multi-Stage Builds:** https://docs.docker.com/build/building/multi-stage/

---

## Acceptance Criteria

✅ **Build Success:**
- Both images build without errors
- Images are properly tagged
- Images are optimized (multi-stage builds)

✅ **Minikube Integration:**
- Images load successfully into Minikube
- Images visible in `minikube image ls`

✅ **Logging:**
- All build output logged
- Status JSON generated
- PHR created with execution details

✅ **Error Handling:**
- Build failures are caught and reported
- Clear error messages with troubleshooting steps
- No partial states (both images or none)

---

## Notes

- This skill follows **Spec-Driven Development** principles
- All execution steps are **idempotent** (can be run multiple times safely)
- Skill is **modular** and can be composed with other skills
- Follows Phase 4 **constitution** (CLAUDE.md requirements)

---

**Status:** Ready for Implementation
**Next:** Create Dockerfile templates and build script

