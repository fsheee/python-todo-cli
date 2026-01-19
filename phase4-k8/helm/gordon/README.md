# Todo Chatbot Helm Chart

Helm chart for deploying the Todo Chatbot application with AI-powered conversational interface to Kubernetes.

## Overview

This Helm chart deploys:
- **Frontend**: React application (Next.js) on port 80
- **Backend**: FastAPI application with OpenAI/OpenRouter integration on port 8001
- **Database**: Uses external Neon PostgreSQL (serverless) - no database pod deployed
- **Ingress**: NGINX ingress controller for routing

## Prerequisites

- Kubernetes cluster (Minikube for local deployment)
- Helm 3.x installed
- kubectl configured
- Docker images built and loaded into cluster
- Neon PostgreSQL database provisioned
- OpenRouter or OpenAI API key

## Quick Start

### 1. Build and Load Docker Images

```bash
# Navigate to Phase 3 frontend
cd ../../phase3-chatbot/frontend
docker build -t todo-chatbot-frontend:latest .

# Navigate to Phase 3 backend
cd ../
docker build -t todo-chatbot-backend:latest .

# Load images into Minikube (if using Minikube)
minikube image load todo-chatbot-frontend:latest
minikube image load todo-chatbot-backend:latest

# Verify images loaded
minikube image ls | grep todo-chatbot
```

### 2. Configure Secrets

Create a `secrets.yaml` file with your sensitive values:

```yaml
backend:
  secrets:
    # OpenRouter configuration (recommended)
    openRouterApiKey: "sk-or-v1-your-key-here"
    baseUrl: "https://openrouter.ai/api/v1"
    modelName: "mistralai/devstral-2512:free"

    # OR use OpenAI (fallback)
    # openaiApiKey: "sk-your-openai-key-here"

    # Better Auth secret for JWT validation
    betterAuthSecret: "your-better-auth-secret"

    # Neon PostgreSQL connection string
    databaseUrl: "postgresql+asyncpg://user:password@ep-xxx.neon.tech/dbname"

    # Internal service token for MCP server
    internalServiceToken: "your-internal-token"

    # Phase 2 API URL (if needed)
    phase2ApiUrl: "https://your-phase2-api.com"
```

**Important**: Keep `secrets.yaml` secure and add it to `.gitignore`!

### 3. Install the Chart

```bash
# Install with secrets file
helm install todo-app . -f secrets.yaml

# Or install with command-line flags
helm install todo-app . \
  --set backend.secrets.openRouterApiKey="sk-or-v1-..." \
  --set backend.secrets.databaseUrl="postgresql+asyncpg://..." \
  --set backend.secrets.betterAuthSecret="your-secret"
```

### 4. Access the Application

For Minikube:

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Access application
open http://todo.local
```

## Configuration

### Image Configuration

```yaml
image:
  registry: ""  # Empty for Minikube, or your registry URL
  pullPolicy: IfNotPresent
```

### Frontend Configuration

```yaml
frontend:
  enabled: true
  replicaCount: 1
  image:
    repository: todo-chatbot-frontend
    tag: latest
  service:
    type: ClusterIP
    port: 80
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"
```

### Backend Configuration

```yaml
backend:
  enabled: true
  replicaCount: 1
  image:
    repository: todo-chatbot-backend
    tag: latest
  service:
    type: ClusterIP
    port: 8001
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"

  # Non-sensitive environment variables
  env:
    API_HOST: "0.0.0.0"
    API_PORT: "8001"
    LOG_LEVEL: "INFO"
    ENVIRONMENT: "production"
```

### Ingress Configuration

```yaml
ingress:
  enabled: true
  className: "nginx"
  host: "todo.local"
  paths:
    - path: /
      pathType: Prefix
      service: frontend
      port: 80
    - path: /api
      pathType: Prefix
      service: backend
      port: 8001
```

## Database Setup

This chart uses **external Neon PostgreSQL** (serverless). No PostgreSQL pod is deployed in the cluster.

### Neon PostgreSQL Setup

1. Create a Neon project at https://neon.tech
2. Create a database (e.g., `todo_db`)
3. Get the connection string from Neon dashboard
4. Format: `postgresql+asyncpg://user:password@ep-xxx-xxx.neon.tech/dbname`
5. Add to `backend.secrets.databaseUrl` in values

