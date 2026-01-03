# Phase IV Spec: Kubernetes Deployment

## Objective

Deploy the Phase III Todo Chatbot application on a local Kubernetes cluster using Minikube and Helm Charts.

## Development Approach

Use Agentic Dev Stack workflow:
1. **Write spec** → This document
2. **Generate plan** → Break into implementation tasks
3. **Implement** → Execute via Claude Code + AI agents

**Rule**: No manual coding allowed. All YAML manifests and Docker configurations must be generated via:
- Docker AI Agent (Gordon) - for Docker operations
- kubectl-ai - for Kubernetes operations
- kagent - for advanced cluster management
- Claude Code - for orchestration and plan generation

---

## Requirements

### Core Requirements

1. **Containerize Applications**
   - Frontend (React app from Phase III)
   - Backend (FastAPI app from Phase III)
   - Use Docker AI Agent (Gordon) for AI-assisted Docker operations

2. **Create Helm Charts**
   - Complete Helm chart structure for deployment
   - Configurable values.yaml for environments
   - All required Kubernetes resources (Deployment, Service, ConfigMap, Secret, StatefulSet, Ingress)

3. **Deploy on Minikube**
   - Local Kubernetes cluster
   - Full application deployment
   - Verify all components are functional

### AIOps Integration

#### Docker AI Agent (Gordon)

Use Gordon for intelligent Docker operations:

```bash
# Enable Gordon (if available)
# Install Docker Desktop 4.53+
# Go to Settings > Beta features > Toggle on

# Example usage:
docker ai "containerize my frontend application"
docker ai "optimize my Docker image for production"
docker ai "create a multi-stage build for backend"
docker ai "What can you do?"  # Check capabilities
```

**Fallback**: If Gordon is unavailable in your region or tier:
- Use standard Docker CLI commands
- Ask Claude Code to generate docker build commands
- Manually write Dockerfiles (approved exception)

#### kubectl-ai

Use kubectl-ai for intelligent Kubernetes operations:

```bash
# Deployment
kubectl-ai "deploy todo frontend with 2 replicas"
kubectl-ai "deploy todo backend with environment variables"

# Troubleshooting
kubectl-ai "check why pods are failing"
kubectl-ai "analyze resource constraints"

# Operations
kubectl-ai "scale backend to handle more load"
kubectl-ai "check ingress configuration"
```

#### kagent

Use kagent for advanced cluster management:

```bash
# Analysis
kagent "analyze cluster health"
kagent "optimize resource allocation"
kagent "identify bottlenecks in my deployment"
```

**Recommendation**: Start with kubectl-ai for day-to-day operations. Layer in kagent for advanced analysis.

---

## Technology Stack

