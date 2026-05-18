# Phase IV: Local Kubernetes Deployment (Minikube + Helm)

## Overview

Deploy the Phase III chatbot system on a local Kubernetes cluster using Minikube and Helm.

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

## Phase IV Directory Structure

```
phase4-k8/
├── helm/
│   └── gordon/                        # Helm chart (actual deployed chart)
│       ├── Chart.yaml                 # Helm chart metadata
│       ├── values.yaml                # Default configuration values
│       ├── secrets.example.yaml       # Example secrets file (copy to secrets.yaml)
│       ├── README.md                  # Chart documentation
│       └── templates/
│           ├── frontend-deployment.yaml    # Frontend deployment with env vars
│           ├── frontend-service.yaml       # Frontend service
│           ├── backend-deployment.yaml     # Backend deployment
│           ├── backend-service.yaml        # Backend service
│           ├── backend-configmap.yaml      # Backend environment variables
│           ├── backend-secret.yaml         # Sensitive credentials
│           ├── ingress.yaml                # NGINX ingress configuration
│           ├── serviceaccount.yaml         # Service account
│           ├── _helpers.tpl                # Template helpers
│           └── tests/
│               └── test-connection.yaml    # Connection test
├── docker/                              # Dockerfile and build scripts
│   ├── backend-phase3.Dockerfile         # Backend (Python 3.13, port 8002)
│   ├── frontend.Dockerfile               # Frontend (Next.js, Node 20, port 80)
│   ├── build.sh                         # Build script
│   └── README.md
├── README.md                # Setup and deployment instructions
├── CLAUDE.md               # This file
```

## Prerequisites

1. **Minikube**: Local Kubernetes cluster
   ```bash
   minikube version
   # Install if needed: https://minikube.sigs.k8s.io/docs/start/
   ```

2. **Helm**: Package manager for Kubernetes
   ```bash
   helm version
   # Install if needed: https://helm.sh/docs/intro/install/
   ```

3. **Docker**: Container runtime
   ```bash
   docker --version
   ```

4. **Kubectl**: Kubernetes CLI
   ```bash
   kubectl version --client
   ```

## Setup Instructions

### 1. Start Minikube

Start Minikube with Docker driver and required addons:

```bash
# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify addons
minikube addons list
```

### 2. Build Docker Images

Use the Phase 4 Dockerfiles to build images from Phase 3 source:

```bash
# From the repo root, build backend
docker build -f phase4-k8/docker/backend-phase3.Dockerfile \
  -t todo-chatbot-backend:latest phase3-chatbot/backend

# Build frontend
docker build -f phase4-k8/docker/frontend.Dockerfile \
  -t todo-chatbot-frontend:latest phase3-chatbot/frontend

# Load images into Minikube
minikube image load todo-chatbot-frontend:latest
minikube image load todo-chatbot-backend:latest
```

Or use the automated build script:
```bash
cd phase4-k8
./docker/build.sh
```

### 3. Configure Secrets

Copy the example secrets file and fill in your values:

```bash
cd phase4-k8/helm/gordon
cp secrets.example.yaml secrets.yaml
# Edit secrets.yaml with your API keys and database URL
```

**NEVER commit `secrets.yaml` to version control.**

### 4. Install Helm Chart

```bash
# Install with secrets
helm install todo-app ./helm/gordon -f ./helm/gordon/secrets.yaml

# Or install with --set flags
helm install todo-app ./helm/gordon \
  --set backend.secrets.openRouterApiKey="sk-or-v1-..." \
  --set backend.secrets.databaseUrl="postgresql+asyncpg://..."

# Check installation status
helm list
```

Upgrade or uninstall:

```bash
helm upgrade todo-app ./helm/gordon -f ./helm/gordon/secrets.yaml
helm uninstall todo-app
```

Alternatively, push to a registry (Docker Hub, local registry, etc.):

