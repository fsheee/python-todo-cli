# Tasks: Phase IV - Kubernetes Deployment

**Input**: Design documents from `phase4-k8/specs/features/`
**Prerequisites**: plan.md (required), kubernetes-deployment.md (spec)

**Tests**: Tests are NOT included for this infrastructure deployment phase.

**Organization**: Tasks are grouped by implementation phase as defined in the spec.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Helm Chart**: `helm-chart/` directory at phase4-k8 root
- **Kubernetes Templates**: `helm-chart/templates/`
- **Documentation**: `phase4-k8/` root
- **Phase 3 Sources**: `../phase3-chatbot/frontend/` and `../phase3-chatbot/`

---

## Phase 1: Setup (Environment & Infrastructure)

**Purpose**: Initialize and verify Kubernetes environment

- [ ] T001 Verify Minikube installation: `minikube version`
- [ ] T002 Verify Helm installation: `helm version`
- [ ] T003 Verify Docker Desktop: `docker --version`
- [ ] T004 Verify kubectl: `kubectl version --client`
- [ ] T005 Start Minikube cluster with docker driver: `minikube start --driver=docker --memory=4096 --cpus=2`
- [ ] T006 Enable Minikube ingress addon: `minikube addons enable ingress`
- [ ] T007 Enable Minikube metrics-server addon: `minikube addons enable metrics-server`
- [ ] T008 Verify Minikube addons: `minikube addons list`
- [ ] T009 Verify storage classes: `kubectl get storageclass`
- [ ] T010 Verify ingress controller: `kubectl get pods -n ingress-nginx`
- [ ] T011 Verify ingress class: `kubectl get ingressclass`
- [ ] T012 Test Docker AI Agent (Gordon) availability: `docker ai "What can you do?"` (if available)
- [ ] T013 Test kubectl-ai availability: `kubectl-ai "check cluster status"` (if available)
- [ ] T014 Test kagent availability: `kagent --help` (if available)
- [ ] T015 Document available AIOps tools and fallback strategies in `history/phr/phr-YYYY-MM-DD-aiops-tools.md`

**Checkpoint**: Environment ready - Minikube running, addons enabled, AIOps tools documented

---

## Phase 2: Foundational (Containerization)

**Purpose**: Create and test Docker images for frontend and backend

**⚠️ CRITICAL**: This phase MUST be complete before Helm chart creation can begin

- [ ] T016 [P] Explore `../phase3-chatbot/frontend/` directory structure
- [ ] T017 [P] Explore `../phase3-chatbot/backend/` directory structure
- [ ] T018 [P] Review Phase 3 frontend package.json build scripts
- [ ] T019 [P] Review Phase 3 backend requirements.txt and dependencies
- [ ] T020 Analyze database architecture: Examine `../phase3-chatbot/app/database/__init__.py` and `../phase3-chatbot/app/main.py`
- [ ] T021 [P] Review Phase 3 environment variables in `.env` files
- [ ] T022 Document Phase 3 structure and requirements in `history/phr/phr-YYYY-MM-DD-phase3-structure.md`
- [ ] T023 Create database architecture ADR: Document PostgreSQL vs file storage decision in `history/adr/adr-YYYY-MM-DD-database-architecture.md`
- [ ] T024 Create frontend Dockerfile in `../phase3-chatbot/frontend/Dockerfile` (multi-stage: Node.js build + Nginx production, port 80)
- [ ] T025 Build frontend Docker image: `cd ../phase3-chatbot/frontend && docker build -t todo-chatbot-frontend:latest .`
- [ ] T026 Test frontend Docker image: `docker run -p 8080:80 todo-chatbot-frontend:latest`
- [ ] T027 Load frontend image into Minikube: `minikube image load todo-chatbot-frontend:latest`
- [ ] T028 Create backend Dockerfile in `../phase3-chatbot/Dockerfile` (Python 3.13, FastAPI, port 8001, health check `/health`)
- [ ] T029 Build backend Docker image: `cd ../phase3-chatbot && docker build -t todo-chatbot-backend:latest .`
- [ ] T030 Test backend Docker image: `docker run -p 8001:8001 todo-chatbot-backend:latest`
- [ ] T031 Verify backend health endpoint: `curl http://localhost:8001/health`
- [ ] T032 Load backend image into Minikube: `minikube image load todo-chatbot-backend:latest`
- [ ] T033 Verify images in Minikube: `minikube image ls | grep todo-chatbot`
- [ ] T034 Document Dockerfile creation process in PHR

**Checkpoint**: Images built, tested, and loaded into Minikube - Ready for Helm chart creation

---

## Phase 3: Helm Chart Creation

**Purpose**: Create complete Helm chart structure with all Kubernetes resources

