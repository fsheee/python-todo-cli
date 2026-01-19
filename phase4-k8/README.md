# Phase 4: Kubernetes Deployment with Minikube

## Overview

This phase deploys the Phase 3 Todo Chatbot application to a local Kubernetes cluster using Minikube and Helm. The deployment includes:

- **Frontend**: Next.js React application (Port 80)
- **Backend**: FastAPI Python application with AI agents (Port 8001)
- **Database**: External Neon PostgreSQL (serverless, no in-cluster database)
- **Ingress**: NGINX Ingress Controller for routing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                         │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Frontend Pod   │  │  Backend Pod    │                   │
│  │  (Next.js)      │  │  (FastAPI)      │                   │
│  │  Port: 80       │  │  Port: 8001     │                   │
│  └─────────────────┘  └─────────────────┘                   │
│          │                   │                                │
│          └─────────┬─────────┘                                │
│                    ▼                                         │
│         ┌────────────────────┐                              │
│         │   Ingress (NGINX)  │                              │
│         │  Host: todo.local   │                              │
│         └────────────────────┘                              │
│                    │                                         │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     ▼
              ┌──────────────────┐
              │  Neon PostgreSQL │
              │   (External)     │
              └──────────────────┘
```

## Prerequisites

Before starting, ensure you have the following installed:

### Required Tools

1. **Docker Desktop**: Container runtime
   ```bash
   docker --version
   # Expected: Docker version 20.10+ or higher
   ```

2. **Minikube**: Local Kubernetes cluster
   ```bash
   minikube version
   # Expected: minikube version v1.30+ or higher
   ```

3. **Helm**: Kubernetes package manager
   ```bash
   helm version
   # Expected: version.BuildInfo{Version:"v3.12+"}
   ```

4. **kubectl**: Kubernetes CLI
   ```bash
   kubectl version --client
   # Expected: Client Version: v1.27+ or higher
   ```

### Installation Guides

If you need to install these tools, see [INSTALL_TOOLS.md](./INSTALL_TOOLS.md).

## Quick Start

### 1. Start Minikube

```bash
# Start Minikube with Docker driver (4GB RAM, 2 CPUs)
minikube start --driver=docker --memory=4096 --cpus=2

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify status
minikube status
```

### 2. Build and Load Docker Images

The Docker images are already built and loaded into Minikube. To verify:

```bash
# Check images in Minikube
minikube image ls | grep todo-chatbot
```

Expected output:
```
docker.io/library/todo-chatbot-frontend:latest
docker.io/library/todo-chatbot-backend:latest
```

If images are missing, rebuild them:

```bash
cd phase4-k8/docker
./build.sh
```

### 3. Deploy with Helm

```bash
cd phase4-k8

# Install the Helm chart
helm install todo-app helm/gordon

# Check deployment status
kubectl get pods
kubectl get svc
kubectl get ingress
```

Wait for all pods to reach `Running` status:
```bash
kubectl get pods -w
```

Expected output:
```
NAME                                            READY   STATUS    RESTARTS   AGE
todo-app-todo-chatbot-backend-xxx              1/1     Running   0          2m
todo-app-todo-chatbot-frontend-xxx             1/1     Running   0          2m
```

### 4. Access the Application

#### Option A: Port Forwarding (Recommended for Windows/WSL)

```bash
# Forward frontend (in one terminal)
kubectl port-forward svc/todo-app-todo-chatbot-frontend 8080:80

# Forward backend (in another terminal)
kubectl port-forward svc/todo-app-todo-chatbot-backend 8081:8001
```

Then access:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8081/health
- **API Docs**: http://localhost:8081/docs

#### Option B: Ingress with Hosts File (Linux/Mac)

```bash
# Get Minikube IP
minikube ip
# Output: 192.168.49.2 (example)

# Add to hosts file
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Access application
open http://todo.local
```

#### Option C: Minikube Tunnel (Alternative)

```bash
# Run in a separate terminal (requires admin/sudo)
minikube tunnel

# Access via ingress
curl http://todo.local
```

## Helm Chart Configuration

### Default Configuration

The Helm chart is located at `helm/gordon/` and uses these defaults:

```yaml
# Image configuration
image:
  registry: ""  # Empty for local Minikube images
  pullPolicy: Never

# Frontend
frontend:
  replicaCount: 1
  image:
    repository: todo-chatbot-frontend
    tag: latest
  service:
    port: 80
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"