### Why Neon?

- Serverless (auto-scales, pay-per-use)
- No storage management in Kubernetes
- Managed backups and replication
- Production-ready without extra configuration

## Deployment Commands

### Install

```bash
# Install with default values
helm install todo-app .

# Install with custom values
helm install todo-app . -f custom-values.yaml

# Install with secrets
helm install todo-app . -f secrets.yaml

# Dry run to test
helm install todo-app . --dry-run --debug
```

### Upgrade

```bash
# Upgrade deployment
helm upgrade todo-app .

# Upgrade with new values
helm upgrade todo-app . -f secrets.yaml

# Rollback if needed
helm rollback todo-app
```

### Uninstall

```bash
# Remove deployment
helm uninstall todo-app

# Verify removal
kubectl get all
```

## Verification

### Check Deployment Status

```bash
# Watch pods starting
kubectl get pods -w

# Check all resources
kubectl get all

# Check services
kubectl get svc

# Check ingress
kubectl get ingress

# Describe pod for debugging
kubectl describe pod <pod-name>
```

### View Logs

```bash
# Frontend logs
kubectl logs -f deployment/todo-app-todo-chatbot-frontend

# Backend logs
kubectl logs -f deployment/todo-app-todo-chatbot-backend

# Follow logs from all backend pods
kubectl logs -f -l app.kubernetes.io/component=backend
```

### Test Endpoints

```bash
# Test backend health
curl http://todo.local/health

# Test backend API docs
curl http://todo.local/docs

# Test frontend
curl http://todo.local/
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod to see events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

**Common issues:**
- Image pull errors: Ensure images are loaded into Minikube
- CrashLoopBackOff: Check environment variables and secrets
- Pending: Check resource limits and node capacity

### Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress

# Verify DNS
ping todo.local

# Check if host is in /etc/hosts
cat /etc/hosts | grep todo.local
```

### Database Connection Issues

```bash
# Test database connection from backend pod
kubectl exec -it <backend-pod> -- sh
# Inside pod:
python -c "import asyncpg; print('asyncpg installed')"

# Check DATABASE_URL secret
kubectl get secret todo-app-todo-chatbot-backend-secret -o yaml
```

**Common issues:**
- Connection refused: Verify Neon database is accessible from Kubernetes
- Authentication failed: Check database credentials in secret
- SSL errors: Ensure connection string includes SSL parameters

### Missing Environment Variables

```bash
# Check ConfigMap
kubectl get configmap todo-app-todo-chatbot-backend-config -o yaml

# Check Secret (decoded)
kubectl get secret todo-app-todo-chatbot-backend-secret -o jsonpath='{.data}' | jq 'map_values(@base64d)'
```

## Security Best Practices

1. **Never commit secrets to Git**
   - Add `secrets.yaml` to `.gitignore`
   - Use external secret management (Vault, Sealed Secrets) for production

2. **Use separate secrets per environment**
   - Different API keys for dev/staging/prod
   - Rotate secrets regularly

3. **Limit resource access**
   - Use RBAC for service accounts
   - Restrict ingress to specific IPs if needed

4. **Enable TLS/HTTPS**
   - Use cert-manager for automatic certificate management
   - Configure TLS in ingress

## Advanced Configuration

### Enable Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Add TLS/HTTPS

```yaml
ingress:
  tls:
    - secretName: todo-chatbot-tls
      hosts:
        - todo.local
```

### Custom Resource Limits

```yaml
backend:
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

## Development

### Helm Lint

```bash
# Lint chart
helm lint .

# Validate templates
helm template todo-app . | kubectl apply --dry-run=client -f -
```

### Template Rendering

```bash
# Render all templates
helm template todo-app .

# Render specific template
helm template todo-app . -s templates/backend-deployment.yaml

# Debug with values
helm template todo-app . -f secrets.yaml --debug
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/hackathon-todo/issues
- Documentation: See `../CLAUDE.md` for architecture details

## License

See project LICENSE file.