- [ ] T035 Create Helm chart directory: `mkdir -p helm-chart/templates`
- [ ] T036 Create Chart.yaml in `helm-chart/Chart.yaml` with metadata (name: todo-chatbot, version: 0.1.0)
- [ ] T037 Create initial values.yaml in `helm-chart/values.yaml` with structure
- [ ] T038 [P] Create frontend deployment template in `helm-chart/templates/frontend-deployment.yaml` (port 80, resource limits, liveness/readiness probes)
- [ ] T039 [P] Create frontend service template in `helm-chart/templates/frontend-service.yaml` (ClusterIP, port 80)
- [ ] T040 [P] Create backend deployment template in `helm-chart/templates/backend-deployment.yaml` (port 8001, resource limits, health check `/health`)
- [ ] T041 [P] Create backend service template in `helm-chart/templates/backend-service.yaml` (ClusterIP, port 8001)
- [ ] T042 Create backend ConfigMap template in `helm-chart/templates/backend-configmap.yaml` (non-sensitive env vars: logging config, rate limiting)
- [ ] T043 Create backend Secret template in `helm-chart/templates/backend-secret.yaml` (sensitive: OPENAI_API_KEY, BETTER_AUTH_SECRET, DATABASE_PASSWORD)
- [ ] T044 Create PostgreSQL StatefulSet template in `helm-chart/templates/postgres-statefulset.yaml` (if PostgreSQL used per T023 decision)
- [ ] T045 Create PostgreSQL service template in `helm-chart/templates/postgres-service.yaml` (if PostgreSQL used per T023 decision)
- [ ] T046 [P] Create PVC for PostgreSQL storage in `helm-chart/templates/postgres-pvc.yaml` (if PostgreSQL used per T023 decision)
- [ ] T047 Create Ingress template in `helm-chart/templates/ingress.yaml` (ingress class from T011, host: todo.local, routes: `/` → frontend, `/api/` → backend port 8001)
- [ ] T048 Update values.yaml in `helm-chart/values.yaml` with all configurable parameters (global image settings, frontend/backend configs, PostgreSQL config if used, ingress config)
- [ ] T049 Add comprehensive comments to values.yaml in `helm-chart/values.yaml`
- [ ] T050 Set sensible defaults for local Minikube in `helm-chart/values.yaml`
- [ ] T051 Document secret setup requirements in `helm-chart/values.yaml` comments
- [ ] T052 Run Helm lint: `helm lint ./helm-chart`
- [ ] T053 Render Helm templates: `helm template todo-app ./helm-chart`
- [ ] T054 Dry-run Helm install: `helm install --dry-run --debug todo-app ./helm-chart`
- [ ] T055 Fix any Helm lint warnings or errors
- [ ] T056 Verify all Kubernetes resources in rendered manifests

**Checkpoint**: Helm chart validated - Ready for deployment

---

## Phase 4: Deployment

**Purpose**: Deploy Helm chart to Minikube cluster

- [ ] T057 Validate storage classes: `kubectl get storageclass`
- [ ] T058 Validate ingress class: `kubectl get ingressclass`
- [ ] T059 Verify node resources: `kubectl describe nodes`
- [ ] T060 Confirm images in Minikube: `minikube image ls | grep todo-chatbot`
- [ ] T061 Create secret with OpenAI API key: `kubectl create secret generic openai-secret --from-literal=OPENAI_API_KEY=sk-...` (or use `helm install --set`)
- [ ] T062 Install Helm chart: `helm install todo-app ./helm-chart` (with secret parameter if needed)
- [ ] T063 Check Helm installation status: `helm list`
- [ ] T064 Watch pods deployment: `kubectl get pods -w` (wait until all Running)
- [ ] T065 Verify all pods Running: `kubectl get pods`
- [ ] T066 Verify all services have endpoints: `kubectl get svc`
- [ ] T067 Verify ingress created: `kubectl get ingress`
- [ ] T068 Describe any failing pods: `kubectl describe pod <pod-name>` (if any failed)
- [ ] T069 Get Minikube IP: `minikube ip`
- [ ] T070 Add hosts entry: Edit `/etc/hosts` or `C:\Windows\System32\drivers\etc\hosts` with `<minikube-ip> todo.local`
- [ ] T071 Test DNS resolution: `ping todo.local`
- [ ] T072 Test HTTP connection: `curl -v http://todo.local`

**Checkpoint**: Application deployed and accessible

---

## Phase 5: Validation & Testing

**Purpose**: Verify application functionality and cluster health

