# Kubernetes Setup Script - kurbeScript.ps1
# This script starts a Kubernetes cluster, verifies it's running, and retrieves available pods

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Kubernetes Cluster Setup Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if minikube is installed
Write-Host "Checking if minikube is installed..." -ForegroundColor Yellow
try {
    $minikubeVersion = minikube version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ minikube is installed" -ForegroundColor Green
        Write-Host $minikubeVersion
    } else {
        throw "minikube not found"
    }
} catch {
    Write-Host "Error: minikube is not installed." -ForegroundColor Red
    Write-Host "Please install minikube from: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installation command for Windows (using Chocolatey):" -ForegroundColor Yellow
    Write-Host "  choco install minikube" -ForegroundColor White
    Write-Host ""
    Write-Host "Or download the installer from the minikube website." -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if kubectl is installed
Write-Host "Checking if kubectl is installed..." -ForegroundColor Yellow
try {
    $kubectlVersion = kubectl version --client 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ kubectl is installed" -ForegroundColor Green
        Write-Host $kubectlVersion
    } else {
        throw "kubectl not found"
    }
} catch {
    Write-Host "Error: kubectl is not installed." -ForegroundColor Red
    Write-Host "Please install kubectl from: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installation command for Windows (using Chocolatey):" -ForegroundColor Yellow
    Write-Host "  choco install kubernetes-cli" -ForegroundColor White
    Write-Host ""
    Write-Host "Or download the binary from the Kubernetes website." -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Start minikube cluster
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting Kubernetes cluster with minikube..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
minikube start

# Check if minikube started successfully
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start minikube cluster" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Wait a moment for the cluster to stabilize
Write-Host "Waiting for cluster to stabilize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host ""

# Verify cluster is running
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verifying cluster is running..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl cluster-info

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cluster verification failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Get cluster status
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Minikube Status:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
minikube status
Write-Host ""

# Retrieve available pods in all namespaces
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Retrieving available pods in all namespaces..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl get pods --all-namespaces

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Retrieving pods in default namespace..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl get pods

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Cluster Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  - kubectl get nodes          : View cluster nodes" -ForegroundColor White
Write-Host "  - kubectl get pods           : View pods in default namespace" -ForegroundColor White
Write-Host "  - kubectl get pods -A        : View pods in all namespaces" -ForegroundColor White
Write-Host "  - kubectl get services       : View services" -ForegroundColor White
Write-Host "  - minikube dashboard         : Open Kubernetes dashboard" -ForegroundColor White
Write-Host "  - minikube stop              : Stop the cluster" -ForegroundColor White
Write-Host "  - minikube delete            : Delete the cluster" -ForegroundColor White
Write-Host ""