```bash
# Tag and push to registry
docker tag todo-chatbot-frontend:latest your-registry/todo-chatbot-frontend:latest
docker tag todo-chatbot-backend:latest your-registry/todo-chatbot-backend:latest

docker push your-registry/todo-chatbot-frontend:latest
docker push your-registry/todo-chatbot-backend:latest
```

### 3. Configure Helm Chart

Edit `values.yaml` to match your image repository:

```yaml
# values.yaml
image:
  registry: ""  # Empty for Minikube local images, or your registry
  pullPolicy: IfNotPresent

frontend:
  image:
    repository: todo-chatbot-frontend
    tag: latest
  replicas: 1
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"

backend:
  image:
    repository: todo-chatbot-backend
    tag: latest
  replicas: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  env:
    # Configure your OpenAI API key
    OPENAI_API_KEY: "your-openai-api-key-here"

postgres:
  image:
    repository: postgres
    tag: 16-alpine
  storage:
    size: 1Gi
    storageClass: "standard"
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

ingress:
  enabled: true
  className: "nginx"
  host: "todo.local"
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
```

### 4. Install Helm Chart

```bash
# Navigate to Phase 4 directory
cd ../../phase4-k8

# Install the chart
helm install todo-app ./helm-chart

# Check installation status
helm list
```

If the chart is already installed:

```bash
# Upgrade the chart
helm upgrade todo-app ./helm-chart

# Or uninstall and reinstall
helm uninstall todo-app
helm install todo-app ./helm-chart
```

### 5. Verify Deployment

```bash
# Check pods (wait until all are Running)
kubectl get pods

# Check services
kubectl get svc

# Check ingress
kubectl get ingress

# View logs
kubectl logs -f deployment/todo-app-todo-chatbot-frontend
kubectl logs -f deployment/todo-app-todo-chatbot-backend
```

### 6. Access the Application