- [ ] T073 Access frontend application: Open `http://todo.local` in browser
- [ ] T074 Verify frontend page loads successfully
- [ ] T075 Check browser console for frontend errors
- [ ] T076 Test backend health endpoint: `curl http://todo.local/api/health`
- [ ] T077 Verify backend responds on port 8001 (via Ingress)
- [ ] T078 Check resource usage: `kubectl top pods`
- [ ] T079 [P] View frontend pod logs: `kubectl logs -f deployment/todo-app-frontend`
- [ ] T080 [P] View backend pod logs: `kubectl logs -f deployment/todo-app-backend`
- [ ] T081 [P] View PostgreSQL pod logs: `kubectl logs -f statefulset/todo-app-postgres` (if PostgreSQL used)
- [ ] T082 Verify no critical errors in pod logs
- [ ] T083 Test user authentication flow: Navigate to `http://todo.local/login`, attempt login
- [ ] T084 Test todo operations: Create, list, update, complete, delete todos
- [ ] T085 Test chatbot functionality: Send chat message, verify AI response (if Phase III features available)
- [ ] T086 Check browser network tab for API call success
- [ ] T087 Verify no CORS errors in browser console
- [ ] T088 Create test task via application
- [ ] T089 Note task ID and details
- [ ] T090 Restart database pod: `kubectl delete pod <postgres-pod>` (if PostgreSQL used)
- [ ] T091 Restart backend pod: `kubectl delete pod <l app=todo-app-backend` (if file storage used)
- [ ] T092 Wait for new pod to start
- [ ] T093 Verify test task persists after restart
- [ ] T094 Test frontend-backend communication: Verify all API calls succeed
- [ ] T095 Test error handling: Invalid API requests, network failures
- [ ] T096 Verify logging format in all pods
- [ ] T097 Check page load performance
- [ ] T098 Check API response performance
- [ ] T099 Verify resource usage stable over time
- [ ] T100 Document all validation test results in PHR

**Checkpoint**: Application fully functional and validated

---

## Phase 6: Documentation & Cleanup

**Purpose**: Complete documentation and record all artifacts

- [ ] T101 Create README.md in `phase4-k8/README.md` with setup instructions
- [ ] T102 Document deployment process in `phase4-k8/README.md`
- [ ] T103 Document access method in `phase4-k8/README.md`
- [ ] T104 Add troubleshooting section to `phase4-k8/README.md`
- [ ] T105 Document environment variable setup in `phase4-k8/README.md`
- [ ] T106 Include helm command examples in `phase4-k8/README.md`
- [ ] T107 Create TROUBLESHOOTING.md in `phase4-k8/TROUBLESHOOTING.md`
- [ ] T108 Document pods not starting issues in `phase4-k8/TROUBLESHOOTING.md`
- [ ] T109 Document ingress not working issues in `phase4-k8/TROUBLESHOOTING.md`
- [ ] T110 Document database connection issues in `phase4-k8/TROUBLESHOOTING.md`
- [ ] T111 Document port mismatch issues in `phase4-k8/TROUBLESHOOTING.md`
- [ ] T112 Document storage issues in `phase4-k8/TROUBLESHOOTING.md`
- [ ] T113 Create Helm chart README in `helm-chart/README.md`
- [ ] T114 Add chart overview to `helm-chart/README.md`
- [ ] T115 Add prerequisites to `helm-chart/README.md`
- [ ] T116 Add installation instructions to `helm-chart/README.md`
- [ ] T117 Add configuration values documentation to `helm-chart/README.md`
- [ ] T118 Add upgrade/uninstall commands to `helm-chart/README.md`
- [ ] T119 Add troubleshooting reference to `helm-chart/README.md`
- [ ] T120 Review all prompts used during implementation
- [ ] T121 Create PHR for environment setup issues in `history/phr/`
- [ ] T122 Create PHR for Dockerfile creation issues in `history/phr/`
- [ ] T123 Create PHR for Helm chart issues in `history/phr/`
- [ ] T124 Create PHR for deployment issues in `history/phr/`
- [ ] T125 Create PHR for validation issues in `history/phr/`
- [ ] T126 Store all prompt history in `history/prompts/`
- [ ] T127 Create ADR for Helm chart structure in `history/adr/adr-YYYY-MM-DD-helm-chart-structure.md`
- [ ] T128 Create ADR for resource allocation strategy in `history/adr/adr-YYYY-MM-DD-resource-allocation.md`
- [ ] T129 Create ADR for ingress configuration in `history/adr/adr-YYYY-MM-DD-ingress-configuration.md`
- [ ] T130 Verify all PHRs follow template format
- [ ] T131 Verify all ADRs follow standard format
- [ ] T132 Verify documentation is complete and accurate

**Checkpoint**: All documentation complete, all decisions recorded

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS Helm chart creation
- **Helm Chart (Phase 3)**: Depends on Foundational completion - BLOCKS deployment
- **Deployment (Phase 4)**: Depends on Helm Chart completion - BLOCKS validation
- **Validation (Phase 5)**: Depends on Deployment completion - BLOCKS documentation
- **Documentation (Phase 6)**: Depends on Validation completion - FINAL phase