| Component        | Technology                     |
|-----------------|-------------------------------|
| Container Runtime| Docker (Docker Desktop)        |
| Docker AI       | Docker AI Agent (Gordon)       |
| Orchestration   | Kubernetes (Minikube)          |
| Package Manager  | Helm Charts                    |
| AI DevOps       | kubectl-ai, kagent            |
| Application     | Phase III Todo Chatbot         |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                         │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Frontend Pod   │  │  Backend Pod    │                   │
│  │  (React App)    │  │  (FastAPI)      │                   │
│  │                 │  │                 │                   │
│  │  Service:       │  │  Service:       │                   │
│  │  frontend-svc   │  │  backend-svc    │                   │
│  │  Port: 80       │  │  Port: 8000     │                   │
│  └─────────────────┘  └─────────────────┘                   │
│          │                   │                                │
│          └─────────┬─────────┘                                │
│                    ▼                                         │
│         ┌────────────────────┐                              │
│         │   Ingress (NGINX)  │                              │
│         │  Host: todo.local   │                              │
│         └────────────────────┘                              │
│                    │                                         │
│                    ▼                                         │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ PostgreSQL Pod  │  │  PVC Storage    │                   │
│  │  (pg:16-alpine) │  │  (Data Volume)  │                   │
│  │                 │  └─────────────────┘                   │
│  │  Service:       │                                        │
│  │  postgres-svc   │                                        │
│  │  Port: 5432     │                                        │
│  └─────────────────┘                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
phase4-k8/
├── helm-chart/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── frontend-deployment.yaml
│       ├── frontend-service.yaml
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       ├── backend-configmap.yaml
│       ├── backend-secret.yaml
│       ├── postgres-statefulset.yaml
│       ├── postgres-service.yaml
│       └── ingress.yaml
├── specs/
│   └── features/
│       └── kubernetes-deployment.md  # This file
├── history/
│   ├── phr/          # Problem-Hypothesis-Review documents
│   └── prompts/      # User prompt history
├── CLAUDE.md         # Constitution
├── README.md          # Setup and deployment guide
└── CONSTITUTION.md    # Architecture principles
```

---

## Implementation Plan

### Phase 1: Environment Setup

**Tasks:**
1. Install and configure Minikube
2. Install Helm
3. Enable Minikube addons (ingress, metrics-server)
4. Verify Docker Desktop is running
5. Enable Docker AI Agent (Gordon) if available

**Acceptance Criteria:**
- `minikube version` returns valid version
- `helm version` returns valid version
- `minikube addons list` shows ingress and metrics-server enabled
- `docker ai "What can you do?"` returns capabilities (if available)

### Phase 2: Containerization

**Tasks:**
1. Explore Phase III directory structure
2. Review existing Dockerfiles (if any)
3. Use Docker AI Agent (Gordon) to containerize:
   - Frontend application
   - Backend application
4. Test Docker images locally
5. Load images into Minikube

**Acceptance Criteria:**
- Frontend Docker image builds successfully
- Backend Docker image builds successfully
- `docker images` shows both images
- Images run successfully with `docker run`
- Images loaded into Minikube

### Phase 3: Helm Chart Creation

**Tasks:**
1. Use kubectl-ai to generate Helm chart structure
2. Create Chart.yaml with proper metadata
3. Create values.yaml with configurable parameters:
   - Image repositories and tags
   - Resource limits and requests
   - Replicas count
   - Environment variables
   - Ingress configuration
   - Database credentials
4. Generate Kubernetes templates:
   - Frontend deployment and service
   - Backend deployment and service
   - Backend ConfigMap and Secret
   - PostgreSQL StatefulSet and service
   - Ingress configuration

**Acceptance Criteria:**
- `helm lint ./helm-chart` passes without warnings
- All templates are valid Kubernetes manifests
- Values.yaml is well-documented
- Helm chart can be installed: `helm install todo-app ./helm-chart`

### Phase 4: Deployment

**Tasks:**
1. Use kubectl-ai to deploy Helm chart
2. Monitor pod deployment status
3. Verify all services are created
4. Verify ingress is configured
5. Test application endpoints

**Acceptance Criteria:**
- All pods are in Running state
- All services have correct endpoints
- Ingress is created and accessible
- Application responds to HTTP requests at `http://todo.local`

### Phase 5: Validation & Testing

**Tasks:**
1. Use kagent to analyze cluster health
2. Test complete user flow:
   - Access frontend
   - Login (if authentication implemented)
   - Create tasks
   - Chat with bot (if Phase III features available)
3. Verify data persistence (restart PostgreSQL pod)
4. Check resource usage

**Acceptance Criteria:**
- User can access and use the application
- All Phase III features work in Kubernetes
- Data persists after PostgreSQL pod restart
- Resource usage is within defined limits
- No errors in pod logs

---

## Constraints & Invariants

### Must Do

- Use Docker AI Agent (Gordon) for containerization
- Use kubectl-ai for Kubernetes operations
- Use kagent for cluster analysis
- Deploy on Minikube (local cluster)
- Use Helm for package management
- Follow PHR and ADR documentation standards

### Must Not Do

- Manually write Dockerfiles (use Gordon or fallback)
- Manually write Kubernetes YAML (use kubectl-ai)
- Deploy to cloud (Minikube only for Phase IV)
- Modify Phase III application code
- Skip Helm chart creation
- Ignore resource limits

### Non-Goals

- Production-ready deployment
- High availability configuration
- Multi-environment support (dev/staging/prod)
- CI/CD pipeline integration
- Advanced monitoring (Prometheus, Grafana)
- Centralized logging (ELK, Loki)
- External secrets management (Vault)
- Backup/restore strategies

---

## Success Criteria

### Primary

