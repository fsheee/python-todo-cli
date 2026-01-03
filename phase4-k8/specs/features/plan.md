# Phase IV Implementation Plan (Updated)

## Overview

This plan breaks down the Phase IV Kubernetes deployment into executable tasks based on `kubernetes-deployment.md` and Plan Agent analysis.

**⚠️ Critical Updates Applied:**
- Port 8000 → 8001 corrections throughout
- Database architecture analysis added
- AIOps tool verification tasks added
- Environment variable setup enhanced
- Ingress/storage class verification added
- Pre-deployment validation added
- End-to-end testing enhanced

---

## Plan Strategy

**Approach**: Agentic Dev Stack
- Spec-driven: All work based on `kubernetes-deployment.md`
- Agent-assisted: Use appropriate agents for each phase
- AIOps-enabled: Leverage Gordon, kubectl-ai, kagent
- PHR-captured: All prompts and issues documented

---

## Phase 1: Environment Setup (Estimated: 25 min)

### Task 1.1: Verify Prerequisites

**Agent**: general-purpose

**Steps**:
1.

**Acceptance**:
- [ ] All tools return valid versions
- [ ] Document versions in PHR

---

### Task 1.2: Start Minikube Cluster

**Agent**: general-purpose

**Steps**:
1. Start Minikube: `minikube start --driver=docker --memory=4096 --cpus=2`
2. Enable ingress addon: `minikube addons enable ingress`
3. Enable metrics-server: `minikube addons enable metrics-server`
4. Verify addons: `minikube addons list`

**Acceptance**:
- [ ] Minikube status is "Running"
- [ ] Ingress addon is enabled
- [ ] Metrics-server addon is enabled

---

### Task 1.3: Verify AIOps Tool Availability (NEW)

**Agent**: general-purpose

**Steps**:
1. Test Gordon: `docker ai "What can you do?"`
2. Test kubectl-ai: `kubectl-ai "check cluster status"` (if installed)
3. Test kagent: `kagent --help` (if installed)
4. Document available tools and fallback strategies

**Acceptance**:
- [ ] Documented which AIOps tools are available
- [ ] Fallback strategy defined for unavailable tools
- [ ] PHR documents AIOps tool availability

---

### Task 1.4: Verify Kubernetes Resources (NEW)

**Agent**: general-purpose

**Steps**:
1. Check storage classes: `kubectl get storageclass`
2. Check ingress controller: `kubectl get pods -n ingress-nginx`
3. Check ingress class: `kubectl get ingressclass`
4. Verify available resources: `kubectl describe nodes`

**Acceptance**:
- [ ] Storage class identified (e.g., standard)
- [ ] Ingress controller verified and running
- [ ] Ingress class documented (nginx/traefik/haproxy)
- [ ] Resource limits documented

---

## Phase 2: Containerization (Estimated: 45 min)

### Task 2.1: Explore Phase III Structure

**Agent**: Explore

**Steps**:
1. Explore `../phase3-chatbot/frontend/` directory
2. Explore `../phase3-chatbot/backend/` directory
3. Identify existing Dockerfiles (expecting none)
4. Review build requirements (package.json, requirements.txt, etc.)
5. Identify port configuration from code

**Acceptance**:
- [ ] Document Phase III structure
- [ ] Identify Docker build requirements
- [ ] Confirm no Dockerfiles exist
- [ ] Document backend port (expecting 8001)

---

### Task 2.1.a: Database Architecture Analysis (NEW - CRITICAL)

**Agent**: Explore

**Steps**:
1. Examine `../phase3-chatbot/app/database/__init__.py`
2. Check environment variables in `.env` files
3. Verify if PostgreSQL is actually used or fallback to file storage
4. Review `../phase3-chatbot/app/main.py` for database initialization
5. Document database requirements and storage strategy

**Acceptance**:
- [ ] Clear understanding of database architecture
- [ ] Decision on whether PostgreSQL StatefulSet is needed
- [ ] PHR documents database implementation findings
- [ ] ADR created if architecture decision needed

---

### Task 2.2: Containerize Frontend (UPDATED)

**Agent**: general-purpose + Gordon (or Claude fallback)

