# PowerShell Script for Blue-Green Deployment of Django Messaging App
# This script deploys both blue and green versions and checks for errors

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Blue-Green Deployment Script" -ForegroundColor Cyan
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

# Function to check deployment status
function Check-DeploymentStatus {
    param (
        [string]$DeploymentName,
        [string]$Version
    )
    
    Write-Host "Checking $Version deployment status..." -ForegroundColor Yellow
    kubectl rollout status deployment/$DeploymentName --timeout=120s
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $Version deployment is ready" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ $Version deployment failed" -ForegroundColor Red
        return $false
    }
}

# Function to check logs for errors
function Check-LogsForErrors {
    param (
        [string]$Version
    )
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Checking $Version deployment logs for errors..." -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    
    # Get pod names for the version
    $PODS = kubectl get pods -l app=django-messaging,version=$Version -o jsonpath='{.items[*].metadata.name}'
    
    if (-not $PODS) {
        Write-Host "⚠️  No pods found for $Version deployment" -ForegroundColor Yellow
        return $false
    }
    
    $errorFound = $false
    
    foreach ($POD in $PODS -split ' ') {
        Write-Host ""
        Write-Host "Checking logs for pod: $POD" -ForegroundColor Yellow
        Write-Host "------------------------------------------"
        
        # Get logs and check for errors
        $logs = kubectl logs $POD --tail=100 2>$null
        $errorLines = $logs | Select-String -Pattern "error|exception|failed|fatal|critical" -CaseSensitive:$false
        
        if ($errorLines) {
            $errorCount = ($errorLines | Measure-Object).Count
            Write-Host "⚠️  Found $errorCount potential error(s) in logs:" -ForegroundColor Yellow
            $errorLines | ForEach-Object { Write-Host $_.Line -ForegroundColor Red }
            $errorFound = $true
        } else {
            Write-Host "✓ No critical errors found in recent logs" -ForegroundColor Green
        }
        
        # Display last few lines of logs
        Write-Host ""
        Write-Host "Recent logs (last 10 lines):" -ForegroundColor Yellow
        kubectl logs $POD --tail=10
    }
    
    return -not $errorFound
}

# Step 1: Deploy Blue version (current stable version)
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 1: Deploying Blue Version (Stable)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl apply -f blue_deployment.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to deploy blue version" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Blue deployment applied" -ForegroundColor Green
Write-Host ""

# Wait for blue deployment to be ready
$blueStatus = Check-DeploymentStatus -DeploymentName "django-messaging-app-blue" -Version "Blue"

# Step 2: Deploy Green version (new version)
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 2: Deploying Green Version (New)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl apply -f green_deployment.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to deploy green version" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Green deployment applied" -ForegroundColor Green
Write-Host ""

# Wait for green deployment to be ready
$greenStatus = Check-DeploymentStatus -DeploymentName "django-messaging-app-green" -Version "Green"

# Step 3: Apply services
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 3: Applying Kubernetes Services" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl apply -f kubeservice.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to apply services" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Services applied" -ForegroundColor Green
Write-Host ""

# Step 4: Display current state
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 4: Current Deployment State" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployments:" -ForegroundColor Yellow
kubectl get deployments -l app=django-messaging
Write-Host ""
Write-Host "Pods:" -ForegroundColor Yellow
kubectl get pods -l app=django-messaging
Write-Host ""
Write-Host "Services:" -ForegroundColor Yellow
kubectl get services -l app=django-messaging
Write-Host ""

# Step 5: Check logs for errors
$blueLogsStatus = $true
$greenLogsStatus = $true

if ($blueStatus) {
    $blueLogsStatus = Check-LogsForErrors -Version "blue"
}

if ($greenStatus) {
    $greenLogsStatus = Check-LogsForErrors -Version "green"
}

# Final Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment Summary" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

if ($blueStatus) {
    Write-Host "✓ Blue deployment: READY" -ForegroundColor Green
} else {
    Write-Host "✗ Blue deployment: FAILED" -ForegroundColor Red
}

if ($greenStatus) {
    Write-Host "✓ Green deployment: READY" -ForegroundColor Green
} else {
    Write-Host "✗ Green deployment: FAILED" -ForegroundColor Red
}

# Get current service target
$currentVersion = kubectl get service django-messaging-service -o jsonpath='{.spec.selector.version}'
Write-Host ""
Write-Host "Current traffic target: $currentVersion version" -ForegroundColor Yellow
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test the green deployment:" -ForegroundColor Yellow
Write-Host "  kubectl port-forward service/django-messaging-green 8001:8000" -ForegroundColor White
Write-Host "  # Then access: http://localhost:8001" -ForegroundColor White
Write-Host ""
Write-Host "To switch traffic to green version:" -ForegroundColor Yellow
Write-Host "  kubectl patch service django-messaging-service -p '{`"spec`":{`"selector`":{`"version`":`"green`"}}}'" -ForegroundColor White
Write-Host ""
Write-Host "To rollback to blue version:" -ForegroundColor Yellow
Write-Host "  kubectl patch service django-messaging-service -p '{`"spec`":{`"selector`":{`"version`":`"blue`"}}}'" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  kubectl logs -l app=django-messaging,version=blue" -ForegroundColor White
Write-Host "  kubectl logs -l app=django-messaging,version=green" -ForegroundColor White
Write-Host ""
Write-Host "To delete green deployment (after verifying):" -ForegroundColor Yellow
Write-Host "  kubectl delete -f green_deployment.yaml" -ForegroundColor White
Write-Host ""
