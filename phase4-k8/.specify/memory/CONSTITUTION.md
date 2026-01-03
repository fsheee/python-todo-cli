# Phase IV Constitution: Local Kubernetes Deployment (Minikube + Helm)

## Constitution Objectives

This constitution defines the architectural principles, constraints, and guidelines for deploying the Phase III chatbot system on a local Kubernetes cluster using Minikube and Helm.

## Architectural Principles

### 1. Simplicity First
- The deployment must be straightforward and reproducible
- Use standard Kubernetes resources (Deployment, Service, ConfigMap, Secret, PVC)
- Avoid complex custom resources or operators
- Follow Minikube best practices for local development

### 2. Resource Efficiency
- Set appropriate resource requests and limits for all containers
- Use resource-efficient base images (Alpine variants where applicable)
- Start with single replicas, design for horizontal scaling later

### 3. Data Persistence
- Use StatefulSet for PostgreSQL with stable network identity
- Use PersistentVolumeClaim for database data storage
- Ensure database data survives pod restarts and node failures

### 4. Observability
- Include health checks (liveness and readiness probes) for all pods
- Use resource limits and requests for monitoring
- Enable basic logging through stdout/stderr

### 5. Security Basics
- Use Kubernetes Secrets for sensitive data (database credentials)
- Use ConfigMaps for non-sensitive configuration
- Follow principle of least privilege for container permissions

## Constraints

### Technology Constraints
- **Kubernetes Distribution**: Minikube (local development cluster)
- **Kubernetes Version**: Compatible with Minikube default version
- **Helm Version**: v3.x (latest stable)
- **Container Runtime**: Docker (Minikube default)

### Architecture Constraints
- **Frontend**: Single React container from Phase 3
- **Backend**: Single FastAPI container from Phase 3
- **Database**: PostgreSQL 16 Alpine (single instance with StatefulSet)
- **Networking**: NGINX Ingress Controller for external access

### Resource Constraints
- **Minimum Minikube Resources**:
  - Memory: 4GB
  - CPU: 2 cores
  - Disk: 20GB
- **Frontend Pod**:
  - Memory Request: 128Mi
  - Memory Limit: 256Mi
  - CPU Request: 100m
  - CPU Limit: 200m
- **Backend Pod**:
  - Memory Request: 256Mi
  - Memory Limit: 512Mi
  - CPU Request: 100m
  - CPU Limit: 500m
- **PostgreSQL Pod**:
  - Memory Request: 256Mi
  - Memory Limit: 512Mi
  - CPU Request: 100m/sp/
  - CPU Limit: 500m
  - Storage: 1Gi

### Networking Constraints
- **Frontend Service**: NodePort or ClusterIP (exposed via Ingress)
- **Backend Service**: ClusterIP (internal only)
- **PostgreSQL Service**: ClusterIP (internal only)
- **Ingress**: NGINX Ingress Controller with host-based routing

### Configuration Constraints
- Use Helm values.yaml for all configurable parameters
- Support both local Minikube images and registry-based images
- Use environment variables for backend configuration
- Use OpenAI API key provided via environment variable

## Mandatory Components

### Helm Chart Structure
```
helm-chart/
├── Chart.yaml                    # Helm chart metadata
├── values.yaml                   # All configurable values
└── templates/
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── backend-configmap.yaml
    ├── backend-secret.yaml
    ├── postgres-statefulset.yaml
    ├── postgres-service.yaml
    └── ingress.yaml
```

### Frontend Deployment Requirements
- Use `todo-chatbot-frontend:latest` image (or configurable)
- Expose port 80
- Set resource requests and limits as defined above
- Include liveness probe: HTTP GET / (initial delay 30s, period 10s)
- Include readiness probe: HTTP GET / (initial delay 5s, period 5s)
- Set image pull policy to IfNotPresent for local development

### Backend Deployment Requirements
- Use `todo-chatbot-backend:latest` image (or configurable)
- Expose port 8000
- Set resource requests and limits as defined above
- Include liveness probe: HTTP GET /health (initial delay 30s, period 10s)
- Include readiness probe: HTTP GET /health (initial delay 5s, period 5s)
- Load environment variables from ConfigMap
- Load secrets from Secret
- Set DATABASE_URL environment variable
- Set OPENAI_API_KEY environment variable

### Backend ConfigMap Requirements
- Non-sensitive environment variables
- Service URLs (e.g., DATABASE_URL connection string without password)
- Application configuration settings

### Backend Secret Requirements
- Database password
- Any other sensitive credentials (if added)

### PostgreSQL StatefulSet Requirements
- Use `postgres:16-alpine` image
- Expose port 5432
- Set resource requests and limits as defined above
- Create PersistentVolumeClaim with 1Gi storage
- Use PostgreSQL environment variables:
  - POSTGRES_DB: todo_db
  - POSTGRES_USER: todo_user
  - POSTGRES_PASSWORD: loaded from Secret
- Set stable network identity (serviceName)
- Include liveness probe: TCP socket 5432 (initial delay 30s, period 10s)
- Include readiness probe: TCP socket 5432 (initial delay 5s, period 5s)

### Ingress Requirements
- Use NGINX Ingress Controller class
- Set host-based routing for `todo.local`
- Route `/` path to frontend service
- Route `/api/` path to backend service
- Include rewrite-target annotation if needed
- Enable TLS (optional for local development)

## Implementation Guidelines

### Helm Best Practices
- Use Helm template functions for conditional logic
- Use Helm helper functions (tpl, default, required) where appropriate
- Make all configurable parameters available in values.yaml
- Include meaningful labels and annotations on all resources
- Use semantic versioning for chart version