**Prerequisites**: Task 2.1 completed

**Frontend Build Requirements**:
- Next.js 14.2.35 build process
- Environment variable: `NEXT_PUBLIC_API_URL`
- Port 3000 (dev) / Port 80 (production Nginx)

**Steps**:
1. Navigate to Phase III frontend: `cd ../phase3-chatbot/frontend`
2. Review package.json build scripts
3. Use Gordon (or Claude fallback):
   - If Gordon available: `docker ai "create multi-stage Dockerfile for Next.js 14 production build"`
   - Fallback: Ask Claude Code to generate multi-stage Dockerfile with:
     - Node.js builder stage
     - Next.js build (next build)
     - Nginx runner stage serving port 80
4. Build image: `docker build -t todo-chatbot-frontend:latest .`
5. Test image: `docker run -p 8080:80 todo-chatbot-frontend:latest`
6. Load into Minikube: `minikube image load todo-chatbot-frontend:latest`

**Acceptance**:
- [ ] Dockerfile created/verified
- [ ] Image builds successfully
- [ ] Container serves app on port 80
- [ ] Image loaded in Minikube
- [ ] PHR documents Dockerfile creation process

---

### Task 2.3: Containerize Backend (UPDATED - PORT FIX)

**Agent**: general-purpose + Gordon (or Claude fallback)

**Prerequisites**: Task 2.1 and 2.1.a completed

**Backend Build Requirements**:
- Python 3.13 runtime
- FastAPI dependencies from requirements.txt
- **Port 8001** (NOT 8000!)
- Health endpoint: `/health` (exists at main.py:127-135)
- Database connection: PostgreSQL or file-based

**Steps**:
1. Navigate to Phase III backend: `cd ../phase3-chatbot` (root)
2. Use Gordon (or Claude fallback):
   - If Gordon available: `docker ai "create optimized Dockerfile for Python FastAPI 3.13"`
   - Fallback: Ask Claude Code to generate Dockerfile with:
     - Python 3.13 slim base image
     - Multi-stage build for smaller image size
     - Uvicorn server on port 8001
     - Health check for /health endpoint
3. Build image: `docker build -t todo-chatbot-backend:latest .`
4. Test image: `docker run -p 8001:8001 todo-chatbot-backend:latest`
5. Verify health: `curl http://localhost:8001/health`
6. Load into Minikube: `minikube image load todo-chatbot-backend:latest`

**Acceptance**:
- [ ] Dockerfile created/verified
- [ ] Image builds successfully
- [ ] Health endpoint responds on port 8001
- [ ] Database connection works (if PostgreSQL used)
- [ ] Image loaded in Minikube
- [ ] PHR documents Dockerfile creation process

**⚠️ CRITICAL**: All subsequent tasks must use port 8001, not 8000!

---

## Phase 3: Helm Chart Creation (Estimated: 60 min)

### Task 3.1: Generate Helm Chart Structure

**Agent**: Plan + general-purpose

**Prerequisites**: Tasks 2.1, 2.1.a, 2.2, 2.3 completed

**Steps**:
1. Use kubectl-ai: `kubectl-ai "generate Helm chart structure for todo chatbot"`
2. Create directory structure: `helm-chart/`
3. Create `Chart.yaml` with metadata
4. Create initial `values.yaml`

**Acceptance**:
- [ ] Helm chart directory structure exists
- [ ] Chart.yaml has valid API version and metadata
- [ ] values.yaml has default configuration

---

### Task 3.2: Frontend Deployment & Service (UPDATED)

**Agent**: general-purpose + kubectl-ai

**Prerequisites**: Task 2.2 completed, Task 3.1 completed

**Configuration**:
- Image: todo-chatbot-frontend:latest
- Replicas: 1
- **Port: 80** (Nginx production) or 3000 (Next.js dev)
- Resource limits: 128Mi/256Mi, 100m/200m CPU
- Health check: `/` endpoint

