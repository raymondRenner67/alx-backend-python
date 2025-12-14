# PowerShell script to scale Django messaging app deployment to 3 replicas using kubectl

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Scaling Django Messaging App Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if kubectl is available
try {
    kubectl version --client 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ kubectl is available" -ForegroundColor Green
    }
} catch {
    Write-Host "Error: kubectl is not installed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check current deployment status
Write-Host "Current deployment status:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
kubectl get deployment django-messaging-app 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Deployment 'django-messaging-app' not found" -ForegroundColor Red
    Write-Host "Please ensure the deployment exists before scaling" -ForegroundColor Yellow
    Write-Host "Run: kubectl apply -f deployment.yaml" -ForegroundColor White
    exit 1
}
Write-Host ""

# Scale deployment to 3 replicas
Write-Host "Scaling deployment to 3 replicas..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
kubectl scale deployment django-messaging-app --replicas=3

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to scale deployment" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Scale command executed successfully" -ForegroundColor Green
Write-Host ""

# Wait for rollout to complete
Write-Host "Waiting for rollout to complete..." -ForegroundColor Yellow
kubectl rollout status deployment/django-messaging-app --timeout=120s
Write-Host ""

# Display updated deployment status
Write-Host "Updated deployment status:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
kubectl get deployment django-messaging-app
Write-Host ""

# Display pods
Write-Host "Pods after scaling:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
kubectl get pods -l app=django-messaging
Write-Host ""

# Count running pods
$PODS_OUTPUT = kubectl get pods -l app=django-messaging --no-headers 2>$null
if ($PODS_OUTPUT) {
    $RUNNING_PODS = ($PODS_OUTPUT | Select-String -Pattern "Running" | Measure-Object).Count
} else {
    $RUNNING_PODS = 0
}

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Scaling Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✓ Deployment scaled to 3 replicas" -ForegroundColor Green
Write-Host "✓ $RUNNING_PODS pod(s) are currently running" -ForegroundColor Green
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  - kubectl get pods -l app=django-messaging  : View all pods" -ForegroundColor White
Write-Host "  - kubectl scale deployment django-messaging-app --replicas=5 : Scale to 5 replicas" -ForegroundColor White
Write-Host "  - kubectl describe deployment django-messaging-app : View deployment details" -ForegroundColor White
Write-Host ""