- [ ] Application is fully functional in Minikube
- [ ] All components communicate correctly
- [ ] Data persists across pod restarts
- [ ] Helm chart installs and upgrades correctly

### Secondary

- [ ] All AI agents used successfully (Gordon, kubectl-ai, kagent)
- [ ] Documentation is complete and accurate
- [ ] Troubleshooting guide addresses common issues
- [ ] Setup can be completed in under 60 minutes

---

## Risk Mitigation

| Risk                                | Mitigation Strategy                                              |
|-------------------------------------|----------------------------------------------------------------|
| Gordon unavailable in region           | Fallback to standard Docker CLI + Claude Code generation          |
| kubectl-ai/kagent not available       | Use kubectl directly with Claude Code assistance                  |
| Minikube resource constraints         | Configure adequate resources (4GB RAM, 2 CPU cores)              |
| Image pull errors                    | Use `minikube image load` for local images                     |
| Ingress not working                 | Verify Minikube IP in /etc/hosts, check ingress controller pod  |
| PostgreSQL data loss                 | Use StatefulSet + PVC for data persistence                      |

---

## Dependencies

### External Dependencies

- Docker Desktop 4.53+ (for Gordon beta)
- Minikube installed and running
- Helm 3.x installed
- kubectl installed
- Phase III application complete and functional

### Internal Dependencies

- Phase III frontend Dockerfile (or create via Gordon)
- Phase III backend Dockerfile (or create via Gordon)
- Phase III application configuration (OpenAI API key, database URL)

---

## PHR Capture

Every user prompt and interaction must be recorded in:
- `history/prompts/` directory
- Format: `prompt-YYYY-MM-DD-[topic].txt`

Every significant issue encountered must create a PHR:
- Directory: `history/phr/`
- Format: `phr-YYYY-MM-DD-[topic].md`
- Use template: `history/phr/TEMPLATE.md`

---

## Skills & Agents Required

### Available Skills

- `explaining-code`: Explains code with visual diagrams and analogies

### Recommended New Skills

**High Priority:**
- PHR Generation
- ADR Generation

**Medium Priority:**
- Kubernetes Manifest Generator
- Helm Chart Generator
- Helm Values Validator
- Kubernetes Troubleshooter
- Minikube Assistant

**Low Priority:**
- Docker Image Builder
- Kubernetes Resource Analyzer
- Ingress Configuration Helper
- PersistentVolume Advisor

### Available Agents (Claude Code Built-in)

- `general-purpose`: Complex, multi-step tasks, code research, execution
- `Explore`: Exploring codebases, finding files, understanding structure
- `Plan`: Designing implementation plans, architectural strategies

### Agent Usage Recommendations

| Phase     | Agent          | Purpose                                      |
|-----------|----------------|----------------------------------------------|
| Setup     | general-purpose | Install and configure Minikube, Helm, tools |
| Explore   | Explore        | Understand Phase III directory structure        |
| Plan      | Plan           | Design Helm chart structure                   |
| Build     | general-purpose | Build and test Docker images                 |
| Deploy    | general-purpose | Deploy via kubectl-ai, verify deployment     |
| Validate  | kagent         | Analyze cluster health, test application      |

---

## Documentation Standards

### Required Documentation

- [ ] README.md - Setup and deployment instructions
- [ ] CLAUDE.md - Constitution and guidelines (✅ created)
- [ ] CONSTITUTION.md - Architecture principles (✅ created)
- [ ] Helm chart documentation (values.yaml comments)

### ADR Documentation

Architecture Decision Records for:
- Helm chart structure decisions
- Resource allocation strategy
- Ingress configuration approach
- PostgreSQL StatefulSet vs Deployment

Create ADRs in `history/adr/` directory (if created)

---

## Next Steps

1. **Review this spec** - Ensure all requirements are understood
2. **Generate implementation plan** - Use Plan agent to create detailed tasks
3. **Execute Phase 1** - Environment setup
4. **Document PHRs** - Record issues and solutions as they arise
5. **Create ADRs** - Document significant architectural decisions
6. **Validate success** - Test and validate each phase

---

**Spec Version**: 1.0
**Phase**: IV - Kubernetes Deployment (Minikube + Helm)
**Date**: 2025-01-03
**Status**: Ready for Implementation
