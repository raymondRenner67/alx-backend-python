# PowerShell script to build Docker image and deploy Django Messaging App to Kubernetes

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Django Messaging App - Kubernetes Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build Docker image
Write-Host "Step 1: Building Docker image..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
docker build -t django-messaging-app:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Load image into minikube (if using minikube)
Write-Host "Step 2: Loading image into minikube..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
try {
    $minikubeCheck = minikube version 2>&1
    if ($LASTEXITCODE -eq 0) {
        minikube image load django-messaging-app:latest
        Write-Host "✓ Image loaded into minikube" -ForegroundColor Green
    }
} catch {
    Write-Host "ℹ️  Minikube not detected, skipping image load" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Create namespace (optional)
Write-Host "Step 3: Creating namespace (optional)..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
kubectl create namespace django-app 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ℹ️  Namespace already exists or using default" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Apply Kubernetes manifests
Write-Host "Step 4: Applying Kubernetes deployment..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
kubectl apply -f deployment.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Deployment failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Deployment applied successfully" -ForegroundColor Green
Write-Host ""

# Step 5: Wait for pods to be ready
Write-Host "Step 5: Waiting for pods to be ready..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
kubectl wait --for=condition=ready pod -l app=django-messaging --timeout=120s

Write-Host ""

# Step 6: Display deployment status
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pods:" -ForegroundColor Yellow
kubectl get pods -l app=django-messaging
Write-Host ""
Write-Host "Services:" -ForegroundColor Yellow
kubectl get services -l app=django-messaging
Write-Host ""
Write-Host "Deployments:" -ForegroundColor Yellow
kubectl get deployments -l app=django-messaging
Write-Host ""

# Step 7: Get pod name for logs
$POD_NAME = kubectl get pods -l app=django-messaging -o jsonpath='{.items[0].metadata.name}'

if ($POD_NAME) {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Recent logs from pod: $POD_NAME" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    kubectl logs $POD_NAME --tail=20
    Write-Host ""
    
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  - kubectl get pods                    : View all pods" -ForegroundColor White
    Write-Host "  - kubectl logs $POD_NAME              : View logs" -ForegroundColor White
    Write-Host "  - kubectl describe pod $POD_NAME      : Detailed pod info" -ForegroundColor White
    Write-Host "  - kubectl exec -it $POD_NAME -- bash  : Shell into pod" -ForegroundColor White
    Write-Host "  - kubectl port-forward $POD_NAME 8000:8000 : Access app locally" -ForegroundColor White
    Write-Host "  - kubectl delete -f deployment.yaml   : Remove deployment" -ForegroundColor White
} else {
    Write-Host "Warning: No pods found. Check deployment status with: kubectl get pods" -ForegroundColor Yellow
}
Write-Host ""
