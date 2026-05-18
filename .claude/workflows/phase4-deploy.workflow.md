# Workflow: Phase 4 Deployment

**Version:** 1.0.0
**Author:** Claude Code AI Agent
**Date:** 2025-01-04
**Type:** Deployment Workflow

---

## Purpose

Complete end-to-end deployment workflow for Todo Chatbot application to Kubernetes (Minikube). Orchestrates multiple skills to achieve full Phase 4 deployment without modifying Phase 2 or Phase 3 code.

---

## Architecture Understanding

### Code Reuse Strategy
```
Phase 2: Backend (FastAPI) + Frontend (Next.js) + Auth
Phase 3: Frontend (ChatKit) + AI Agents (on top of Phase 2 backend)
Phase 4: Kubernetes deployment (using Phase 2 backend + Phase 3 frontend)
```

### What Gets Deployed
- **Backend:** `phase2-web/backend/` (FastAPI + AI agents)
- **Frontend:** `phase3-chatbot/frontend/` (Next.js + ChatKit)
- **Database:** External Neon PostgreSQL (no pod)

---

## Workflow Steps

### 1. Environment Setup
**Skill:** `minikube-setup` (to be created)
**Purpose:** Initialize Minikube cluster with required addons

**Actions:**
- Start Minikube cluster
- Enable ingress addon
- Enable metrics-server addon
- Verify cluster status

**Skip if:** Minikube already running

---

### 2. Build Docker Images
**Skill:** `phase4-docker-build` (exists)
**Purpose:** Build backend and frontend images

**Actions:**
- Build backend from `phase2-web/backend/`
- Build frontend from `phase3-chatbot/frontend/`
- Load images into Minikube
- Generate build logs and PHR

**Configuration:**
```yaml
backend:
  source: phase2-web/backend/
  tag: todo-chatbot-backend:latest

frontend:
  source: phase3-chatbot/frontend/
  tag: todo-chatbot-frontend:latest
```

---

### 3. Configure Secrets
**Skill:** `k8s-secrets-configure` (to be created)
**Purpose:** Set up Kubernetes secrets for deployment

**Actions:**
- Prompt for required secrets
- Validate secret format
- Create Kubernetes secret resources
- Verify secrets created

**Required Secrets:**
- `OPEN_ROUTER_API_KEY` or `OPENAI_API_KEY`
- `DATABASE_URL` (Neon PostgreSQL)
- `BETTER_AUTH_SECRET`
- `INTERNAL_SERVICE_TOKEN`

---

### 4. Deploy with Helm
**Skill:** `helm-deploy` (to be created)
**Purpose:** Deploy application using Helm chart

**Actions:**
- Validate Helm chart
- Install/upgrade release
- Wait for pods to be ready
- Verify deployment health

**Configuration:**
```yaml
chart: phase4-k8/helm/gordon/
release_name: todo-app
values_file: secrets.yaml
```

---

### 5. Configure Ingress
**Skill:** `k8s-ingress-setup` (to be created)
**Purpose:** Set up ingress for external access

**Actions:**
- Add Minikube IP to /etc/hosts
- Verify ingress created
- Test ingress routing
- Display access URL

**Expected Result:**
- Application accessible at `http://todo.local`

---

### 6. Verify Deployment
**Skill:** `k8s-verify` (to be created)
**Purpose:** Comprehensive deployment verification

**Actions:**
- Check all pods running
- Check services have endpoints
- Check ingress configured
- Test health endpoints
- Verify logs for errors

**Success Criteria:**
- All pods: `Running` state
- Backend health: `200 OK`
- Frontend accessible
- No error logs

---

### 7. Generate Deployment Report
**Skill:** Built-in (no separate skill)
**Purpose:** Create PHR with deployment summary

**Actions:**
- Collect pod status
- Collect service endpoints
- Collect resource usage
- Generate PHR document

---

## Workflow Execution

### Quick Deploy (All Steps)

```bash
# Execute full workflow
claude-code workflow run phase4-deploy
```

### Step-by-Step Deploy

```bash
# Step 1: Setup environment
claude-code skill run minikube-setup

# Step 2: Build images
cd phase4-k8/docker
./build.sh

# Step 3: Configure secrets
claude-code skill run k8s-secrets-configure

# Step 4: Deploy with Helm
cd phase4-k8
helm install todo-app helm/gordon/ -f secrets.yaml

# Step 5: Configure ingress
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Step 6: Verify
kubectl get pods
kubectl get svc
kubectl get ingress
```

### Selective Steps

```bash
# Only build images
claude-code workflow run phase4-deploy --steps=build

# Build and deploy (skip setup)
claude-code workflow run phase4-deploy --steps=build,deploy

# Only verify existing deployment
claude-code workflow run phase4-deploy --steps=verify
```

---