### Critical Path

1. **Phase 1 (T001-T015)**: Environment must be setup before any work can begin
2. **Phase 2 (T016-T034)**: Images must exist before Helm chart creation can start
   - T023 (database analysis) is CRITICAL for determining PostgreSQL requirements
3. **Phase 3 (T035-T056)**: Helm chart must be created and validated before deployment
   - T044-T046 (PostgreSQL) are CONDITIONAL based on T023 decision
4. **Phase 4 (T057-T072)**: Pre-deployment validation (T057-T060) must pass before install (T062)
5. **Phase 5 (T073-T100)**: Application must be deployed before validation
6. **Phase 6 (T101-T132)**: All phases must complete before documentation

### Parallel Opportunities

**Phase 1 (Setup)**:
- T001-T004 can run in parallel (tool version checks)
- T009-T011 can run in parallel (resource verification)
- T012-T014 can run in parallel (AIOps tool checks)

**Phase 2 (Containerization)**:
- T016-T019 can run in parallel (directory exploration)
- T024-T027 are sequential (frontend)
- T028-T032 are sequential (backend)
- T024 (frontend) and T028 (backend) can run in parallel after T016-T019

**Phase 3 (Helm Chart)**:
- T038-T041 (frontend/backend deployments and services) can run in parallel
- T044-T046 (PostgreSQL) are parallel (but conditional)

**Phase 5 (Validation)**:
- T079-T081 (log viewing) can run in parallel
- T083-T087 (user flow tests) are sequential
- T094-T099 (integration/performance tests) can run in parallel

**Phase 6 (Documentation)**:
- T101-T106 (README) and T107-T112 (TROUBLESHOOTING) can run in parallel
- T113-T118 (Helm README) can run in parallel with above

### Conditional Tasks

**PostgreSQL-related tasks** (T044-T046, T081, T090):
- Execute ONLY if T023 decision is "use PostgreSQL"
- Skip if T023 decision is "use file storage"
- Must document decision in ADR (T023)

---

## Parallel Example: Phase 3 Helm Chart Creation

```bash
# Launch all frontend/backend resources together:
Task: "Create frontend deployment template in helm-chart/templates/frontend-deployment.yaml"
Task: "Create frontend service template in helm-chart/templates/frontend-service.yaml"
Task: "Create backend deployment template in helm-chart/templates/backend-deployment.yaml"
Task: "Create backend service template in helm-chart/templates/backend-service.yaml"

# These can all run in parallel since they target different files with no dependencies
```

---

## Implementation Strategy

### Full Deployment (Complete Feature)

1. **Complete Phase 1** - Environment setup (T001-T015)
2. **Complete Phase 2** - Containerization (T016-T034)
3. **Complete Phase 3** - Helm chart creation (T035-T056)
4. **Complete Phase 4** - Deployment (T057-T072)
5. **Complete Phase 5** - Validation (T073-T100)
6. **Complete Phase 6** - Documentation (T101-T132)

### Checkpoint Strategy

1. **After Phase 1**: Minikube running, addons enabled, AIOps tools documented
2. **After Phase 2**: Images built, tested, loaded into Minikube
3. **After Phase 3**: Helm chart validated (lint passes, dry-run succeeds)
4. **After Phase 4**: Application deployed and accessible at http://todo.local
5. **After Phase 5**: All features working, data persistence verified
6. **After Phase 6**: Documentation complete, all decisions recorded

### Risk Mitigation

| Task | Risk | Mitigation |
|------|------|------------|
| T012-T014 | AIOps tools unavailable | Document fallback strategies in T015 |
| T023 | Database architecture unclear | Thorough analysis, create ADR |
| T024, T028 | Dockerfile creation issues | Use Gordon or Claude fallback, document in PHR |
| T044-T046 | PostgreSQL not needed | Conditional on T023 decision, skip if file storage |
| T062 | Helm install fails | Pre-deployment validation (T057-T060), check logs |
| T070 | DNS/ingress issues | Verify ingress controller (T010), check hosts file |
| T083-T093 | Data persistence issues | Test restart scenarios, document results |

---

## Notes

- [P] tasks = different files, no dependencies
- All tasks follow strict format: `- [ ] [TaskID] [P?] Description with file path`
- T023 (database architecture) is a CRITICAL decision point
- T044-T046, T081, T090 are CONDITIONAL based on T023 decision
- Backend port MUST be 8001 (not 8000) throughout
- OPENAI_API_KEY is CRITICAL and must be in Secret (T043, T061)
- Verify tests fail before implementing (not applicable for infrastructure phase)
- Commit after each task or logical group
- Stop at any checkpoint to validate progress
- Create PHR for every significant issue
- Create ADR for every architectural decision
- All PHRs go to `history/phr/`, prompts to `history/prompts/`, ADRs to `history/adr/`