# Backend
backend:
  replicaCount: 1
  image:
    repository: todo-chatbot-backend
    tag: latest
  service:
    port: 8001
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

# PostgreSQL (External Neon)
postgres:
  enabled: false  # Using external Neon PostgreSQL
```

### Secrets Configuration

The chart requires several secrets to be configured in `helm/gordon/values.yaml`:

```yaml
backend:
  secrets:
    # OpenRouter API key (for AI agent)
    openRouterApiKey: "sk-or-v1-..."

    # Better Auth secret (for JWT validation)
    betterAuthSecret: "your-secret-here"

    # Neon PostgreSQL connection string
    databaseUrl: "postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"

    # Internal service token (for MCP server)
    internalServiceToken: "your-token-here"
```

**⚠️ Security Note**: Never commit secrets to git. Use `.gitignore` or external secret management.

### Customizing the Deployment

To override values:

```bash
# Using --set flags
helm install todo-app helm/gordon \
  --set backend.secrets.openRouterApiKey="your-key-here" \
  --set backend.replicaCount=2

# Using a custom values file
helm install todo-app helm/gordon -f custom-values.yaml
```

## Verification and Testing

### 1. Check Pod Status

```bash
# List all pods
kubectl get pods

# Describe a pod for details
kubectl describe pod <pod-name>

# View pod logs
kubectl logs -f deployment/todo-app-todo-chatbot-frontend
kubectl logs -f deployment/todo-app-todo-chatbot-backend
```

### 2. Check Services

```bash
# List services
kubectl get svc

# Check service endpoints
kubectl get endpoints
```

### 3. Check Ingress

```bash
# List ingress resources
kubectl get ingress

# Describe ingress
kubectl describe ingress todo-app-todo-chatbot
```

### 4. Test Backend Health

```bash
# Via port-forward
kubectl port-forward svc/todo-app-todo-chatbot-backend 8081:8001 &
curl http://localhost:8081/health

# Expected output: {"status":"healthy"}
```

### 5. Test Frontend

```bash
# Via port-forward
kubectl port-forward svc/todo-app-todo-chatbot-frontend 8080:80 &
curl -I http://localhost:8080

# Expected: HTTP/1.1 200 OK
```

### 6. Monitor Resources

```bash
# Check resource usage
kubectl top pods

# Check cluster info
kubectl cluster-info

# Check node resources
kubectl describe nodes
```

## Upgrading the Deployment

### Update Application Code

1. Make changes to Phase 3 code
2. Rebuild Docker images:
   ```bash
   cd phase4-k8/docker
   ./build.sh
   ```
3. Upgrade Helm release:
   ```bash
   helm upgrade todo-app helm/gordon
   ```

### Update Helm Configuration

```bash
# Edit values.yaml, then upgrade
helm upgrade todo-app helm/gordon -f helm/gordon/values.yaml

# Or use --set for quick changes
helm upgrade todo-app helm/gordon \
  --set backend.replicaCount=3
```

## Uninstalling

### Remove Helm Release

```bash
# Uninstall the application
helm uninstall todo-app

# Verify deletion
kubectl get pods
kubectl get svc
kubectl get ingress
```

### Stop Minikube

```bash
# Stop the cluster (preserves data)
minikube stop

