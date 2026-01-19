# Phase 4 Tool Installation Guide

## Prerequisites

- Windows OS
- Administrator privileges (for installation)
- Docker Desktop already installed and running ✅

---

## 1. Install Minikube

### Option 1: Using Windows Installer (Recommended)

1. Download the latest Minikube installer:
   ```
   https://github.com/kubernetes/minikube/releases/latest/download/minikube-installer.exe
   ```

2. Run the installer as Administrator
3. Follow the installation wizard
4. Verify installation:
   ```powershell
   minikube version
   ```

### Option 2: Using Chocolatey

If you have Chocolatey installed:
```powershell
choco install minikube
```

### Option 3: Using Scoop

If you have Scoop installed:
```powershell
scoop install minikube
```

### Option 4: Using winget (Windows Package Manager)

```powershell
winget install Kubernetes.minikube
```

### Verification

After installation, verify:
```powershell
minikube version
```

Expected output:
```
minikube version: v1.34.0
commit: <hash>
```

---

## 2. Install Helm

### Option 1: Using Chocolatey (Recommended)

If you have Chocolatey installed:
```powershell
choco install kubernetes-helm
```

### Option 2: Using Scoop

If you have Scoop installed:
```powershell
scoop install helm
```

### Option 3: Using winget

```powershell
winget install Kubernetes.helm
```

### Option 4: Manual Installation (MSI)

1. Download the latest Helm MSI installer:
   ```
   https://github.com/helm/helm/releases/latest/download/helm-v3.x.x-windows-amd64.msi
   ```

2. Run the installer as Administrator
3. Follow the installation wizard
4. Verify installation:
   ```powershell
   helm version
   ```

### Option 5: Using Binary (No installer required)

1. Download the latest Windows binary:
   ```
   https://get.helm.sh/helm-v3.x.x-windows-amd64.zip
   ```

2. Extract the zip file
3. Add the directory to your PATH:
   ```powershell
   # Add to System Environment Variables
   # Path: C:\path\to\helm
   ```

4. Restart terminal
5. Verify:
   ```powershell
   helm version
   ```

### Verification

After installation, verify:
```powershell
helm version
```

Expected output:
```
version.BuildInfo{Version:"v3.16.1", GitCommit:"...", GoVersion:"go1.22.0"}
```

---

## 3. Add to PATH (if needed)

If commands are still not found after installation:

### Windows PATH Setup

1. Open Environment Variables:
   ```
   Press Win + R → Type "env" → Enter
   ```

2. Edit "Path" variable:
   - Add Minikube path (typically: `C:\Program Files\Kubernetes\minikube`)
   - Add Helm path (typically: `C:\Program Files\Helm` or custom location)

3. Click OK and restart terminal

### Verify PATH

```powershell
$env:Path -split ';' | Select-String -Pattern 'minikube'
$env:Path -split ';' | Select-String -Pattern 'helm'
```

---

## 4. Quick Installation Script (One-liner)

If you have Chocolatey installed, install both at once:

```powershell
choco install minikube kubernetes-helm -y
```

If you have Scoop:

```powershell
scoop install minikube helm
```

If you have winget:

```powershell
winget install Kubernetes.minikube Kubernetes.helm
```

---

## 5. Verify All Tools

After installation, verify all tools:

```powershell
# Check Minikube
minikube version

# Check Helm
helm version

# Check Docker (already verified)
docker --version

# Check kubectl (already verified)
kubectl version --client
```

---

## 6. Post-Installation Steps (Next in Phase 1)

Once tools are installed and verified, continue with:

```powershell
# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify installation
minikube addons list
```

---

## Troubleshooting

### Issue: Command not found after installation

**Solution 1**: Restart terminal
**Solution 2**: Add to PATH (see section 3)
**Solution 3**: Use full path (e.g., `C:\Program Files\Kubernetes\minikube\minikube.exe`)

### Issue: Permission denied

**Solution**: Run terminal as Administrator

### Issue: Docker Desktop not detected

**Solution**: Ensure Docker Desktop is running before starting Minikube

### Issue: Virtualization not enabled

**Solution**: Enable virtualization in BIOS:
- Intel: Intel VT-x
- AMD: AMD-V

---

## Recommended Installation Method

**For Windows users with Chocolatey** (most reliable):
```powershell
# Install Chocolatey first if needed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install tools
choco install minikube kubernetes-helm -y

# Verify
minikube version
helm version
```

---

## Alternative: Quick Start Without Minikube

If Minikube installation is problematic, you can:

1. **Use Docker Compose** for local deployment (simpler setup)
2. **Use Docker directly** for manual pod management
3. **Skip to cloud Kubernetes** (if you have cloud access)

These alternatives are noted in ADR: `adr-YYYY-MM-DD-kubernetes-alternatives.md`

---

**Status**: Installation guide ready
**Next**: After installation, continue with T005 (Start Minikube cluster)
