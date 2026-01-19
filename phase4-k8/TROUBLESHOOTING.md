# Troubleshooting Guide - Phase 4 Kubernetes Deployment

This guide provides solutions to common issues encountered when deploying and running the Todo Chatbot application on Minikube.

## Table of Contents

1. [Environment Setup Issues](#environment-setup-issues)
2. [Docker Image Issues](#docker-image-issues)
3. [Helm Deployment Issues](#helm-deployment-issues)
4. [Pod Issues](#pod-issues)
5. [Service and Networking Issues](#service-and-networking-issues)
6. [Ingress Issues](#ingress-issues)
7. [Database Connection Issues](#database-connection-issues)
8. [Resource Issues](#resource-issues)
9. [Application Issues](#application-issues)
10. [Common Error Messages](#common-error-messages)

---

## Environment Setup Issues

### Minikube Won't Start

**Symptoms**:
```
minikube start --driver=docker --memory=4096 --cpus=2
❌ Exiting due to DRV_DOCKER_NOT_RUNNING: Docker daemon is not running
```

**Solutions**:

1. **Start Docker Desktop**:
   - Windows: Start Docker Desktop from Start Menu
   - Mac: Start Docker Desktop from Applications
   - Linux: `sudo systemctl start docker`

2. **Verify Docker is running**:
   ```bash
   docker ps
   # Should show running containers or empty list
   ```

3. **Check Docker daemon**:
   ```bash
   docker info
   # Should display Docker system information
   ```

4. **Reset Docker** (if needed):
   - Docker Desktop > Troubleshoot > Reset to Factory Defaults

### Minikube Driver Issues

**Symptoms**:
```
❌ Exiting due to DRV_AS_ROOT: The "docker" driver should not be used with root privileges
```

**Solutions**:

1. **Run without sudo** (Linux):
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker

   # Then start Minikube
   minikube start --driver=docker
   ```

2. **Use different driver**:
   ```bash
   # Try VirtualBox driver
   minikube start --driver=virtualbox

   # Or Hyper-V (Windows)
   minikube start --driver=hyperv
   ```

### Addons Won't Enable

**Symptoms**:
```
minikube addons enable ingress
❌ Error enabling ingress addon
```

**Solutions**:

1. **Wait for Minikube to fully start**:
   ```bash
   minikube status
   # Wait until all components show "Running"
   ```

2. **Check addon status**:
   ```bash
   minikube addons list
   # Look for ingress and metrics-server
   ```

3. **Disable and re-enable**:
   ```bash
   minikube addons disable ingress
   minikube addons enable ingress
   ```

4. **Restart Minikube**:
   ```bash
   minikube stop
   minikube start --driver=docker --memory=4096 --cpus=2
   minikube addons enable ingress
   ```

---

## Docker Image Issues

### ImagePullBackOff Error

**Symptoms**:
```bash
kubectl get pods
NAME                                       READY   STATUS             RESTARTS   AGE
todo-app-backend-xxx                       0/1     ImagePullBackOff   0          2m
```

**Root Cause**: Kubernetes cannot find the Docker image.

**Solutions**:

1. **Verify images exist in Minikube**:
   ```bash
   minikube image ls | grep todo-chatbot
   ```

   Expected:
   ```
   docker.io/library/todo-chatbot-frontend:latest
   docker.io/library/todo-chatbot-backend:latest
   ```

2. **Load images into Minikube**:
   ```bash
   cd phase4-k8/docker
   ./build.sh
   ```

   Or manually:
   ```bash
   minikube image load todo-chatbot-frontend:latest
   minikube image load todo-chatbot-backend:latest
   ```

3. **Verify image pull policy**:
   ```bash
   # In helm/gordon/values.yaml
   image:
     pullPolicy: Never  # For local images
   ```

4. **Check pod events**:
   ```bash
   kubectl describe pod <pod-name> | grep -A 10 Events
   ```

### Image Build Failures

**Symptoms**:
```bash
cd phase4-k8/docker
./build.sh
❌ Backend image build failed
```

**Solutions**:

1. **Check build logs**:
   ```bash
   cat ../logs/backend-build.log
   cat ../logs/frontend-build.log
   ```

2. **Common issues**:

   **Missing dependencies**:
   ```bash
   # Backend: Check requirements.txt
   cd ../../phase2-web/backend
   cat requirements.txt

   # Frontend: Check package.json
   cd ../../phase3-chatbot/frontend
   cat package.json
   ```

   **Out of disk space**:
   ```bash
   docker system df
   # If low, clean up
   docker system prune -a
   ```

   **Network issues**:
   ```bash
   # Test connectivity
   curl -I https://pypi.org
   curl -I https://registry.npmjs.org
   ```

3. **Build manually to debug**:
   ```bash
   # Backend
   cd ../../phase2-web/backend
   docker build -f ../../phase4-k8/docker/backend.Dockerfile -t test-backend .

   # Frontend
   cd ../../phase3-chatbot/frontend
   docker build -f ../../phase4-k8/docker/frontend.Dockerfile -t test-frontend .
   ```

---

## Helm Deployment Issues

### Helm Install Fails

**Symptoms**:
```bash
helm install todo-app helm/gordon
Error: INSTALLATION FAILED: ...
```

**Solutions**:

1. **Lint the chart**:
   ```bash
   helm lint helm/gordon
   # Fix any errors or warnings
   ```

2. **Dry-run to test**:
   ```bash
   helm install --dry-run --debug todo-app helm/gordon
   ```

3. **Check values syntax**:
   ```bash
   # Validate YAML syntax
   python -c "import yaml; yaml.safe_load(open('helm/gordon/values.yaml'))"
   ```

4. **Common issues**:
   - **Missing secrets**: Ensure all required secrets are set
   - **Invalid template**: Check template syntax in `helm/gordon/templates/`
   - **Name conflicts**: Use `helm uninstall todo-app` first

### Helm Upgrade Fails

**Symptoms**:
```bash
helm upgrade todo-app helm/gordon
Error: UPGRADE FAILED: ...
```

**Solutions**:

1. **Check release status**:
   ```bash
   helm list
   helm status todo-app
   ```

2. **Rollback if needed**:
   ```bash
   helm rollback todo-app
   ```

3. **Force upgrade**:
   ```bash
   helm upgrade --force todo-app helm/gordon
   ```

4. **Uninstall and reinstall**:
   ```bash
   helm uninstall todo-app
   helm install todo-app helm/gordon
   ```

---

## Pod Issues

### CrashLoopBackOff

**Symptoms**:
```bash
kubectl get pods
NAME                                       READY   STATUS             RESTARTS   AGE
todo-app-backend-xxx                       0/1     CrashLoopBackOff   5          5m
```

**Root Cause**: Application keeps crashing and restarting.

**Solutions**:

1. **Check logs**:
   ```bash
   kubectl logs <pod-name>
   kubectl logs <pod-name> --previous  # Logs from previous crash
   ```

2. **Common causes**:

   **Missing environment variables**:
   ```bash
   kubectl describe pod <pod-name> | grep -A 20 "Environment:"
   ```

   **Database connection failure**:
   ```bash
   kubectl logs <pod-name> | grep -i database
   kubectl logs <pod-name> | grep -i connection
   ```

   **Port already in use**:
   ```bash
   kubectl logs <pod-name> | grep -i "address already in use"
   ```

3. **Test in Docker locally**:
   ```bash
   # Backend
   docker run -p 8001:8001 todo-chatbot-backend:latest

   # Frontend
   docker run -p 8080:80 todo-chatbot-frontend:latest
   ```

4. **Check health probes**:
   ```yaml
   # In helm/gordon/values.yaml, increase initial delay
   backend:
     livenessProbe:
       initialDelaySeconds: 60  # Increase if app starts slowly
   ```

### Pod Pending

**Symptoms**:
```bash
kubectl get pods
NAME                                       READY   STATUS    RESTARTS   AGE
todo-app-backend-xxx                       0/1     Pending   0          2m
```

**Root Cause**: Kubernetes cannot schedule the pod.

**Solutions**:

1. **Check events**:
   ```bash
   kubectl describe pod <pod-name> | grep -A 10 Events
   ```

2. **Common causes**:

   **Insufficient resources**:
   ```bash
   kubectl describe nodes
   # Look for "Allocated resources" section

   # Solution: Increase Minikube resources
   minikube stop
   minikube start --driver=docker --memory=8192 --cpus=4
   ```

   **PVC not bound** (if using persistent storage):
   ```bash
   kubectl get pvc
   # If status is "Pending", check storage class
   kubectl get storageclass
   ```

3. **Reduce resource requests**:
   ```yaml
   # In helm/gordon/values.yaml
   backend:
     resources:
       requests:
         memory: "128Mi"  # Reduce if needed
         cpu: "50m"
   ```

### Pod OOMKilled

**Symptoms**:
```bash
kubectl get pods
NAME                                       READY   STATUS      RESTARTS   AGE
todo-app-backend-xxx                       0/1     OOMKilled   3          5m
```

**Root Cause**: Pod exceeded memory limit.

**Solutions**:

1. **Check memory usage**:
   ```bash
   kubectl top pod <pod-name>
   ```

2. **Increase memory limit**:
   ```yaml
   # In helm/gordon/values.yaml
   backend:
     resources:
       limits:
         memory: "1Gi"  # Increase from 512Mi
   ```

3. **Check for memory leaks**:
   ```bash
   kubectl logs <pod-name> | grep -i memory
   ```

---

## Service and Networking Issues

### Service Has No Endpoints

**Symptoms**:
```bash
kubectl get endpoints
NAME                                  ENDPOINTS   AGE
todo-app-todo-chatbot-backend         <none>      5m
```

**Root Cause**: Service cannot find matching pods.

**Solutions**:

1. **Check pod labels**:
   ```bash
   kubectl get pods --show-labels
   ```

2. **Check service selector**:
   ```bash
   kubectl describe service todo-app-todo-chatbot-backend | grep Selector
   ```

3. **Verify pod is running**:
   ```bash
   kubectl get pods | grep backend
   # Should show "Running" status
   ```

4. **Check service definition**:
   ```bash
   kubectl get service todo-app-todo-chatbot-backend -o yaml
   ```

### Cannot Connect to Service

**Symptoms**:
```bash
curl http://<service-ip>:<port>
curl: (7) Failed to connect
```

**Solutions**:

1. **Use port-forward to test**:
   ```bash
   kubectl port-forward svc/todo-app-todo-chatbot-backend 8081:8001
   curl http://localhost:8081/health
   ```

2. **Check service type**:
   ```bash
   kubectl get svc
   # Should be ClusterIP for internal services
   ```

3. **Test from within cluster**:
   ```bash
   kubectl run -it --rm debug --image=busybox --restart=Never -- sh
   # Inside pod:
   wget -O- http://todo-app-todo-chatbot-backend:8001/health
   ```

---

## Ingress Issues

### Ingress Not Working

**Symptoms**:
- Cannot access `http://todo.local`
- Browser shows "This site can't be reached"

**Solutions**:

1. **Verify ingress controller is running**:
   ```bash
   kubectl get pods -n ingress-nginx
   ```

   Expected:
   ```
   NAME                                       READY   STATUS    RESTARTS   AGE
   ingress-nginx-controller-xxx               1/1     Running   0          10m
   ```

2. **Check ingress resource**:
   ```bash
   kubectl get ingress
   kubectl describe ingress todo-app-todo-chatbot
   ```

3. **Verify ingress class**:
   ```bash
   kubectl get ingressclass
   # Should show "nginx" class
   ```

4. **Test with Minikube IP directly**:
   ```bash
   curl -H "Host: todo.local" http://$(minikube ip)
   ```

5. **Use port-forward as alternative**:
   ```bash
   # Frontend
   kubectl port-forward svc/todo-app-todo-chatbot-frontend 8080:80

   # Backend
   kubectl port-forward svc/todo-app-todo-chatbot-backend 8081:8001
   ```

### Hosts File Not Working

**Symptoms**:
```bash
ping todo.local
ping: cannot resolve todo.local: Unknown host
```

**Solutions**:

1. **Add to hosts file**:

   **Linux/Mac**:
   ```bash
   echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
   ```

   **Windows (as Administrator)**:
   ```powershell
   Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n$(minikube ip) todo.local"
   ```

2. **Verify entry**:
   ```bash
   # Linux/Mac
   cat /etc/hosts | grep todo.local

   # Windows
   type C:\Windows\System32\drivers\etc\hosts | findstr todo
   ```

3. **Flush DNS cache**:
   ```bash
   # Windows
   ipconfig /flushdns

   # Mac
   sudo dscacheutil -flushcache

   # Linux
   sudo systemd-resolve --flush-caches
   ```

---

## Database Connection Issues

### Backend Cannot Connect to Database

**Symptoms**:
```bash
kubectl logs deployment/todo-app-todo-chatbot-backend
Error: could not connect to database
```

**Solutions**:

1. **Verify database URL secret**:
   ```bash
   kubectl get secret todo-app-todo-chatbot-backend -o jsonpath='{.data.database-url}' | base64 -d
   ```

2. **Test connection from pod**:
   ```bash
   kubectl exec -it deployment/todo-app-todo-chatbot-backend -- sh
   # Inside pod:
   ping ep-xxx.neon.tech
   curl -v https://ep-xxx.neon.tech
   ```

3. **Check Neon database status**:
   - Visit https://console.neon.tech
   - Verify database is not paused
   - Check connection limits

4. **Verify connection string format**:
   ```
   postgresql://user:password@host/dbname?sslmode=require
   ```

5. **Check firewall/network**:
   ```bash
   kubectl run -it --rm debug --image=busybox --restart=Never -- sh
   # Inside pod:
   nslookup ep-xxx.neon.tech
   ```

### SSL/TLS Connection Errors

**Symptoms**:
```
Error: SSL connection has been closed unexpectedly
```

**Solutions**:

1. **Ensure sslmode=require** in connection string:
   ```
   postgresql://...?sslmode=require
   ```

2. **Update PostgreSQL client library**:
   ```bash
   # Check requirements.txt
   psycopg2-binary>=2.9.0
   ```

3. **Test with psql**:
   ```bash
   kubectl exec -it deployment/todo-app-todo-chatbot-backend -- sh
   psql "postgresql://user:password@host/dbname?sslmode=require"
   ```

---

## Resource Issues

### Node Resources Exhausted

**Symptoms**:
```bash
kubectl describe nodes
Allocated resources:
  CPU Requests: 950m (95% of 1000m)
  Memory Requests: 3.8Gi (95% of 4Gi)
```

**Solutions**:

1. **Increase Minikube resources**:
   ```bash
   minikube stop
   minikube start --driver=docker --memory=8192 --cpus=4
   ```

2. **Reduce pod resource requests**:
   ```yaml
   # In helm/gordon/values.yaml
   backend:
     resources:
       requests:
         memory: "128Mi"
         cpu: "50m"
   ```

3. **Delete unused resources**:
   ```bash
   kubectl delete deployment <unused-deployment>
   helm uninstall <unused-release>
   ```

### High CPU Usage

**Symptoms**:
```bash
kubectl top pods
NAME                         CPU    MEMORY
todo-app-backend-xxx         950m   200Mi
```

**Solutions**:

1. **Check application logs**:
   ```bash
   kubectl logs deployment/todo-app-todo-chatbot-backend
   ```

2. **Reduce traffic** (if load testing)

3. **Optimize application code**

4. **Increase CPU limit**:
   ```yaml
   backend:
     resources:
       limits:
         cpu: "1"  # Allow more CPU
   ```

---

## Application Issues

### Frontend Loads But Shows Errors

**Symptoms**:
- Frontend page loads
- Browser console shows API errors
- Network tab shows failed requests

**Solutions**:

1. **Check browser console**:
   - Open DevTools (F12)
   - Look for CORS or network errors

2. **Verify backend health**:
   ```bash
   kubectl port-forward svc/todo-app-todo-chatbot-backend 8081:8001
   curl http://localhost:8081/health
   ```

3. **Check API URL configuration**:
   ```bash
   kubectl logs deployment/todo-app-todo-chatbot-frontend | grep -i api
   ```

4. **Verify CORS settings** in backend

### Authentication Not Working

**Symptoms**:
- Login fails
- JWT token errors
- 401 Unauthorized responses

**Solutions**:

1. **Verify Better Auth secret**:
   ```bash
   kubectl get secret todo-app-todo-chatbot-backend -o jsonpath='{.data.better-auth-secret}' | base64 -d
   ```

2. **Check backend logs**:
   ```bash
   kubectl logs deployment/todo-app-todo-chatbot-backend | grep -i auth
   ```

3. **Test authentication flow**:
   - Clear browser cookies/cache
   - Try different browser
   - Check network tab for token

### AI Chatbot Not Responding

**Symptoms**:
- Chatbot UI loads
- Messages don't get responses
- API calls timeout

**Solutions**:

1. **Verify OpenRouter API key**:
   ```bash
   kubectl get secret todo-app-todo-chatbot-backend -o jsonpath='{.data.openrouter-api-key}' | base64 -d
   ```

2. **Check backend logs for AI errors**:
   ```bash
   kubectl logs deployment/todo-app-todo-chatbot-backend | grep -i openrouter
   kubectl logs deployment/todo-app-todo-chatbot-backend | grep -i agent
   ```

3. **Test API key**:
   ```bash
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer $OPENROUTER_API_KEY"
   ```

4. **Check rate limits or quota**

---

## Common Error Messages

### "Error: failed to create resource"

**Solution**: Chart template error. Run `helm lint helm/gordon` to find syntax issues.

### "Error: rendered manifests contain a resource that already exists"

**Solution**: Resource already exists. Either delete it or use `helm upgrade --force`.

### "Error: YAML parse error"

**Solution**: Invalid YAML syntax in values.yaml. Validate with `yamllint` or online YAML validator.

### "x509: certificate signed by unknown authority"

**Solution**: SSL certificate issue. Add `--set backend.env.SSL_VERIFY=false` for testing (not for production).

### "connection refused"

**Solution**: Service not accessible. Use port-forward or check service/pod status.

### "context deadline exceeded"

**Solution**: Timeout error. Increase timeout or check network connectivity.

---

## Getting More Help

### Useful Commands

```bash
# View all resources
kubectl get all

# Describe resource for details
kubectl describe <resource-type> <resource-name>

# View logs with follow
kubectl logs -f <pod-name>

# Get events sorted by time
kubectl get events --sort-by='.lastTimestamp'

# Debug with interactive shell
kubectl run -it --rm debug --image=busybox --restart=Never -- sh

# Port-forward for testing
kubectl port-forward <pod-name> <local-port>:<pod-port>

# Execute command in pod
kubectl exec -it <pod-name> -- <command>
```

### Log Locations

```
phase4-k8/
├── logs/
│   ├── backend-build.log      # Docker build logs
│   ├── frontend-build.log
│   └── build-status.json      # Build status
└── history/
    ├── phr/                   # Problem-Hypothesis-Review docs
    └── prompts/               # Prompt history
```

### Additional Resources

- [Kubernetes Debugging Docs](https://kubernetes.io/docs/tasks/debug/)
- [Helm Troubleshooting](https://helm.sh/docs/faq/troubleshooting/)
- [Minikube Handbook](https://minikube.sigs.k8s.io/docs/handbook/)
- [NGINX Ingress Troubleshooting](https://kubernetes.github.io/ingress-nginx/troubleshooting/)

---

**Last Updated**: 2026-01-04
