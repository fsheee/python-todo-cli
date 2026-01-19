---
Date: 2025-01-03
Topic: Phase 1 tool installation guide
Feature: phase4-k8
Stage: tasks
---

## PROMPT

User Request: "install minikube and helm"

Context:
- Phase 1 setup verification revealed Minikube and Helm are not installed
- Docker v26.1.4 and kubectl v1.29.2 are already available
- User is on Windows system
- Need installation guide for both Minikube and Helm

Command: Manual installation request (not /sp.tasks)

Expected Output:
- Provide clear installation instructions for Minikube and Helm on Windows
- Include multiple installation methods (Chocolatey, Scoop, winget, manual)
- Provide verification commands
- Document PATH setup if needed
- Include troubleshooting section

---

## RESPONSE

Created comprehensive installation guide: `phase4-k8/INSTALL_TOOLS.md`

### Installation Methods Provided

#### Minikube Installation (4 options)
1. **Windows Installer** (Recommended)
   - Download: `https://github.com/kubernetes/minikube/releases/latest/download/minikube-installer.exe`
   - Run as Administrator
   - Verify with: `minikube version`

2. **Chocolatey**: `choco install minikube`
3. **Scoop**: `scoop install minikube`
4. **winget**: `winget install Kubernetes.minikube`

#### Helm Installation (5 options)
1. **Chocolatey** (Recommended): `choco install kubernetes-helm`
2. **Scoop**: `scoop install helm`
3. **winget**: `winget install Kubernetes.helm`
4. **MSI Installer**: Download and run MSI from GitHub
5. **Binary**: Download and add to PATH

### Quick Installation Commands

**With Chocolatey** (most reliable):
```powershell
choco install minikube kubernetes-helm -y
```

**With Scoop**:
```powershell
scoop install minikube helm
```

**With winget**:
```powershell
winget install Kubernetes.minikube Kubernetes.helm
```

### PATH Configuration

If commands are still not found after installation:
1. Open Environment Variables (Win + R → "env")
2. Edit "Path" variable
3. Add paths:
   - Minikube: `C:\Program Files\Kubernetes\minikube`
   - Helm: `C:\Program Files\Helm` or custom location
4. Restart terminal

### Verification Steps

After installation, verify all tools:
```powershell
minikube version
helm version
docker --version
kubectl version --client
```

### Post-Installation Next Steps

Once tools are installed and verified, continue with Phase 1 tasks:
```powershell
# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify installation
minikube addons list
```

### Troubleshooting Included

Guide includes solutions for:
- Command not found after installation
- Permission denied errors
- Docker Desktop not detected
- Virtualization not enabled in BIOS

### Alternative Approaches

If Minikube installation fails:
1. Use Docker Compose for local deployment (simpler)
2. Use Docker directly for manual pod management
3. Skip to cloud Kubernetes (if cloud access available)
4. Document decision in ADR

### File Created

**Output**: `phase4-k8/INSTALL_TOOLS.md`
**Status**: ✅ Installation guide complete
**Next**: User should install tools, then continue with T005 (Start Minikube cluster)

---

## Recommendations

1. **Best Method for Windows**: Chocolatey (most reliable)
2. **Alternative**: Scoop or winget if Chocolatey not available
3. **Fallback**: Manual installer or MSI binary download
4. **Critical**: Verify installation with version commands before proceeding
5. **Note**: Docker Desktop must be running before starting Minikube

---

## Impact on Phase 1 Tasks

**Before installation** (T001-T004):
- ❌ T001: Minikube not found
- ❌ T002: Helm not found
- ✅ T003: Docker verified
- ✅ T004: kubectl verified

**After installation** (should complete T001-T004):
- ✅ T001: `minikube version` succeeds
- ✅ T002: `helm version` succeeds
- ✅ T003: Docker already verified
- ✅ T004: kubectl already verified

Then proceed to T005-T015 (Minikube setup, addons, and AIOps tools)
