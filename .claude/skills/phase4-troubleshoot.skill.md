---
name: phase4-troubleshoot
description: Interactive troubleshooting guide for Phase 4 Kubernetes deployment (Minikube, Helm, Docker).
---

# Phase 4 Troubleshooting Assistant

This skill guides the user through debugging Kubernetes deployment issues for the Todo Chatbot application.

## Workflow

1.  **Analyze Symptoms**:
    - If the user provides an error message, analyze it.
    - If not, ask: "What specific issue are you facing? (e.g., Pods not starting, Can't access via browser, Database connection error, Minikube issues)"
    - Categorize the issue into: Environment, Docker Images, Helm, Pods, Networking, Ingress, or Database.

2.  **Select Troubleshooting Path**:

    ### A. Environment & Minikube
    - **Symptom**: Minikube won't start, driver errors, docker daemon not running.
    - **Diagnose**: `minikube status`, `docker ps`, `docker info`
    - **Solutions**:
      - Start Docker Desktop/Daemon.
      - Check driver permissions.
      - Reset Minikube: `minikube delete` && `minikube start --driver=docker`.

    ### B. Docker Images (ImagePullBackOff)
    - **Symptom**: Pod status `ImagePullBackOff`, `ErrImagePull`.
    - **Diagnose**: `minikube image ls | grep todo`
    - **Solutions**:
      - Build and load images: `cd phase4-k8/docker && ./build.sh`
      - Manually load: `minikube image load todo-chatbot-backend:latest`
      - Verify `values.yaml` image pull policy is `Never` (for local) or `IfNotPresent`.

    ### C. Helm Deployment Fails
    - **Symptom**: "INSTALLATION FAILED", "UPGRADE FAILED".
    - **Diagnose**: `helm list`, `helm history todo-app`
    - **Solutions**:
      - Lint chart: `helm lint phase4-k8/helm-chart`
      - Uninstall/Reinstall: `helm uninstall todo-app` then install.
      - Check for missing secrets or invalid YAML in `values.yaml`.

    ### D. Pod Issues (CrashLoopBackOff / Pending)
    - **Symptom**: Pods restarting or stuck in Pending.
    - **Diagnose**:
      - `kubectl get pods`
      - `kubectl logs <pod-name>`
      - `kubectl describe pod <pod-name>`
    - **Solutions**:
      - **CrashLoop**: Check env vars (Secrets), DB connection strings, application logs.
      - **Pending**: Check resources (CPU/Mem), assume Minikube needs more memory (`minikube start --memory=8192`).
      - **OOMKilled**: Increase memory limits in `values.yaml`.

    ### E. Service & Networking
    - **Symptom**: Service has no endpoints, connection refused.
    - **Diagnose**: `kubectl get svc`, `kubectl get endpoints`
    - **Solutions**:
      - Check Selector labels match Pod labels.
      - Verify Pod is Running.

    ### F. Ingress & Access
    - **Symptom**: `todo.local` not reachable, 404 Not Found.
    - **Diagnose**: `kubectl get ingress`, `kubectl get pods -n ingress-nginx`
    - **Solutions**:
      - Enable ingress addon: `minikube addons enable ingress`
      - Update hosts file: `echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts`
      - Test with direct IP: `curl -H "Host: todo.local" http://$(minikube ip)`

    ### G. Database Connection
    - **Symptom**: Backend logs "could not connect to database".
    - **Diagnose**: `kubectl logs statefulset/todo-app-postgres`
    - **Solutions**:
      - Check Secret `database-url`.
      - Check SSL mode (`sslmode=require`).
      - Test connection from inside pod with `psql` or `curl`.

3.  **Execution**:
    - Ask the user for permission before running diagnostic commands.
    - Interpret the output for the user.
    - Suggest the specific fix based on `phase4-k8/TROUBLESHOOTING.md`.

## Reference
This skill is based on `phase4-k8/TROUBLESHOOTING.md`. Refer to that file for complete details.