## Workflow Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `minikube_driver` | String | No | `docker` | Minikube driver (docker, virtualbox, etc.) |
| `minikube_memory` | String | No | `4096` | Memory allocation (MB) |
| `minikube_cpus` | String | No | `2` | CPU cores |
| `backend_source` | Path | Yes | `phase2-web/backend/` | Backend source directory |
| `frontend_source` | Path | Yes | `phase3-chatbot/frontend/` | Frontend source directory |
| `helm_chart` | Path | Yes | `phase4-k8/helm/gordon/` | Helm chart location |
| `release_name` | String | No | `todo-app` | Helm release name |
| `skip_minikube_setup` | Boolean | No | `false` | Skip Minikube setup if running |
| `skip_image_build` | Boolean | No | `false` | Skip image build if exists |

---

## Workflow Outputs

### Artifacts Created

```
phase4-k8/
├── logs/
│   ├── workflow-execution-YYYY-MM-DD-HH-MM-SS.log
│   ├── backend-build.log
│   ├── frontend-build.log
│   └── deployment-status.json
└── history/
    └── prompts/
        └── phase4-deploy-YYYY-MM-DD-HH-MM-SS.md (PHR)
```

### Deployment Status JSON

```json
{
  "workflow": "phase4-deploy",
  "version": "1.0.0",
  "timestamp": "2025-01-04T10:30:00Z",
  "status": "success",
  "steps": {
    "minikube_setup": { "status": "success", "duration": "15s" },
    "docker_build": { "status": "success", "duration": "120s" },
    "secrets_configure": { "status": "success", "duration": "5s" },
    "helm_deploy": { "status": "success", "duration": "45s" },
    "ingress_setup": { "status": "success", "duration": "10s" },
    "verification": { "status": "success", "duration": "20s" }
  },
  "deployment": {
    "release_name": "todo-app",
    "namespace": "default",
    "pods": 2,
    "services": 2,
    "ingress_url": "http://todo.local"
  },
  "images": {
    "backend": "todo-chatbot-backend:latest",
    "frontend": "todo-chatbot-frontend:latest"
  }
}
```

---

## Preconditions

### System Requirements
- ✅ Docker Desktop installed and running
- ✅ kubectl installed and configured
- ✅ Helm 3.x installed
- ✅ Minikube installed (or can be installed)
- ✅ Minimum 4GB RAM available
- ✅ Minimum 10GB disk space

### Code Requirements
- ✅ Phase 2 backend exists at `phase2-web/backend/`
- ✅ Phase 3 frontend exists at `phase3-chatbot/frontend/`
- ✅ Phase 4 Helm chart exists at `phase4-k8/helm/gordon/`

### Credentials Required
- ✅ OpenRouter or OpenAI API key
- ✅ Neon PostgreSQL connection string
- ✅ Better Auth secret
- ✅ Internal service token

---

## Postconditions

### Kubernetes Resources
- ✅ Namespace: `default` (or custom)
- ✅ Pods: 2 running (frontend + backend)
- ✅ Services: 2 ClusterIP
- ✅ Ingress: 1 with routes
- ✅ Secrets: 1 with credentials
- ✅ ConfigMap: 1 with env vars

### Application State
- ✅ Backend API responding on port 8001
- ✅ Frontend accessible on port 80
- ✅ Health checks passing
- ✅ Database connected (Neon)
- ✅ Ingress routing working

### Access
- ✅ Application URL: `http://todo.local`
- ✅ API docs: `http://todo.local/docs`
- ✅ Health endpoint: `http://todo.local/health`

---

## Error Handling

### Workflow Failure Recovery

**If Step 1 (Minikube Setup) Fails:**
- Check Docker Desktop running
- Check virtualization enabled
- Retry with different driver: `--minikube-driver=virtualbox`

**If Step 2 (Docker Build) Fails:**
- Check source directories exist
- Check Dockerfile syntax
- Review build logs: `logs/backend-build.log`
- Retry individual image: `./build.sh --backend-only`

**If Step 3 (Secrets) Fails:**
- Validate secret format
- Check Kubernetes connection: `kubectl cluster-info`
- Manually create secret: `kubectl create secret generic ...`

**If Step 4 (Helm Deploy) Fails:**
- Validate chart: `helm lint helm/gordon/`
- Check image availability: `minikube image ls`
- Review Helm output for specific error
- Rollback if needed: `helm rollback todo-app`

**If Step 5 (Ingress) Fails:**
- Check ingress controller: `kubectl get pods -n ingress-nginx`
- Verify ingress resource: `kubectl describe ingress`
- Check /etc/hosts entry
- Try port-forward as fallback: `kubectl port-forward svc/todo-app-frontend 8080:80`

**If Step 6 (Verification) Fails:**
- Check pod logs: `kubectl logs deployment/todo-app-backend`
- Check events: `kubectl get events`
- Verify secrets mounted: `kubectl describe pod <pod-name>`
- Check resource limits: `kubectl describe nodes`

---

## Rollback Procedure

### Complete Rollback