**Steps**:
1. Use kubectl-ai: `kubectl-ai "generate Kubernetes Deployment manifest for Next.js frontend"`
2. Create `templates/frontend-deployment.yaml`:
   - Image: todo-chatbot-frontend:latest
   - Replicas: 1
   - Resource limits: 128Mi/256Mi, 100m/200m CPU
   - Port: 80 (production Nginx) or 3000 (Next.js)
   - Environment variable: `NEXT_PUBLIC_API_URL` (from ConfigMap)
   - Liveness/readiness probes: HTTP GET to `/`
3. Create `templates/frontend-service.yaml`:
   - Type: ClusterIP
   - Port: 80 or 3000
   - Target port: Container port

**Acceptance**:
- [ ] Frontend deployment template created
- [ ] Frontend service template created
- [ ] Port configuration correct
- [ ] Environment variable configured
- [ ] Templates use Helm values

---

### Task 3.3: Backend Deployment & Service (UPDATED - PORT FIX)

**Agent**: general-purpose + kubectl-ai

**Prerequisites**: Task 2.3 completed, Task 3.1 completed

**Configuration**:
- Image: todo-chatbot-backend:latest
- Replicas: 1
- **Port: 8001** (CORRECTED!)
- Resource limits: 256Mi/512Mi, 100m/500m CPU
- Health check: `/health` endpoint

**Steps**:
1. Use kubectl-ai: `kubectl-ai "generate Kubernetes Deployment manifest for FastAPI backend"`
2. Create `templates/backend-deployment.yaml`:
   - Image: todo-chatbot-backend:latest
   - Replicas: 1
   - Resource limits: 256Mi/512Mi, 100m/500m CPU
   - **Port: 8001** (CORRECTED!)
   - Environment variables:
     - `DATABASE_URL` (from Secret or ConfigMap)
     - `OPENAI_API_KEY` (from Secret - CRITICAL!)
     - `BETTER_AUTH_SECRET` (from Secret, if used)
   - Liveness/readiness probes: HTTP GET to `/health`
3. Create `templates/backend-service.yaml`:
   - Type: ClusterIP
   - **Port: 8001** (CORRECTED!)
   - Target port: 8001

**Acceptance**:
- [ ] Backend deployment template created
- [ ] Backend service template created
- [ ] Port configured as 8001
- [ ] Templates use Helm values

---

### Task 3.4: Backend ConfigMap & Secret (NEW)

**Agent**: general-purpose

**Prerequisites**: Task 2.1.a completed (database architecture known)

**Steps**:
1. Create `templates/backend-configmap.yaml`:
   - Non-sensitive environment variables:
     - `NEXT_PUBLIC_API_URL` (if needed)
     - Logging configuration
     - Rate limiting settings
2. Create `templates/backend-secret.yaml`:
   - **Sensitive data**:
     - `OPENAI_API_KEY` (CRITICAL - must be secret!)
     - `BETTER_AUTH_SECRET` (if used)
     - `DATABASE_PASSWORD` (if PostgreSQL used)
3. Document secret setup in values.yaml

**Acceptance**:
- [ ] ConfigMap template created
- [ ] Secret template created
- [ ] Sensitive data properly isolated
- [ ] values.yaml documents secret requirements

---

### Task 3.5: PostgreSQL StatefulSet & Service (UPDATED - CONDITIONAL)

**Agent**: general-purpose + kubectl-ai

**Prerequisites**: Task 2.1.a completed (database architecture decision made)

**Condition**: Only execute if PostgreSQL is required (per Task 2.1.a findings)

**Configuration**:
- Image: postgres:16-alpine
- Resource limits: 256Mi/512Mi, 100m/500m CPU
- Port: 5432
- PVC with 1Gi storage

**Steps**:
1. **IF PostgreSQL required**:
   - Use kubectl-ai: `kubectl-ai "generate Kubernetes StatefulSet for PostgreSQL with PVC"`
   - Create `templates/postgres-statefulset.yaml`
   - Create `templates/postgres-service.yaml`
   - Create `templates/postgres-pvc.yaml` (if separate)
2. **IF file-based storage**:
   - Skip this task entirely
   - Consider adding PVC for backend file storage
   - Document decision in ADR

**Acceptance** (if executed):
- [ ] PostgreSQL StatefulSet template created
- [ ] PostgreSQL service template created
- [ ] PVC configuration correct
- [ ] Templates use Helm values

