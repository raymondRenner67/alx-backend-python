# Kubernetes Setup Script - kurbeScript

This directory contains scripts to set up and verify a local Kubernetes cluster using minikube.

## Files

- `kurbeScript` - Bash script for Linux/Mac
- `kurbeScript.ps1` - PowerShell script for Windows

## Prerequisites

Before running the script, you need to install:

1. **minikube** - Local Kubernetes cluster
2. **kubectl** - Kubernetes command-line tool

### Installation on Windows

#### Option 1: Using Chocolatey (Recommended)

```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install minikube
choco install minikube

# Install kubectl
choco install kubernetes-cli
```

#### Option 2: Manual Installation

**minikube:**
1. Download the latest minikube installer from: https://minikube.sigs.k8s.io/docs/start/
2. Run the installer
3. Add minikube to your PATH

**kubectl:**
1. Download kubectl from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
2. Add kubectl.exe to your PATH

### Installation on Linux

```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### Installation on macOS

```bash
# Using Homebrew
brew install minikube
brew install kubectl
```

## Usage

### On Windows (PowerShell)

```powershell
# Navigate to the directory
cd c:\Users\Latitude7480\Downloads\pf\alx-backend-python\messaging_app

# Run the PowerShell script
.\kurbeScript.ps1
```

### On Linux/Mac (Bash)

```bash
# Navigate to the directory
cd messaging_app

# Make the script executable
chmod +x kurbeScript

# Run the script
./kurbeScript
```

## What the Script Does

1. **Checks Prerequisites**: Verifies that minikube and kubectl are installed
2. **Starts Cluster**: Launches a local Kubernetes cluster using minikube
3. **Verifies Cluster**: Runs `kubectl cluster-info` to confirm the cluster is running
4. **Retrieves Pods**: Lists all available pods in all namespaces
5. **Shows Status**: Displays minikube status and cluster information

## Expected Output

The script will display:
- minikube and kubectl version information
- Cluster startup progress
- Cluster information (API server, CoreDNS endpoints)
- Minikube status
- List of pods in all namespaces
- List of pods in the default namespace
- Helpful commands for managing the cluster

## Common Issues

### Issue: Virtualization not enabled

**Error**: "minikube start" fails with virtualization error

**Solution**: 
- Enable virtualization in BIOS/UEFI settings
- Or use Docker driver: `minikube start --driver=docker`

### Issue: Docker not running

**Error**: "minikube start" fails because Docker is not running

**Solution**: 
- Start Docker Desktop
- Or use a different driver: `minikube start --driver=hyperv` (Windows) or `minikube start --driver=virtualbox`

### Issue: Insufficient resources

**Error**: Cluster fails to start due to resource constraints

**Solution**: 
```bash
minikube start --cpus=2 --memory=2048
```

## Useful Commands

After the cluster is running, you can use these commands:

```bash
# View cluster nodes
kubectl get nodes

# View all pods
kubectl get pods -A

# View services
kubectl get services

# Open Kubernetes dashboard
minikube dashboard

# Stop the cluster
minikube stop

# Delete the cluster
minikube delete

# SSH into the minikube VM
minikube ssh
```

## Troubleshooting

If the script fails:

1. Check that minikube and kubectl are properly installed:
   ```bash
   minikube version
   kubectl version --client
   ```

2. Check minikube status:
   ```bash
   minikube status
   ```

3. View minikube logs:
   ```bash
   minikube logs
   ```

4. Delete and recreate the cluster:
   ```bash
   minikube delete
   minikube start
   ```

## Additional Resources

- [minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [kubectl Documentation](https://kubernetes.io/docs/reference/kubectl/)
- [Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
