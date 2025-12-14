#!/bin/bash

# Script to set up Nginx Ingress Controller and apply Ingress configuration

echo "=========================================="
echo "Kubernetes Ingress Setup"
echo "=========================================="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    exit 1
fi
echo "✓ kubectl is available"
echo ""

# Check if minikube is available
if command -v minikube &> /dev/null; then
    USING_MINIKUBE=true
    echo "✓ minikube detected"
else
    USING_MINIKUBE=false
    echo "ℹ️  minikube not detected, will use standard installation"
fi
echo ""

# Step 1: Install Nginx Ingress Controller
echo "=========================================="
echo "Step 1: Installing Nginx Ingress Controller"
echo "=========================================="

if [ "$USING_MINIKUBE" = true ]; then
    echo "Enabling Ingress addon in minikube..."
    minikube addons enable ingress
    
    if [ $? -eq 0 ]; then
        echo "✓ Ingress addon enabled"
    else
        echo "✗ Failed to enable Ingress addon"
        exit 1
    fi
else
    echo "Installing Nginx Ingress Controller via kubectl..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
    
    if [ $? -eq 0 ]; then
        echo "✓ Ingress Controller installed"
    else
        echo "✗ Failed to install Ingress Controller"
        exit 1
    fi
fi
echo ""

# Step 2: Wait for Ingress Controller to be ready
echo "=========================================="
echo "Step 2: Waiting for Ingress Controller"
echo "=========================================="
echo "This may take a minute..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=120s

if [ $? -eq 0 ]; then
    echo "✓ Ingress Controller is ready"
else
    echo "⚠️  Timeout waiting for Ingress Controller"
    echo "Checking controller status..."
    kubectl get pods -n ingress-nginx
fi
echo ""

# Step 3: Apply Ingress configuration
echo "=========================================="
echo "Step 3: Applying Ingress Configuration"
echo "=========================================="
kubectl apply -f ingress.yaml

if [ $? -eq 0 ]; then
    echo "✓ Ingress configuration applied"
else
    echo "✗ Failed to apply Ingress configuration"
    exit 1
fi
echo ""

# Step 4: Display Ingress information
echo "=========================================="
echo "Step 4: Ingress Status"
echo "=========================================="
echo ""
echo "Ingress Resources:"
kubectl get ingress
echo ""
echo "Ingress Details:"
kubectl describe ingress django-messaging-ingress | head -20
echo ""

# Step 5: Configure local DNS
echo "=========================================="
echo "Step 5: DNS Configuration"
echo "=========================================="

if [ "$USING_MINIKUBE" = true ]; then
    MINIKUBE_IP=$(minikube ip)
    echo "Minikube IP: $MINIKUBE_IP"
    echo ""
    echo "Add the following line to your /etc/hosts file:"
    echo "$MINIKUBE_IP messaging-app.local api.messaging-app.local"
    echo ""
    echo "On Linux/Mac, run:"
    echo "  echo '$MINIKUBE_IP messaging-app.local api.messaging-app.local' | sudo tee -a /etc/hosts"
    echo ""
    echo "On Windows, add to C:\\Windows\\System32\\drivers\\etc\\hosts:"
    echo "  $MINIKUBE_IP messaging-app.local api.messaging-app.local"
else
    echo "Get your cluster's external IP:"
    kubectl get service -n ingress-nginx ingress-nginx-controller
    echo ""
    echo "Add the EXTERNAL-IP to your hosts file"
fi
echo ""

# Step 6: Display access information
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Access the application:"
echo "  - http://messaging-app.local"
echo "  - http://messaging-app.local/admin"
echo "  - http://messaging-app.local/api"
echo "  - http://api.messaging-app.local"
echo ""
echo "Test with curl:"
echo "  curl http://messaging-app.local/"
echo ""
echo "Port forwarding alternative (if DNS not configured):"
echo "  kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80"
echo "  Then access: http://localhost:8080"
echo ""
echo "View logs:"
echo "  kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller"
echo ""