**Acceptance** (if skipped):
- [ ] PHR documents why PostgreSQL was skipped
- [ ] ADR documents file-based storage approach

---

### Task 3.6: Ingress Configuration (UPDATED)

**Agent**: general-purpose + kubectl-ai

**Prerequisites**:
- Task 3.2 completed (frontend service)
- Task 3.3 completed (backend service)
- Task 1.4 completed (ingress class known)

**Configuration**:
- Ingress class: Verified from Task 1.4 (e.g., nginx, traefik)
- Host: todo.local
- Routes: `/` → frontend, `/api/` → backend (port 8001)

**Steps**:
1. Use kubectl-ai: `kubectl-ai "generate NGINX Ingress for todo app with host routing"`
2. Verify ingress class from Task 1.4:
   ```bash
   kubectl get ingressclass
   ```
3. Create `templates/ingress.yaml`:
   - Ingress class: From Task 1.4 findings (e.g., nginx)
   - Host: todo.local
   - Routes:
     - `/` → frontend service (port 80/3000)
     - `/api/` → backend service (port 8001) with rewrite rules
   - Annotations for rewrite rules (controller-specific)

**Acceptance**:
- [ ] Ingress class verified
- [ ] Ingress template created
- [ ] Routes configured correctly (frontend: `/`, backend: `/api/`)
- [ ] Annotations match ingress controller
- [ ] Backend route uses port 8001

---

### Task 3.7: Complete values.yaml (ENHANCED)

**Agent**: general-purpose

**Prerequisites**: Tasks 3.2-3.6 completed

**Steps**:
1. Update `values.yaml` with all configurable parameters:
   - Global image settings (registry, pullPolicy)
   - Frontend configuration (image, replicas, resources, env)
   - Backend configuration (image, replicas, resources, secrets, config)
   - PostgreSQL configuration (if used: image, storage, resources)
   - Ingress configuration (enabled, className, host, annotations)
2. Add comments for all parameters
3. Set sensible defaults for local Minikube
4. Document secret setup requirements

**Acceptance**:
- [ ] All templates reference values.yaml
- [ ] All parameters have clear comments
- [ ] Defaults work for local Minikube deployment
- [ ] Secret setup documented
- [ ] Port references use 8001 for backend

---

### Task 3.8: Validate Helm Chart (ENHANCED)

**Agent**: general-purpose

**Prerequisites**: All Phase 3 tasks completed

**Steps**:
1. Run Helm lint: `helm lint ./helm-chart`
2. Render templates: `helm template todo-app ./helm-chart`
3. Dry-run deployment: `helm install --dry-run --debug todo-app ./helm-chart`
4. Fix any warnings or errors
5. Review rendered manifests

**Acceptance**:
- [ ] Helm lint passes without warnings
- [ ] Templates render correctly
- [ ] Dry-run deployment succeeds
- [ ] All Kubernetes resources are valid

---

## Phase 4: Deployment (Estimated: 25 min)

### Task 4.0: Pre-Deployment Validation (NEW)

**Agent**: general-purpose

**Prerequisites**: All Phase 3 tasks completed

**Steps**:
1. Validate Helm chart:
   ```bash
   helm lint ./helm-chart
   helm template todo-app ./helm-chart --debug
   helm install --dry-run --debug todo-app ./helm-chart
   ```
2. Verify resources:
   ```bash
   kubectl get storageclass
   kubectl get ingressclass
   kubectl get nodes -o wide
   ```
3. Check image availability:
   ```bash
   minikube image ls | grep todo-chatbot
   ```

**Acceptance**:
- [ ] Helm lint passes
- [ ] Dry-run deployment succeeds
- [ ] Storage classes available
- [ ] Ingress class available
- [ ] Images loaded in Minikube

---

### Task 4.1: Deploy Helm Chart

**Agent**: general-purpose + kubectl-ai

**Prerequisites**: Task 4.0 completed

**Steps**:
1. Use kubectl-ai: `kubectl-ai "install Helm chart from ./helm-chart"`
2. Install with secrets: `helm install todo-app ./helm-chart --set backend.secret.OPENAI_API_KEY=sk-...`
3. Check status: `helm list`