# Delete the cluster (removes all data)
minikube delete
```

## Troubleshooting

### Pods Not Starting

**Problem**: Pods stuck in `Pending`, `ImagePullBackOff`, or `CrashLoopBackOff`

**Solutions**:

1. Check pod events:
   ```bash
   kubectl describe pod <pod-name>
   ```

2. Check logs:
   ```bash
   kubectl logs <pod-name>
   ```

3. Common issues:
   - **ImagePullBackOff**: Image not loaded into Minikube
     ```bash
     minikube image load todo-chatbot-frontend:latest
     minikube image load todo-chatbot-backend:latest
     ```

   - **CrashLoopBackOff**: Application error (check logs)
   - **Pending**: Insufficient resources (increase Minikube memory/CPU)

### Ingress Not Working

**Problem**: Cannot access application via `todo.local`

**Solutions**:

1. Verify ingress controller is running:
   ```bash
   kubectl get pods -n ingress-nginx
   ```

2. Check ingress configuration:
   ```bash
   kubectl describe ingress todo-app-todo-chatbot
   ```

3. Use port-forward as alternative:
   ```bash
   kubectl port-forward svc/todo-app-todo-chatbot-frontend 8080:80
   ```

### Database Connection Issues

**Problem**: Backend cannot connect to Neon PostgreSQL

**Solutions**:

1. Verify database URL in backend secret:
   ```bash
   kubectl get secret todo-app-todo-chatbot-backend -o yaml
   ```

2. Test connection from backend pod:
   ```bash
   kubectl exec -it deployment/todo-app-todo-chatbot-backend -- sh
   # Inside pod:
   curl -v https://ep-xxx.neon.tech
   ```

3. Check backend logs for connection errors:
   ```bash
   kubectl logs deployment/todo-app-todo-chatbot-backend | grep -i database
   ```

### High Resource Usage

**Problem**: Pods consuming too much memory/CPU

**Solutions**:

1. Check resource usage:
   ```bash
   kubectl top pods
   ```

2. Adjust resource limits in `values.yaml`:
   ```yaml
   backend:
     resources:
       limits:
         memory: "1Gi"  # Increase if needed
         cpu: "1"
   ```

3. Restart Minikube with more resources:
   ```bash
   minikube stop
   minikube start --driver=docker --memory=8192 --cpus=4
   ```

## Architecture Decisions

This deployment follows several key architectural decisions documented in ADRs:

### ADR-001: External Neon PostgreSQL

**Decision**: Use external Neon PostgreSQL instead of deploying PostgreSQL in Kubernetes.

**Rationale**:
- Consistency with Phase 2 and Phase 3
- Zero operational overhead (managed service)
- Automatic backups and high availability
- No StatefulSet/PVC complexity

**Trade-offs**:
- Requires internet connectivity
- External dependency on Neon
- Slight network latency (<50ms)

See [history/adr/adr-2025-01-04-database-architecture.md](./history/adr/adr-2025-01-04-database-architecture.md) for full details.

## File Structure

```
phase4-k8/
├── README.md                          # This file
├── INSTALL_TOOLS.md                   # Tool installation guide
├── HELM_CHART_SUMMARY.md              # Helm chart documentation
├── CLAUDE.md                          # Phase 4 guide for Claude
├── .specify/
│   └── memory/
│       └── CONSTITUTION.md            # Project constitution
├── docker/
│   ├── backend.Dockerfile             # Backend Docker image
│   ├── frontend.Dockerfile            # Frontend Docker image
│   ├── build.sh                       # Build script
│   └── README.md                      # Docker documentation
├── helm/
│   └── gordon/                        # Helm chart directory
│       ├── Chart.yaml                 # Chart metadata
│       ├── values.yaml                # Default values
│       ├── value.example.yaml         # Example values
│       ├── README.md                  # Chart documentation
│       └── templates/                 # Kubernetes manifests
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── backend-configmap.yaml
│           ├── backend-secret.yaml
│           ├── ingress.yaml
│           ├── serviceaccount.yaml
│           ├── _helpers.tpl
│           ├── NOTES.txt
│           └── tests/
│               └── test-connection.yaml
├── history/
│   ├── adr/                           # Architecture Decision Records
│   ├── phr/                           # Problem-Hypothesis-Review docs
│   └── prompts/                       # Prompt history
├── logs/
│   ├── backend-build.log              # Backend build logs
│   ├── frontend-build.log             # Frontend build logs
│   └── build-status.json              # Build status
└── specs/
    └── features/
        ├── kubernetes-deployment.md   # Feature specification
        ├── plan.md                    # Implementation plan
        └── tasks.md                   # Task breakdown
```

## Next Steps

1. **Test Application Features**:
   - User authentication
   - Todo CRUD operations
   - AI chatbot functionality

2. **Monitor Performance**:
   - Resource usage
   - Response times
   - Error rates

3. **Explore Scaling**:
   - Increase replicas
   - Test load balancing
   - Optimize resources

4. **Production Readiness** (Future):
   - CI/CD pipeline
   - Multi-environment deployment
   - Advanced monitoring (Prometheus/Grafana)
   - Centralized logging (ELK stack)

## Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Neon PostgreSQL](https://neon.tech/docs)

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `kubectl logs <pod-name>`
3. Check pod events: `kubectl describe pod <pod-name>`
4. Review ADRs in `history/adr/`

---

**Phase 4 Status**: ✅ Deployed and Verified

**Last Updated**: 2026-01-04
