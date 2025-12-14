# Blue-Green Deployment Strategy for Django Messaging App

## Overview

This implementation provides a zero-downtime deployment strategy using Kubernetes blue-green deployment pattern. The blue version represents the current stable deployment, while the green version represents the new version being deployed.

## Files Created

1. **blue_deployment.yaml** - Stable/current version deployment
2. **green_deployment.yaml** - New version deployment
3. **kubeservice.yaml** - Services for traffic management
4. **kubctl-0x02** - Bash script for deployment and verification
5. **kubctl-0x02.ps1** - PowerShell script for deployment and verification

## Blue-Green Deployment Concept

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer/Service                 │
│                 (Traffic Selector: version)              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Switch traffic by changing selector
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│    BLUE      │    │    GREEN     │
│  (Current)   │    │    (New)     │
│   3 Pods     │    │   3 Pods     │
│  v1 Image    │    │  v2 Image    │
└──────────────┘    └──────────────┘
```

## Deployment Strategy Steps

### Phase 1: Initial State
- **Blue deployment** is running and receiving all traffic
- Service selector points to `version: blue`

### Phase 2: Deploy Green
- Deploy **green deployment** alongside blue
- Both versions run simultaneously
- Green receives no production traffic yet

### Phase 3: Testing
- Test green deployment through dedicated service
- Verify logs for errors
- Perform smoke tests

### Phase 4: Traffic Switch
- Update service selector from `blue` to `green`
- All traffic now goes to green deployment
- Blue deployment remains running (for rollback)

### Phase 5: Cleanup
- Monitor green deployment in production
- If stable, delete blue deployment
- If issues, switch back to blue (instant rollback)

## Usage

### Automated Deployment (Recommended)

**On Windows (PowerShell):**
```powershell
.\kubctl-0x02.ps1
```

**On Linux/Mac (Bash):**
```bash
chmod +x kubctl-0x02
./kubctl-0x02
```

### Manual Step-by-Step

#### Step 1: Deploy Blue Version
```bash
kubectl apply -f blue_deployment.yaml
kubectl rollout status deployment/django-messaging-app-blue
```

#### Step 2: Deploy Green Version
```bash
kubectl apply -f green_deployment.yaml
kubectl rollout status deployment/django-messaging-app-green
```

#### Step 3: Apply Services
```bash
kubectl apply -f kubeservice.yaml
```

#### Step 4: Verify Both Deployments
```bash
# Check deployments
kubectl get deployments -l app=django-messaging

# Check pods
kubectl get pods -l app=django-messaging

# Check services
kubectl get services -l app=django-messaging
```

#### Step 5: Test Green Deployment
```bash
# Port forward to green service
kubectl port-forward service/django-messaging-green 8001:8000

# Access in browser: http://localhost:8001
# Run your tests against this endpoint
```

#### Step 6: Check Logs
```bash
# Blue deployment logs
kubectl logs -l app=django-messaging,version=blue --tail=50

# Green deployment logs
kubectl logs -l app=django-messaging,version=green --tail=50
```

#### Step 7: Switch Traffic to Green
```bash
# Update main service to point to green
kubectl patch service django-messaging-service -p '{"spec":{"selector":{"version":"green"}}}'

# Verify the change
kubectl get service django-messaging-service -o yaml | grep version
```

#### Step 8: Monitor and Rollback if Needed
```bash
# If everything is good, continue monitoring
kubectl logs -l app=django-messaging,version=green -f

# If issues occur, rollback to blue
kubectl patch service django-messaging-service -p '{"spec":{"selector":{"version":"blue"}}}'
```

#### Step 9: Cleanup (After Verification)
```bash
# Once green is stable, remove blue deployment
kubectl delete -f blue_deployment.yaml
```

## Service Configuration

The `kubeservice.yaml` includes multiple services:

### 1. Main Service (django-messaging-service)
- **Purpose**: Primary production traffic
- **Type**: ClusterIP
- **Selector**: Can be switched between `version: blue` and `version: green`
- **Port**: 8000

### 2. Blue Service (django-messaging-blue)
- **Purpose**: Direct access to blue deployment for testing
- **Type**: ClusterIP
- **Selector**: Always points to `version: blue`
- **Port**: 8000

### 3. Green Service (django-messaging-green)
- **Purpose**: Direct access to green deployment for testing
- **Type**: ClusterIP
- **Selector**: Always points to `version: green`
- **Port**: 8000

### 4. External Service (django-messaging-external)
- **Purpose**: External access via LoadBalancer (optional)
- **Type**: LoadBalancer
- **Selector**: Can be switched like main service
- **Port**: 80 → 8000

## Traffic Switching Commands

### Switch to Green (New Version)
```bash
kubectl patch service django-messaging-service -p '{"spec":{"selector":{"version":"green"}}}'
```

### Rollback to Blue (Stable Version)
```bash
kubectl patch service django-messaging-service -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Verify Current Target
```bash
kubectl get service django-messaging-service -o jsonpath='{.spec.selector.version}'
```

## Verification Commands

### Check Deployment Status
```bash
# All deployments
kubectl get deployments -l app=django-messaging

# Specific version
kubectl get deployment django-messaging-app-blue
kubectl get deployment django-messaging-app-green
```

### Check Pod Status
```bash
# All pods
kubectl get pods -l app=django-messaging

# Blue pods only
kubectl get pods -l app=django-messaging,version=blue

# Green pods only
kubectl get pods -l app=django-messaging,version=green
```