```bash
# Uninstall Helm release
helm uninstall todo-app

# Delete secrets
kubectl delete secret todo-app-backend-secret

# Remove images from Minikube
minikube image rm todo-chatbot-backend:latest
minikube image rm todo-chatbot-frontend:latest

# Remove local Docker images
docker rmi todo-chatbot-backend:latest
docker rmi todo-chatbot-frontend:latest

# Stop Minikube (optional)
minikube stop
```

### Partial Rollback

```bash
# Rollback to previous Helm release
helm rollback todo-app

# Restart specific deployment
kubectl rollout restart deployment/todo-app-backend
```

---

## Skills Composition

This workflow composes the following skills:

| Step | Skill | Status | Location |
|------|-------|--------|----------|
| 1 | `minikube-setup` | ⚠️ To be created | `.claude/skills/` |
| 2 | `phase4-docker-build` | ✅ Exists | `.claude/skills/phase4-docker-build.skill.md` |
| 3 | `k8s-secrets-configure` | ⚠️ To be created | `.claude/skills/` |
| 4 | `helm-deploy` | ⚠️ To be created | `.claude/skills/` |
| 5 | `k8s-ingress-setup` | ⚠️ To be created | `.claude/skills/` |
| 6 | `k8s-verify` | ⚠️ To be created | `.claude/skills/` |

**Note:** Skills marked ⚠️ need to be created following the same spec-driven approach as `phase4-docker-build`.

---

## Workflow Variants

### Development Workflow
```yaml
name: phase4-deploy-dev
steps:
  - minikube-setup
  - docker-build (--no-cache for fresh builds)
  - secrets-configure (dev credentials)
  - helm-deploy (dev values)
  - verify (skip ingress, use port-forward)
```

### Production Workflow
```yaml
name: phase4-deploy-prod
steps:
  - k8s-cluster-verify (cloud K8s, not Minikube)
  - docker-build-push (push to registry)
  - secrets-from-vault (use external secret management)
  - helm-deploy (prod values, replicas=3)
  - ingress-setup (real domain, TLS)
  - verify (comprehensive checks)
  - monitoring-setup (Prometheus/Grafana)
```

### Quick Test Workflow
```yaml
name: phase4-quick-test
steps:
  - docker-build (use cached layers)
  - helm-upgrade (if already deployed)
  - verify-pods-only
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Phase 4 Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Phase 4 Deployment Workflow
        run: |
          claude-code workflow run phase4-deploy \
            --skip-minikube-setup \
            --backend-source=phase2-web/backend \
            --frontend-source=phase3-chatbot/frontend
```

---

## Monitoring and Observability

### Post-Deployment Monitoring

```bash
# Watch pod status
kubectl get pods -w

# View logs (streaming)
kubectl logs -f deployment/todo-app-backend
kubectl logs -f deployment/todo-app-frontend

# Check resource usage
kubectl top pods
kubectl top nodes

# View events
kubectl get events --sort-by='.lastTimestamp'
```

### Health Checks

```bash
# Backend health
curl http://todo.local/health

# Frontend health
curl http://todo.local/

# API docs
curl http://todo.local/docs
```

---

## Best Practices

1. **Always Use Workflow**
   - Don't run skills individually unless debugging
   - Workflow ensures correct order and dependencies

2. **Version Control**
   - Commit `secrets.yaml.example` (without real secrets)
   - Add `secrets.yaml` to `.gitignore`

3. **Idempotency**
   - Workflow can be run multiple times safely
   - Use `helm upgrade --install` for idempotent deploys

4. **Testing**
   - Test workflow in development first
   - Use `--dry-run` flags where available

5. **Documentation**
   - Every workflow execution creates PHR
   - Review PHR for debugging and auditing

---

## References

- **Phase 4 Spec:** `phase4-k8/specs/features/kubernetes-deployment.md`
- **Docker Build Skill:** `.claude/skills/phase4-docker-build.skill.md`
- **Helm Chart:** `phase4-k8/helm/gordon/`
- **Phase 2 Backend:** `phase2-web/backend/`
- **Phase 3 Frontend:** `phase3-chatbot/frontend/`

---

## Changelog

**Version 1.0.0** (2025-01-04)
- Initial workflow definition
- 6-step deployment process
- Skill composition documented
- Error handling and rollback procedures

---

## Next Steps

1. **Create Missing Skills**
   - `minikube-setup`
   - `k8s-secrets-configure`
   - `helm-deploy`
   - `k8s-ingress-setup`
   - `k8s-verify`

2. **Implement Workflow Executor**
   - Script to orchestrate skill execution
   - Handle dependencies between steps
   - Aggregate logs and status

3. **Test Workflow End-to-End**
   - Run on clean Minikube cluster
   - Verify all steps complete
   - Document any issues

4. **Create Workflow Variants**
   - Dev, staging, production workflows
   - Quick test workflow
   - Rollback workflow

---

**Status:** Ready for Implementation
**Dependencies:** phase4-docker-build skill (exists)
**Blocks:** Full Phase 4 deployment
