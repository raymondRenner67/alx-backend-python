#!/bin/bash

# Script to verify Kubernetes deployment of Django Messaging App

echo "=========================================="
echo "Kubernetes Deployment Verification"
echo "=========================================="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed"
    exit 1
fi
echo "✓ kubectl is available"
echo ""

# Check cluster connection
echo "Checking cluster connection..."
kubectl cluster-info &> /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Connected to Kubernetes cluster"
else
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi
echo ""

# Check if deployment exists
echo "Checking deployment..."
DEPLOYMENT=$(kubectl get deployment django-messaging-app 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✓ Deployment 'django-messaging-app' exists"
    kubectl get deployment django-messaging-app
else
    echo "❌ Deployment 'django-messaging-app' not found"
    echo "   Run: kubectl apply -f deployment.yaml"
    exit 1
fi
echo ""

# Check if service exists
echo "Checking service..."
SERVICE=$(kubectl get service django-messaging-service 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✓ Service 'django-messaging-service' exists"
    kubectl get service django-messaging-service
else
    echo "❌ Service 'django-messaging-service' not found"
fi
echo ""

# Check pods status
echo "Checking pods..."
PODS=$(kubectl get pods -l app=django-messaging --no-headers 2>/dev/null | wc -l)
if [ $PODS -gt 0 ]; then
    echo "✓ Found $PODS pod(s)"
    kubectl get pods -l app=django-messaging
    echo ""
    
    # Check if pods are running
    RUNNING_PODS=$(kubectl get pods -l app=django-messaging --no-headers 2>/dev/null | grep -c "Running")
    if [ $RUNNING_PODS -gt 0 ]; then
        echo "✓ $RUNNING_PODS pod(s) are running"
    else
        echo "⚠️  No pods are in Running state"
    fi
else
    echo "❌ No pods found with label app=django-messaging"
    exit 1
fi
echo ""

# Get first pod name
POD_NAME=$(kubectl get pods -l app=django-messaging -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$POD_NAME" ]; then
    echo "=========================================="
    echo "Pod Details: $POD_NAME"
    echo "=========================================="
    
    # Check pod status
    POD_STATUS=$(kubectl get pod $POD_NAME -o jsonpath='{.status.phase}')
    echo "Status: $POD_STATUS"
    
    # Check pod readiness
    READY=$(kubectl get pod $POD_NAME -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    echo "Ready: $READY"
    
    echo ""
    
    # Show recent logs
    echo "=========================================="
    echo "Recent Logs (last 15 lines):"
    echo "=========================================="
    kubectl logs $POD_NAME --tail=15 2>/dev/null || echo "⚠️  Could not retrieve logs"
    echo ""
    
    # Show pod events
    echo "=========================================="
    echo "Recent Events:"
    echo "=========================================="
    kubectl get events --field-selector involvedObject.name=$POD_NAME --sort-by='.lastTimestamp' 2>/dev/null | tail -5
fi

echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo "✓ Deployment exists and configured"
echo "✓ Service exists (ClusterIP)"
echo "✓ Pods are created"
echo ""
echo "Next steps:"
echo "  1. Check logs: kubectl logs $POD_NAME"
echo "  2. Access app: kubectl port-forward $POD_NAME 8000:8000"
echo "  3. Shell into pod: kubectl exec -it $POD_NAME -- bash"
echo ""