### View Logs
```bash
# All logs
kubectl logs -l app=django-messaging --all-containers=true

# Blue logs
kubectl logs -l app=django-messaging,version=blue --tail=100

# Green logs
kubectl logs -l app=django-messaging,version=green --tail=100

# Follow logs in real-time
kubectl logs -l app=django-messaging,version=green -f
```

### Describe Resources
```bash
# Deployment details
kubectl describe deployment django-messaging-app-blue
kubectl describe deployment django-messaging-app-green

# Service details
kubectl describe service django-messaging-service

# Pod details
kubectl describe pod <pod-name>
```

## Testing Strategy

### 1. Pre-Deployment Testing
- Build new Docker image with tag `v2`
- Test locally with `docker run`
- Push to registry

### 2. Green Deployment Testing
```bash
# Deploy green
kubectl apply -f green_deployment.yaml

# Wait for ready state
kubectl wait --for=condition=ready pod -l version=green --timeout=120s

# Port forward for testing
kubectl port-forward service/django-messaging-green 8001:8000

# Run tests against localhost:8001
curl http://localhost:8001/admin/
# Run full test suite
```

### 3. Canary Testing (Optional)
Before full switch, you can gradually shift traffic using multiple replicas or external tools.

### 4. Production Switch
```bash
# Switch all traffic
kubectl patch service django-messaging-service -p '{"spec":{"selector":{"version":"green"}}}'
```

### 5. Post-Deployment Monitoring
```bash
# Monitor logs
kubectl logs -l version=green -f

# Check pod health
kubectl get pods -l version=green --watch

# Check metrics (if available)
kubectl top pods -l version=green
```

## Rollback Procedure

### Instant Rollback (Service Switch)
```bash
# Switch back to blue immediately
kubectl patch service django-messaging-service -p '{"spec":{"selector":{"version":"blue"}}}'

# Verify
kubectl get service django-messaging-service -o yaml | grep version
```

### Complete Rollback
```bash
# Delete green deployment
kubectl delete -f green_deployment.yaml

# Verify blue is handling traffic
kubectl get pods -l app=django-messaging
```

## Advantages of Blue-Green Deployment

1. **Zero Downtime**: Both versions run simultaneously during transition
2. **Instant Rollback**: Switch back to blue if green has issues
3. **Safe Testing**: Test green in production environment before switching
4. **Simple Process**: Single kubectl patch command to switch traffic
5. **Reduced Risk**: Old version remains available during transition

## Image Tagging Strategy

```bash
# Build images with version tags
docker build -t django-messaging-app:v1 .  # Blue version
docker build -t django-messaging-app:v2 .  # Green version

# Or use git commits
docker build -t django-messaging-app:$(git rev-parse --short HEAD) .

# Tag as latest
docker tag django-messaging-app:v2 django-messaging-app:latest

# Load into minikube
minikube image load django-messaging-app:v1
minikube image load django-messaging-app:v2
```

## Cleanup

### Remove Green After Successful Deployment
```bash
kubectl delete -f green_deployment.yaml
kubectl delete service django-messaging-green
```

### Remove Blue After Successful Deployment
```bash
kubectl delete -f blue_deployment.yaml
kubectl delete service django-messaging-blue
```

### Complete Cleanup
```bash
kubectl delete -f blue_deployment.yaml
kubectl delete -f green_deployment.yaml
kubectl delete -f kubeservice.yaml
```

## Troubleshooting

### Green Pods Not Starting
```bash
# Check pod events
kubectl describe pod <green-pod-name>

# Check logs
kubectl logs <green-pod-name>

# Check image availability
minikube image ls | grep django-messaging
```

### Service Not Routing Traffic
```bash
# Check service endpoints
kubectl get endpoints django-messaging-service

# Verify selector
kubectl get service django-messaging-service -o yaml | grep -A 5 selector
```

### Rollback Not Working
```bash
# Verify blue deployment is still running
kubectl get deployment django-messaging-app-blue

# Check blue pod status
kubectl get pods -l version=blue

# Force service update
kubectl apply -f kubeservice.yaml
```

## Best Practices

1. **Always test green** before switching production traffic
2. **Monitor logs** during and after the switch
3. **Keep blue running** for at least 24 hours after switch
4. **Use health checks** (liveness/readiness probes)
5. **Tag images** with version numbers, not just `latest`
6. **Document changes** between blue and green versions
7. **Automate testing** of green deployment
8. **Set up alerts** for error rates and performance metrics

## Advanced: Automated Traffic Switching

You can create a script to gradually shift traffic:

```bash
#!/bin/bash
# Gradual traffic shift (requires Istio or similar)

# 10% to green
kubectl patch service django-messaging-service --type merge -p '{"spec":{"selector":{"version":"green","weight":"10"}}}'
sleep 300

# 50% to green
kubectl patch service django-messaging-service --type merge -p '{"spec":{"selector":{"version":"green","weight":"50"}}}'
sleep 300

# 100% to green
kubectl patch service django-messaging-service -p '{"spec":{"selector":{"version":"green"}}}'
```

Note: Basic Kubernetes services don't support weighted routing. Consider using Istio, Linkerd, or NGINX Ingress for advanced traffic splitting.

## Resources

- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Zero-Downtime Deployments](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)
