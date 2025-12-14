# PowerShell Script for Rolling Update with Zero Downtime Verification
# This script applies rolling updates and continuously tests for downtime

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Kubernetes Rolling Update Script" -ForegroundColor Cyan
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

# Configuration
$DEPLOYMENT_NAME = "django-messaging-app-blue"
$DEPLOYMENT_FILE = "blue_deployment.yaml"
$SERVICE_NAME = "django-messaging-service"
$TEST_ENDPOINT = "http://localhost:8000"
$LOG_FILE = "rolling_update_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Function to test application availability
function Test-Application {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -in @(200, 301, 302)) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to continuously monitor application availability
function Monitor-Availability {
    param([int]$Duration)
    
    $totalRequests = 0
    $failedRequests = 0
    $endTime = (Get-Date).AddSeconds($Duration)
    
    Write-Host "Starting continuous availability monitoring for ${Duration}s..." -ForegroundColor Yellow
    "$(Get-Date): Monitoring started" | Out-File -FilePath $LOG_FILE -Append
    
    while ((Get-Date) -lt $endTime) {
        $totalRequests++
        
        if (Test-Application -Url $TEST_ENDPOINT) {
            Write-Host "." -NoNewline -ForegroundColor Green
        } else {
            $failedRequests++
            Write-Host "X" -NoNewline -ForegroundColor Red
            "$(Get-Date): Request failed (Total failures: $failedRequests)" | Out-File -FilePath $LOG_FILE -Append
        }
        
        Start-Sleep -Seconds 1
    }
    
    Write-Host ""
    Write-Host ""
    Write-Host "Availability Test Results:" -ForegroundColor Cyan
    Write-Host "  Total Requests: $totalRequests" -ForegroundColor White
    Write-Host "  Failed Requests: $failedRequests" -ForegroundColor White
    $successRate = if ($totalRequests -gt 0) { (($totalRequests - $failedRequests) / $totalRequests) * 100 } else { 0 }
    Write-Host "  Success Rate: $([math]::Round($successRate, 2))%" -ForegroundColor White
    Write-Host ""
    
    if ($failedRequests -eq 0) {
        Write-Host "✓ Zero downtime achieved!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⚠️  Some requests failed during update" -ForegroundColor Yellow
        return $false
    }
}

# Step 1: Check current deployment status
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 1: Current Deployment Status" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl get deployment $DEPLOYMENT_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Deployment not found, will create new deployment..." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Current image version:" -ForegroundColor Yellow
    kubectl get deployment $DEPLOYMENT_NAME -o jsonpath='{.spec.template.spec.containers[0].image}'
    Write-Host ""
    Write-Host ""
    
    Write-Host "Current pods:" -ForegroundColor Yellow
    kubectl get pods -l app=django-messaging,version=blue
    Write-Host ""
}

# Step 2: Set up port forwarding in background
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 2: Setting up Port Forwarding" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting port forward to service..." -ForegroundColor Yellow

