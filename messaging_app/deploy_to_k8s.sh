#!/bin/bash

# Script to build Docker image and deploy Django Messaging App to Kubernetes

echo "=========================================="
echo "Django Messaging App - Kubernetes Deployment"
echo "=========================================="
echo ""

# Step 1: Build Docker image
echo "Step 1: Building Docker image..."
echo "=========================================="
docker build -t django-messaging-app:latest .

if [ $? -ne 0 ]; then
    echo "Error: Docker build failed"
    exit 1
fi
echo "✓ Docker image built successfully"
echo ""

# Step 2: Load image into minikube (if using minikube)
echo "Step 2: Loading image into minikube..."
echo "=========================================="
if command -v minikube &> /dev/null; then
    minikube image load django-messaging-app:latest
    echo "✓ Image loaded into minikube"
else
    echo "ℹ️  Minikube not detected, skipping image load"
fi
echo ""

# Step 3: Create namespace (optional)
echo "Step 3: Creating namespace (optional)..."
echo "=========================================="
kubectl create namespace django-app 2>/dev/null || echo "ℹ️  Namespace already exists or using default"
echo ""

# Step 4: Apply Kubernetes manifests
echo "Step 4: Applying Kubernetes deployment..."
echo "=========================================="
kubectl apply -f deployment.yaml

if [ $? -ne 0 ]; then
    echo "Error: Deployment failed"
    exit 1
fi
echo "✓ Deployment applied successfully"
echo ""

# Step 5: Wait for pods to be ready
echo "Step 5: Waiting for pods to be ready..."
echo "=========================================="
kubectl wait --for=condition=ready pod -l app=django-messaging --timeout=120s

echo ""

# Step 6: Display deployment status
echo "=========================================="
echo "Deployment Status"
echo "=========================================="
echo ""
echo "Pods:"
kubectl get pods -l app=django-messaging
echo ""
echo "Services:"
kubectl get services -l app=django-messaging
echo ""
echo "Deployments:"
kubectl get deployments -l app=django-messaging
echo ""

# Step 7: Get pod name for logs
POD_NAME=$(kubectl get pods -l app=django-messaging -o jsonpath='{.items[0].metadata.name}')

if [ -n "$POD_NAME" ]; then
    echo "=========================================="
    echo "Recent logs from pod: $POD_NAME"
    echo "=========================================="
    kubectl logs $POD_NAME --tail=20
    echo ""
    
    echo "=========================================="
    echo "Deployment Complete!"
    echo "=========================================="
    echo ""
    echo "Useful commands:"
    echo "  - kubectl get pods                    : View all pods"
    echo "  - kubectl logs $POD_NAME              : View logs"
    echo "  - kubectl describe pod $POD_NAME      : Detailed pod info"
    echo "  - kubectl exec -it $POD_NAME -- bash  : Shell into pod"
    echo "  - kubectl port-forward $POD_NAME 8000:8000 : Access app locally"
    echo "  - kubectl delete -f deployment.yaml   : Remove deployment"
else
    echo "Warning: No pods found. Check deployment status with: kubectl get pods"
fi
echo ""