**Acceptance**:
- [ ] Helm installation succeeds
- [ ] Release is deployed

---

### Task 4.2: Monitor Deployment

**Agent**: general-purpose

**Prerequisites**: Task 4.1 completed

**Steps**:
1. Watch pods: `kubectl get pods -w`
2. Wait for all pods to be Running
3. Check services: `kubectl get svc`
4. Check ingress: `kubectl get ingress`
5. Describe any failing pods: `kubectl describe pod <pod-name>`

**Acceptance**:
- [ ] All pods are Running
- [ ] All services have endpoints
- [ ] Ingress is created

---

### Task 4.3: Configure DNS (ENHANCED)

**Agent**: general-purpose

**Prerequisites**: Task 4.2 completed (ingress created)

**Steps**:
1. Get Minikube IP: `minikube ip`
2. **Windows** (add to `C:\Windows\System32\drivers\etc\hosts`):
   ```
   <minikube-ip> todo.local
   ```
3. **Linux/Mac** (add to `/etc/hosts`):
   ```
   <minikube-ip> todo.local
   ```
4. Test DNS: `ping todo.local`
5. Test HTTP: `curl -v http://todo.local`

**Troubleshooting**:
- If ping fails: Check hosts file permissions and IP
- If HTTP fails: Check ingress controller: `kubectl get pods -n ingress-nginx`
- If 404/503: Check ingress configuration: `kubectl describe ingress todo-app-ingress`

**Acceptance**:
- [ ] DNS resolves to Minikube IP
- [ ] Host entry created
- [ ] Ping succeeds
- [ ] HTTP connection succeeds

---

## Phase 5: Validation & Testing (Estimated: 45 min)

### Task 5.1: Verify Application Access

**Agent**: general-purpose

**Prerequisites**: Task 4.3 completed

**Steps**:
1. Access frontend: `http://todo.local`
2. Verify page loads
3. Check browser console for errors
4. Test backend API: `curl http://todo.local/api/health`

**Acceptance**:
- [ ] Frontend loads successfully
- [ ] No console errors
- [ ] Backend health endpoint responds (port 8001)

---

### Task 5.2: Cluster Health Analysis

**Agent**: kagent (if available) + general-purpose

**Prerequisites**: Task 4.2 completed

**Steps**:
1. Use kagent: `kagent "analyze cluster health"` (if available)
2. Check resource usage: `kubectl top pods`
3. Check pod logs:
   - `kubectl logs -f deployment/todo-app-frontend`
   - `kubectl logs -f deployment/todo-app-backend`
   - `kubectl logs -f statefulset/todo-app-postgres` (if used)
4. Verify no errors

**Acceptance**:
- [ ] No critical issues reported
- [ ] Resource usage within limits
- [ ] No error logs
- [ ] All pods healthy

---

### Task 5.3: Test Data Persistence

**Agent**: general-purpose

**Prerequisites**: Task 5.1 completed

**Steps**:
1. Create a task via application
2. Note task ID and details
3. Restart relevant pod:
   - If PostgreSQL: `kubectl delete pod <postgres-pod>`
   - If file storage: `kubectl delete pod -l app=todo-app-backend`
4. Wait for new pod to start
5. Verify task still exists

**Acceptance**:
- [ ] Task persists across restart
- [ ] Data not lost
- [ ] PHR documents persistence test results

---

### Task 5.4: Complete User Flow Test (ENHANCED)

**Agent**: general-purpose

**Prerequisites**: Task 5.1 completed

**Steps**:
1. Test user authentication flow:
   - Navigate to `http://todo.local/login`
   - Attempt login (with test credentials)
   - Verify JWT token received
2. Test todo operations:
   - Create multiple todos
   - List todos
   - Update a todo
   - Complete a todo
   - Delete a todo
3. Test chatbot functionality (if Phase III features exist):
   - Send chat message
   - Verify AI response
   - Test tool invocation
4. Test frontend-backend communication:
   - Check browser network tab
   - Verify API calls succeed
   - Verify no CORS errors