### Kubernetes Best Practices
- Use appropriate Kubernetes API versions
- Include resource metadata (labels, annotations)
- Set appropriate restart policies
- Use proper selectors for Services
- Follow naming conventions (lowercase, hyphens)

### Security Best Practices
- Use non-root user in containers (if supported by images)
- Set appropriate security contexts
- Use Secrets for sensitive data
- Avoid hardcoding credentials in values.yaml
- Document security assumptions

### Local Development Considerations
- Support Minikube local images (set `image.registry: ""` in values.yaml)
- Use Minikube image loading for local builds
- Provide instructions for both local and registry-based deployments
- Document host file changes for Ingress access

## Validation Criteria

### Functional Validation
- [ ] Frontend is accessible via Ingress host
- [ ] Backend API is accessible via Ingress host
- [ ] Frontend can communicate with backend
- [ ] Backend can connect to PostgreSQL
- [ ] Chatbot functionality works end-to-end
- [ ] User authentication works (if implemented in Phase 3)

### Infrastructure Validation
- [ ] All pods are in Running state
- [ ] All services have correct endpoints
- [ ] Ingress is created and routes traffic correctly
- [ ] PVC is bound and mounted to PostgreSQL
- [ ] Database data persists after pod restart
- [ ] Health checks are passing for all pods

### Resource Validation
- [ ] Resource requests are set for all containers
- [ ] Resource limits are set for all containers
- [ ] Pods are not OOMKilled
- [ ] Resource usage is within limits

### Helm Validation
- [ ] Helm chart installs without errors
- [ ] Helm chart upgrades without errors
- [ ] Helm chart uninstalls cleanly
- [ ] Helm template renders valid Kubernetes manifests
- [ ] Helm lint passes without warnings

## Testing Requirements

### Unit Testing (Optional)
- Helm template tests using `helm test`
- Kubernetes resource validation using kubeval or similar

### Integration Testing
- Manual testing of all user flows
- Verify chatbot responds to queries
- Verify authentication (if applicable)
- Test database persistence by restarting pods

### Load Testing (Optional)
- Test with multiple concurrent users
- Verify resource limits prevent runaway containers
- Verify application handles load gracefully

## Documentation Requirements

### Required Documentation
- [ ] README.md with setup instructions
- [ ] Prerequisites (Minikube, Helm, Docker, kubectl)
- [ ] Step-by-step deployment guide
- [ ] Troubleshooting section with common issues
- [ ] Cleanup instructions
- [ ] Architecture diagram
- [ ] Helm chart documentation (values.yaml structure)

### Architecture Documentation
- Component diagram showing all Kubernetes resources
- Network diagram showing service connectivity
- Data flow diagram showing request path
- Storage diagram showing PVC usage

## Non-Requirements (Out of Scope)

### Not Required for Phase IV
- Production-ready deployment (CI/CD, production cluster)
- High availability (multiple replicas, multi-node)
- Advanced monitoring (Prometheus, Grafana)
- Centralized logging (ELK stack, Loki)
- Advanced security (NetworkPolicies, PodSecurityPolicies)
- Secret management external tools (Vault, Sealed Secrets)
- Service mesh (Istio, Linkerd)
- Autoscaling (HPA, VPA)
- Backup/restore strategies
- Disaster recovery procedures

### Future Considerations (Not Now)
- Multi-environment deployments (dev, staging, prod)
- Multiple ingress hosts/routes
- SSL/TLS certificate management
- External secrets integration
- Advanced observability features
- Canary deployments or blue-green deployments

## Success Metrics

### Primary Success Metrics
- Application is fully functional in Minikube
- All components communicate correctly
- Data persists correctly
- Helm chart installs, upgrades, and uninstalls without errors
- User can access application via Ingress

### Secondary Success Metrics
- Documentation is clear and comprehensive
- Troubleshooting guide addresses common issues
- Setup can be completed in under 30 minutes
- Resource usage stays within defined limits
- No critical security vulnerabilities

## Constraints on Implementation

### What Must Be Done
- Create complete Helm chart with all mandatory templates
- Deploy Phase 3 images to Minikube
- Configure all components to work together
- Create comprehensive documentation
- Test end-to-end functionality

### What Must Not Be Done
- Do not modify Phase 3 code or images
- Do not add new features to the application
- Do not implement production-level security
- Do not implement high availability features
- Do not create complex custom resources
- Do not use advanced Kubernetes features (beyond scope)
- Do not implement CI/CD pipelines

### Decision Points to Be Made
- Registry strategy (local Minikube images vs external registry)
- Ingress host name (default: todo.local)
- Storage class for PVC (default: standard)
- Database credentials (hardcoded in values.yaml for demo vs Secret only)
- Health check timing (can be adjusted based on application startup time)

## Constitution Version

- **Version**: 1.0
- **Phase**: IV - Local Kubernetes Deployment (Minikube + Helm)
- **Last Updated**: 2025-01-03
- **Approver**: Specification from "Hackathon II - Todo Spec-Driven Development.pdf"

## Adherence Checklist

Before completing Phase IV, ensure:

- [ ] All mandatory components are implemented
- [ ] All constraints are respected
- [ ] All validation criteria are met
- [ ] All documentation requirements are satisfied
- [ ] Non-requirements are not implemented
- [ ] Success metrics are achieved
- [ ] Constitution is followed throughout implementation

---

**Note**: This constitution must be followed during the entire implementation of Phase IV. Any deviations must be documented and justified. The constitution serves as the single source of truth for architectural decisions and implementation boundaries.
