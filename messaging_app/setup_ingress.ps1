# PowerShell Script to set up Nginx Ingress Controller and apply Ingress configuration

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Kubernetes Ingress Setup" -ForegroundColor Cyan
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

# Check if minikube is available
$USING_MINIKUBE = $false
try {
    minikube version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $USING_MINIKUBE = $true
        Write-Host "✓ minikube detected" -ForegroundColor Green
    }
} catch {
    Write-Host "ℹ️  minikube not detected, will use standard installation" -ForegroundColor Yellow
}
Write-Host ""

# Step 1: Install Nginx Ingress Controller
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 1: Installing Nginx Ingress Controller" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($USING_MINIKUBE) {
    Write-Host "Enabling Ingress addon in minikube..." -ForegroundColor Yellow
    minikube addons enable ingress
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Ingress addon enabled" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to enable Ingress addon" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Installing Nginx Ingress Controller via kubectl..." -ForegroundColor Yellow
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Ingress Controller installed" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install Ingress Controller" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Step 2: Wait for Ingress Controller to be ready
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 2: Waiting for Ingress Controller" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "This may take a minute..." -ForegroundColor Yellow
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Ingress Controller is ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  Timeout waiting for Ingress Controller" -ForegroundColor Yellow
    Write-Host "Checking controller status..." -ForegroundColor Yellow
    kubectl get pods -n ingress-nginx
}
Write-Host ""

# Step 3: Apply Ingress configuration
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 3: Applying Ingress Configuration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
kubectl apply -f ingress.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Ingress configuration applied" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to apply Ingress configuration" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Display Ingress information
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 4: Ingress Status" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ingress Resources:" -ForegroundColor Yellow
kubectl get ingress
Write-Host ""
Write-Host "Ingress Details:" -ForegroundColor Yellow
kubectl describe ingress django-messaging-ingress | Select-Object -First 20
Write-Host ""

# Step 5: Configure local DNS
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 5: DNS Configuration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($USING_MINIKUBE) {
    $MINIKUBE_IP = minikube ip
    Write-Host "Minikube IP: $MINIKUBE_IP" -ForegroundColor Green
    Write-Host ""
    Write-Host "Add the following line to your hosts file:" -ForegroundColor Yellow
    Write-Host "$MINIKUBE_IP messaging-app.local api.messaging-app.local" -ForegroundColor White
    Write-Host ""
    Write-Host "Windows hosts file location:" -ForegroundColor Yellow
    Write-Host "  C:\Windows\System32\drivers\etc\hosts" -ForegroundColor White
    Write-Host ""
    Write-Host "Run as Administrator to add automatically:" -ForegroundColor Yellow
    Write-Host "  Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value `"``n$MINIKUBE_IP messaging-app.local api.messaging-app.local`"" -ForegroundColor White
} else {
    Write-Host "Get your cluster's external IP:" -ForegroundColor Yellow
    kubectl get service -n ingress-nginx ingress-nginx-controller
    Write-Host ""
    Write-Host "Add the EXTERNAL-IP to your hosts file" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Display access information
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Yellow
Write-Host "  - http://messaging-app.local" -ForegroundColor White
Write-Host "  - http://messaging-app.local/admin" -ForegroundColor White
Write-Host "  - http://messaging-app.local/api" -ForegroundColor White
Write-Host "  - http://api.messaging-app.local" -ForegroundColor White
Write-Host ""
Write-Host "Test with curl:" -ForegroundColor Yellow
Write-Host "  curl http://messaging-app.local/" -ForegroundColor White
Write-Host ""
Write-Host "Port forwarding alternative (if DNS not configured):" -ForegroundColor Yellow
Write-Host "  kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80" -ForegroundColor White
Write-Host "  Then access: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller" -ForegroundColor White
Write-Host ""