**Acceptance**:
- [ ] All Phase III features work in Kubernetes
- [ ] User can complete full workflow
- [ ] Data persists across pod restarts
- [ ] No CORS errors
- [ ] No console errors

---

### Task 5.5: End-to-End Integration Testing (NEW)

**Agent**: general-purpose

**Prerequisites**: Task 5.4 completed

**Steps**:
1. Verify all services communicate:
   - Frontend → Backend (via `/api/` routes)
   - Backend → PostgreSQL (if used)
2. Test error handling:
   - Invalid API requests
   - Network failures
   - Database connection issues
3. Verify logging:
   - Check all pod logs for errors
   - Verify structured logging format
4. Performance verification:
   - Page load time acceptable
   - API response time acceptable
   - Resource usage stable

**Acceptance**:
- [ ] All services communicate correctly
- [ ] Error handling works as expected
- [ ] Logs are complete and structured
- [ ] Performance meets requirements
- [ ] PHR documents integration test results

---

## Phase 6: Documentation & Cleanup (Estimated: 20 min)

### Task 6.1: Create README.md

**Agent**: general-purpose

**Prerequisites**: Phase 5 completed

**Steps**:
1. Document setup instructions
2. Document deployment process
3. Document access method
4. Add troubleshooting section
5. Document environment variable setup
6. Include helm command examples

**Acceptance**:
- [ ] README.md created
- [ ] All steps documented
- [ ] Troubleshooting includes common issues
- [ ] Environment setup documented

---

### Task 6.2: Create Troubleshooting Guide (NEW)

**Agent**: general-purpose

**Prerequisites**: Phase 5 completed

**Create**: `TROUBLESHOOTING.md` with sections:
- Pods not starting (ImagePullBackOff, CrashLoopBackOff, Pending)
- Ingress not working (404, DNS issues)
- Database connection issues
- Port mismatch issues
- Storage issues (PVC pending)

**Acceptance**:
- [ ] TROUBLESHOOTING.md created
- [ ] Common issues documented
- [ ] Solutions provided for each issue

---

### Task 6.3: Record All PHRs

**Agent**: general-purpose

**Prerequisites**: All phases completed

**Steps**:
1. Review all prompts used
2. Create PHR for each significant issue encountered
3. Store in `history/phr/`
4. Store prompt history in `history/prompts/`

**Acceptance**:
- [ ] All significant issues documented
- [ ] All prompts recorded
- [ ] PHRs follow template format

---

### Task 6.4: Create ADRs (if needed)

**Agent**: general-purpose

**Prerequisites**: All phases completed

**Steps**:
1. Identify significant architectural decisions made:
   - Database architecture (PostgreSQL vs file storage)
   - Helm chart structure decisions
   - Resource allocation strategy
   - Ingress configuration approach
2. Create ADR for each decision
3. Store in `history/adr/` (if directory created)

**Acceptance**:
- [ ] Major decisions documented
- [ ] ADRs follow standard format
- [ ] Architecture decisions justified

---

### Task 6.5: Create Helm Chart README (NEW)

**Agent**: general-purpose

**Prerequisites**: Phase 3 completed

**Create**: `helm-chart/README.md` with:
- Chart overview
- Prerequisites
- Installation instructions
- Configuration values
- Upgrade/uninstall commands
- Troubleshooting reference

**Acceptance**:
- [ ] Helm chart README.md created
- [ ] Installation instructions clear
- [ ] Configuration documented
- [ ] Examples provided

---

## Risk Mitigation Plan