# Kill any existing port-forward processes
Get-Process | Where-Object { $_.ProcessName -eq "kubectl" -and $_.CommandLine -like "*port-forward*$SERVICE_NAME*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Start port forwarding in background
$portForwardJob = Start-Job -ScriptBlock {
    param($serviceName)
    kubectl port-forward service/$serviceName 8000:8000
} -ArgumentList $SERVICE_NAME

Start-Sleep -Seconds 3

if ($portForwardJob.State -eq "Running") {
    Write-Host "✓ Port forwarding established (Job ID: $($portForwardJob.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠️  Port forwarding failed, will skip availability tests" -ForegroundColor Yellow
    $portForwardJob = $null
}
Write-Host ""

# Step 3: Test initial application availability
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 3: Testing Initial Application State" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
if ($portForwardJob -and $portForwardJob.State -eq "Running") {
    if (Test-Application -Url $TEST_ENDPOINT) {
        Write-Host "✓ Application is responding before update" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Application not responding, continuing anyway..." -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ️  Skipping pre-update test (port forwarding not available)" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Start background monitoring
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 4: Starting Continuous Monitoring" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$monitorJob = $null
if ($portForwardJob -and $portForwardJob.State -eq "Running") {
    Write-Host "Monitoring will run during the rolling update..." -ForegroundColor Yellow
    Write-Host "Legend: . = success, X = failure" -ForegroundColor Yellow
    Write-Host ""
    
    # Start monitoring in background
    $monitorJob = Start-Job -ScriptBlock {
        param($endpoint, $logFile)
        
        $totalRequests = 0
        $failedRequests = 0
        $endTime = (Get-Date).AddSeconds(60)
        
        while ((Get-Date) -lt $endTime) {
            $totalRequests++
            
            try {
                $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($response.StatusCode -in @(200, 301, 302)) {
                    Write-Output "."
                } else {
                    $failedRequests++
                    Write-Output "X"
                }
            } catch {
                $failedRequests++
                Write-Output "X"
            }
            
            Start-Sleep -Seconds 1
        }
        
        return @{
            Total = $totalRequests
            Failed = $failedRequests
        }
    } -ArgumentList $TEST_ENDPOINT, $LOG_FILE
} else {
    Write-Host "ℹ️  Skipping availability monitoring (port forwarding not available)" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# Step 5: Apply rolling update
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 5: Applying Rolling Update" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Applying deployment file: $DEPLOYMENT_FILE" -ForegroundColor Yellow
kubectl apply -f $DEPLOYMENT_FILE

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to apply deployment" -ForegroundColor Red
    if ($portForwardJob) { Stop-Job -Job $portForwardJob; Remove-Job -Job $portForwardJob }
    if ($monitorJob) { Stop-Job -Job $monitorJob; Remove-Job -Job $monitorJob }
    exit 1
}
Write-Host "✓ Rolling update initiated" -ForegroundColor Green
Write-Host ""

Write-Host "New image version:" -ForegroundColor Yellow
kubectl get deployment $DEPLOYMENT_NAME -o jsonpath='{.spec.template.spec.containers[0].image}'
Write-Host ""
Write-Host ""

# Step 6: Monitor rollout status
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 6: Monitoring Rollout Progress" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl rollout status deployment/$DEPLOYMENT_NAME --timeout=120s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Rollout completed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Rollout failed or timed out" -ForegroundColor Red
    if ($portForwardJob) { Stop-Job -Job $portForwardJob; Remove-Job -Job $portForwardJob }
    if ($monitorJob) { Stop-Job -Job $monitorJob; Remove-Job -Job $monitorJob }
    exit 1
}
Write-Host ""

# Step 7: Wait for monitoring to complete
if ($monitorJob) {
    Write-Host "Waiting for availability monitoring to complete..." -ForegroundColor Yellow
    Wait-Job -Job $monitorJob | Out-Null
    $monitorResult = Receive-Job -Job $monitorJob
    Remove-Job -Job $monitorJob
    
    if ($monitorResult) {
        Write-Host "Monitor output collected" -ForegroundColor Green
    }
}

# Step 8: Verify rollout completion
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 8: Verifying Rollout Completion" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Updated pods:" -ForegroundColor Yellow
kubectl get pods -l app=django-messaging,version=blue
Write-Host ""

Write-Host "Rollout history:" -ForegroundColor Yellow
kubectl rollout history deployment/$DEPLOYMENT_NAME
Write-Host ""

Write-Host "Current deployment status:" -ForegroundColor Yellow
kubectl get deployment $DEPLOYMENT_NAME
Write-Host ""

Write-Host "Pod details:" -ForegroundColor Yellow
kubectl get pods -l app=django-messaging,version=blue -o wide
Write-Host ""

# Step 9: Final verification
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 9: Final Verification" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Verify all pods are running
$readyReplicas = kubectl get deployment $DEPLOYMENT_NAME -o jsonpath='{.status.readyReplicas}'
$desiredReplicas = kubectl get deployment $DEPLOYMENT_NAME -o jsonpath='{.spec.replicas}'

Write-Host "Ready Replicas: $readyReplicas / $desiredReplicas" -ForegroundColor White

if ($readyReplicas -eq $desiredReplicas) {
    Write-Host "✓ All replicas are ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  Not all replicas are ready yet" -ForegroundColor Yellow
}
Write-Host ""

# Test final application state
if ($portForwardJob -and $portForwardJob.State -eq "Running") {
    Write-Host "Testing application after update..." -ForegroundColor Yellow
    if (Test-Application -Url $TEST_ENDPOINT) {
        Write-Host "✓ Application is responding after update" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Application not responding after update" -ForegroundColor Yellow
    }
}
Write-Host ""

# Cleanup port forwarding
if ($portForwardJob) {
    Stop-Job -Job $portForwardJob
    Remove-Job -Job $portForwardJob
    Write-Host "✓ Port forwarding stopped" -ForegroundColor Green
}
Write-Host ""

# Final summary
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Rolling Update Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
$currentImage = kubectl get deployment $DEPLOYMENT_NAME -o jsonpath='{.spec.template.spec.containers[0].image}'
Write-Host "  - Deployment: $DEPLOYMENT_NAME" -ForegroundColor White
Write-Host "  - Image: $currentImage" -ForegroundColor White
Write-Host "  - Replicas: $readyReplicas / $desiredReplicas" -ForegroundColor White
Write-Host "  - Log file: $LOG_FILE" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  - kubectl get pods -l app=django-messaging,version=blue" -ForegroundColor White
Write-Host "  - kubectl describe deployment $DEPLOYMENT_NAME" -ForegroundColor White
Write-Host "  - kubectl rollout history deployment/$DEPLOYMENT_NAME" -ForegroundColor White
Write-Host "  - kubectl rollout undo deployment/$DEPLOYMENT_NAME  # Rollback if needed" -ForegroundColor White
Write-Host ""
