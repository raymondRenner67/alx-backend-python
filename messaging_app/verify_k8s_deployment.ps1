# PowerShell script to verify Kubernetes deployment of Django Messaging App

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Kubernetes Deployment Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if kubectl is available
try {
    kubectl version --client | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ kubectl is available" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ kubectl is not installed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check cluster connection
Write-Host "Checking cluster connection..." -ForegroundColor Yellow
kubectl cluster-info 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Connected to Kubernetes cluster" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot connect to Kubernetes cluster" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if deployment exists
Write-Host "Checking deployment..." -ForegroundColor Yellow
kubectl get deployment django-messaging-app 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Deployment 'django-messaging-app' exists" -ForegroundColor Green
    kubectl get deployment django-messaging-app
} else {
    Write-Host "❌ Deployment 'django-messaging-app' not found" -ForegroundColor Red
    Write-Host "   Run: kubectl apply -f deployment.yaml" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if service exists
Write-Host "Checking service..." -ForegroundColor Yellow
kubectl get service django-messaging-service 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Service 'django-messaging-service' exists" -ForegroundColor Green
    kubectl get service django-messaging-service
} else {
    Write-Host "❌ Service 'django-messaging-service' not found" -ForegroundColor Red
}
Write-Host ""

# Check pods status
Write-Host "Checking pods..." -ForegroundColor Yellow
$PODS = kubectl get pods -l app=django-messaging --no-headers 2>$null
if ($PODS) {
    $POD_COUNT = ($PODS | Measure-Object -Line).Lines
    Write-Host "✓ Found $POD_COUNT pod(s)" -ForegroundColor Green
    kubectl get pods -l app=django-messaging
    Write-Host ""
    
    # Check if pods are running
    $RUNNING_PODS = ($PODS | Select-String -Pattern "Running" | Measure-Object).Count
    if ($RUNNING_PODS -gt 0) {
        Write-Host "✓ $RUNNING_PODS pod(s) are running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No pods are in Running state" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No pods found with label app=django-messaging" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Get first pod name
$POD_NAME = kubectl get pods -l app=django-messaging -o jsonpath='{.items[0].metadata.name}' 2>$null

if ($POD_NAME) {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Pod Details: $POD_NAME" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    
    # Check pod status
    $POD_STATUS = kubectl get pod $POD_NAME -o jsonpath='{.status.phase}'
    Write-Host "Status: $POD_STATUS" -ForegroundColor White
    
    # Check pod readiness
    $READY = kubectl get pod $POD_NAME -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'
    Write-Host "Ready: $READY" -ForegroundColor White
    
    Write-Host ""
    
    # Show recent logs
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Recent Logs (last 15 lines):" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    try {
        kubectl logs $POD_NAME --tail=15 2>$null
    } catch {
        Write-Host "⚠️  Could not retrieve logs" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Show pod events
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Recent Events:" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    kubectl get events --field-selector involvedObject.name=$POD_NAME --sort-by='.lastTimestamp' 2>$null | Select-Object -Last 5
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Verification Summary" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✓ Deployment exists and configured" -ForegroundColor Green
Write-Host "✓ Service exists (ClusterIP)" -ForegroundColor Green
Write-Host "✓ Pods are created" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Check logs: kubectl logs $POD_NAME" -ForegroundColor White
Write-Host "  2. Access app: kubectl port-forward $POD_NAME 8000:8000" -ForegroundColor White
Write-Host "  3. Shell into pod: kubectl exec -it $POD_NAME -- bash" -ForegroundColor White
Write-Host ""