| Risk                              | Mitigation Strategy                                              | Status |
|-----------------------------------|----------------------------------------------------------------|---------|
| Gordon unavailable                 | Fallback to standard Docker CLI + Claude Code generation       | ✅ Added task 1.3 |
| kubectl-ai unavailable           | Use kubectl directly with Claude assistance                  | ✅ Added task 1.3 |
| kagent unavailable               | Use kubectl commands and manual analysis                         | ✅ Added task 1.3 |
| Minikube resource constraints         | Configure adequate resources (4GB RAM, 2 CPU cores)              | ✅ In task 1.2 |
| Images not pulling               | Use `minikube image load` for local images                     | ✅ In tasks 2.2, 2.3 |
| Ingress not working                 | Verify /etc/hosts, check ingress controller, verify ingress class  | ✅ Enhanced task 4.3 |
| PostgreSQL data loss                 | Use StatefulSet + PVC for data persistence                      | ✅ Conditional task 3.5 |
| Port mismatch (8000 vs 8001)        | All plans use port 8001 for backend                            | ✅ FIXED throughout |
| File storage data loss         | Task 2.1.a investigates database architecture                     | ✅ Added task 2.1.a |
| Environment variable issues     | Enhanced ConfigMap/Secret setup in task 3.4                      | ✅ Added task 3.4 |
| Storage class unavailable        | Task 1.4 verifies available storage classes                    | ✅ Added task 1.4 |
| Ingress class mismatch        | Task 1.4 verifies ingress class                                 | ✅ Added task 1.4 |
| Deployment failures            | Task 4.0 adds pre-deployment validation                          | ✅ Added task 4.0 |

---

## Success Metrics

### Primary Metrics

- [ ] 100% of pods Running
- [ ] 100% of services have endpoints
- [ ] Application fully functional
- [ ] Data persistence verified
- [ ] Backend accessible on port 8001

### Secondary Metrics

- [ ] Zero errors in pod logs
- [ ] Resource usage within limits
- [ ] Helm install time < 5 min
- [ ] Documentation complete
- [ ] All PHRs documented

---

## Task Dependencies

```
Phase 1 (Setup) → Phase 2 (Containerize) → Phase 3 (Helm Chart)
                                                            ↓
                                              Phase 4 (Deploy) → Phase 5 (Validate) → Phase 6 (Docs)
```

**Critical Path**:
1. Environment must be setup before containerization
2. Database architecture must be understood (2.1.a) before containerization completes
3. Images must exist before Helm chart creation
4. Helm chart must be created and validated before deployment
5. Pre-deployment validation (4.0) must pass before install
6. Deployment must succeed before validation
7. Validation must pass before documentation completion

---

## Estimated Total Time (Updated)

- Phase 1: 25 min (added tasks 1.3, 1.4)
- Phase 2: 45 min (added task 2.1.a, enhanced Dockerfile creation)
- Phase 3: 60 min (enhanced ConfigMap/Secret, added pre-dep validation)
- Phase 4: 25 min (added pre-dep validation, enhanced DNS config)
- Phase 5: 45 min (enhanced testing, added integration test)
- Phase 6: 20 min (added troubleshooting, helm README)

**Total: ~220 minutes (3.7 hours)**

**Buffer for issues: +40 min** (AIOps fallback, database investigation, ingress troubleshooting)

**Total with buffer: ~260 minutes (4.3 hours)**

---

## Next Actions

1. **Execute Task 1.1** - Verify prerequisites
2. **Create PHR** - Document environment setup
3. **Proceed through phases** - Follow task order
4. **Document issues** - Create PHR for every blocker
5. **Create ADRs** - Document architectural decisions (especially database)
6. **Validate success** - Meet all acceptance criteria

---

**Plan Version**: 2.0
**Based On Spec**: `kubernetes-deployment.md`
**Reviewed By**: Plan Agent
**Status**: Updated with all recommended improvements - Ready for Execution

---

## Summary of Critical Updates

| Category | Update | Impact |
|-----------|---------|---------|
| Port Configuration | Changed 8000 → 8001 throughout | Fixes backend connectivity |
| Database Analysis | Added task 2.1.a | Determines if PostgreSQL needed |
| AIOps Verification | Added task 1.3 | Uncovers tool availability early |
| Resource Verification | Added task 1.4 | Prevents PVC/Ingress failures |
| Environment Variables | Enhanced task 3.4 | Ensures proper ConfigMap/Secret setup |
| Pre-Deployment Validation | Added task 4.0 | Catches issues before install |
| DNS Configuration | Enhanced task 4.3 | Better troubleshooting |
| Integration Testing | Added task 5.5 | Comprehensive validation |
| Documentation | Added tasks 6.2, 6.5 | Troubleshooting + Helm README |
| Timeline | 2.5h → 4.3h | Accounts for Dockerfile creation, investigation |