Add the ingress host to your `/etc/hosts` file (on Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (on Windows):

```
<minikube-ip> todo.local
```

Get the Minikube IP:

```bash
minikube ip
```

Then access the application at:
```
http://todo.local
```

Or use Minikube tunnel (for LoadBalancer services):

```bash
# In a separate terminal
minikube tunnel

# Then get the URL
minikube service todo-app-frontend --url
```

## Helm Chart Components

### Chart.yaml
```yaml
apiVersion: v2
name: todo-chatbot
description: Helm chart for Todo Chatbot application
type: application
version: 0.1.0
appVersion: "1.0.0"
```

### Key Templates

#### Frontend Deployment
- Uses Next.js (Node 20) image
- Exposes port 80 with env vars (NEXT_PUBLIC_API_URL)
- Includes resource limits and requests
- Health checks via liveness and readiness probes

#### Backend Deployment
- Uses FastAPI (Python 3.13) image
- Exposes port 8002
- ConfigMap for environment variables
- Secret for sensitive data (API keys, DB URL, JWT secret)
- Health checks for `/health` endpoint

#### Ingress
- NGINX Ingress Controller
- Route: `/` → frontend, `/api` `/health` `/docs` `/auth` → backend
- Host-based routing for todo.local

## Troubleshooting

### Pods not starting
```bash
# Describe pod to see events
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
```

### Image pull errors
```bash
# Check image exists in Minikube
minikube image ls

# Load image if missing
minikube image load your-image:latest
```

### Ingress not working
```bash
# Check Ingress Controller
kubectl get pods -n ingress-nginx

# Check Ingress resources
kubectl describe ingress todo-app-todo-chatbot

# Verify DNS
curl -v http://todo.local
```

### Database connection issues
```bash
# Check PostgreSQL pod (if in-cluster DB is enabled)
kubectl logs statefulset/todo-app-todo-chatbot-postgres

# Test connection from backend pod
kubectl exec -it <backend-pod> -- sh
# Then: psql -h todo-app-todo-chatbot-postgres -U todo_user -d todo_db
```

## Cleanup

```bash
# Uninstall Helm chart
helm uninstall todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster (careful: this deletes all data)
minikube delete
```

## Next Steps

After successful deployment:
1. Verify all components are working
2. Test the chatbot functionality
3. Monitor resource usage
4. Consider scaling replicas for production
5. Set up monitoring and logging
6. Configure proper secrets management (Vault, Sealed Secrets)

## Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

## Documentation Standards

This project follows spec-driven development with the following documentation artifacts:

### PHR (Problem-Hypothesis-Review)
PHR documents are available for systematic problem analysis:
- Used when encountering complex issues requiring structured analysis
- Format: Problem statement → Hypothesis → Review/Conclusion
- **Storage**: All PHR records are stored in `history/phr/` directory
- **Prompt History**: All user prompts and interactions are stored in `history/prompts/` directory
- **Naming Convention**: `phr-YYYY-MM-DD-[topic].md`
- **Note**: No dedicated skill currently exists - use manual creation

#### PHR History Structure
```
history/
├── phr/
│   ├── phr-2025-01-03-initial-setup.md
│   ├── phr-2025-01-03-docker-image-issues.md
│   ├── TEMPLATE.md
│   └── .gitkeep
└── prompts/
    ├── prompt-2025-01-03-initial-setup.txt
    ├── prompt-2025-01-03-docker-image-issues.txt
    └── .gitkeep
```

### ADR (Architecture Decision Record)
ADR documents are available for recording architectural decisions:
- Used for documenting significant architectural decisions
- Format: Title, Status, Context, Decision, Consequences
- **Storage**: All ADR records are stored in `history/adr/` directory (if created)
- **Naming Convention**: `adr-YYYY-MM-DD-[decision].md`
- **Note**: No dedicated skill currently exists - use manual creation

### Available Skills
Currently available skills in `.claude/skills/`:
- `explaining-code`: Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when user asks "how does this work?"

**Missing Skills**: PHR and ADR generation skills are **NOT** currently available.

### Recommended New Skills for Phase IV

**High Priority** (Would significantly improve workflow):
- **PHR Generation**: Automated creation of Problem-Hypothesis-Review documents
- **ADR Generation**: Automated creation of Architecture Decision Records

**Medium Priority** (Would save time on common tasks):
- **Kubernetes Manifest Generator**: Generate Kubernetes YAML manifests (Deployment, Service, ConfigMap, Secret, StatefulSet, Ingress)
- **Helm Chart Generator**: Generate Helm chart structure with Chart.yaml and templates
- **Helm Values Validator**: Validate and suggest improvements for values.yaml files
- **Kubernetes Troubleshooter**: Diagnose and suggest fixes for Kubernetes pod/service/ingress issues
- **Minikube Assistant**: Help with Minikube setup, configuration, and common operations

**Low Priority** (Nice to have):
- **Docker Image Builder**: Automated Docker build, tag, and push operations
- **Kubernetes Resource Analyzer**: Analyze Kubernetes resource usage and suggest optimizations
- **Ingress Configuration Helper**: Generate and validate NGINX Ingress configurations
- **PersistentVolume Advisor**: Suggest PVC configurations based on storage requirements

### Agents Required for Phase IV

**Available Agents** (built-in to Claude Code):
- `general-purpose`: For complex, multi-step tasks, code research, and execution
- `Explore`: For exploring codebases, finding files, and understanding structure
- `Plan`: For designing implementation plans and architectural strategies

**Recommended Agent Usage for Phase IV**:

| Agent | When to Use |
|-------|-------------|
| `Explore` | Understanding Phase 3 code structure, finding Dockerfiles, examining directory layouts |
| `Plan` | Designing Helm chart structure, planning Kubernetes resources, creating deployment strategies |
| `general-purpose` | Building Docker images, troubleshooting deployment issues, executing multi-step setup tasks |

**When to Use Skills vs Agents**:
- **Skills**: Use for specialized tasks (e.g., `06-explaining-code` to understand Kubernetes YAML)
- **Agents**: Use for autonomous, multi-step work (e.g., exploring codebase and creating deployment plan)

**Skills Status**: PHR and ADR generation skills are **NOT** currently available. If you need these skills, they would need to be created manually or requested as new skill installations.
