# Kubernetes Deployment Guide for Django Messaging App

## Prerequisites

1. **Kubernetes cluster running** (minikube or other)
2. **kubectl installed and configured**
3. **Docker installed** (to build the image)

## Quick Start

### Option 1: Automated Deployment (Recommended)

**On Windows (PowerShell):**
```powershell
.\deploy_to_k8s.ps1
```

**On Linux/Mac (Bash):**
```bash
chmod +x deploy_to_k8s.sh
./deploy_to_k8s.sh
```

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Build Docker Image
```bash
docker build -t django-messaging-app:latest .
```

#### Step 2: Load Image into Minikube (if using minikube)
```bash
minikube image load django-messaging-app:latest
```

#### Step 3: Apply Deployment
```bash
kubectl apply -f deployment.yaml
```

#### Step 4: Verify Deployment
```bash
# Check pods
kubectl get pods -l app=django-messaging

# Check service
kubectl get service django-messaging-service

# Check deployment
kubectl get deployment django-messaging-app
```

#### Step 5: View Logs
```bash
# Get pod name
kubectl get pods -l app=django-messaging

# View logs (replace <pod-name> with actual pod name)
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -f <pod-name>
```

## Deployment Components

### deployment.yaml includes:

1. **Deployment**: 
   - 3 replicas of the Django app
   - Docker image: `django-messaging-app:latest`
   - Container port: 8000
   - Resource limits and requests
   - Liveness and readiness probes

2. **Service (ClusterIP)**:
   - Internal access only
   - Port 8000
   - Session affinity enabled

3. **ConfigMap**:
   - Django configuration settings
   - Environment variables

4. **Secret**:
   - Sensitive data (SECRET_KEY)

## Accessing the Application

### Port Forwarding (for local access)
```bash
# Forward pod port to localhost
kubectl port-forward deployment/django-messaging-app 8000:8000
```
Then access: http://localhost:8000

### Exec into Pod (for debugging)
```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=django-messaging -o jsonpath='{.items[0].metadata.name}')

# Shell into pod
kubectl exec -it $POD_NAME -- bash

# Run Django management commands
kubectl exec -it $POD_NAME -- python manage.py migrate
kubectl exec -it $POD_NAME -- python manage.py createsuperuser
```

## Verification Commands

```bash
# 1. Check if pods are running
kubectl get pods -l app=django-messaging

# Expected output: STATUS should be "Running"
# NAME                                    READY   STATUS    RESTARTS   AGE
# django-messaging-app-xxxxxxxxxx-xxxxx   1/1     Running   0          2m

# 2. Check service
kubectl get service django-messaging-service

# Expected output: TYPE should be "ClusterIP"
# NAME                      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
# django-messaging-service  ClusterIP   10.96.xxx.xxx   <none>        8000/TCP   2m

# 3. Check deployment
kubectl get deployment django-messaging-app

# Expected output: READY should show "3/3"
# NAME                   READY   UP-TO-DATE   AVAILABLE   AGE
# django-messaging-app   3/3     3            3           2m

# 4. View detailed pod info
kubectl describe pod <pod-name>

# 5. View logs from all pods
kubectl logs -l app=django-messaging --all-containers=true

# 6. Check resource usage
kubectl top pods -l app=django-messaging
```

## Troubleshooting

### Pod not starting?
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check if image is available
minikube image ls | grep django-messaging
```

### ImagePullBackOff error?
```bash
# Make sure image is loaded into minikube
minikube image load django-messaging-app:latest

# Or update deployment to use imagePullPolicy: IfNotPresent
```

### CrashLoopBackOff?
```bash
# Check logs for errors
kubectl logs <pod-name>

# Check previous container logs
kubectl logs <pod-name> --previous
```

### Service not accessible?
```bash
# Verify service endpoints
kubectl get endpoints django-messaging-service

# Use port-forward to test
kubectl port-forward service/django-messaging-service 8000:8000
```

## Updating the Deployment

```bash
# After making changes to code:
docker build -t django-messaging-app:latest .
minikube image load django-messaging-app:latest

# Restart deployment
kubectl rollout restart deployment/django-messaging-app

# Watch rollout status
kubectl rollout status deployment/django-messaging-app
```

## Scaling the Deployment

```bash
# Scale to 5 replicas
kubectl scale deployment django-messaging-app --replicas=5

# Verify scaling
kubectl get pods -l app=django-messaging
```

## Cleanup

```bash
# Delete all resources
kubectl delete -f deployment.yaml

# Or delete individually
kubectl delete deployment django-messaging-app
kubectl delete service django-messaging-service
kubectl delete configmap django-config
kubectl delete secret django-secrets
```

## Environment Variables

You can customize these in `deployment.yaml`:

- `DEBUG`: Set to "False" for production
- `ALLOWED_HOSTS`: Configure allowed hosts
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Django secret key (stored in Secret)

## Production Considerations

1. **Use a real database** (PostgreSQL, MySQL) instead of SQLite
2. **Use persistent volumes** for data storage
3. **Configure ingress** for external access
4. **Set resource limits** appropriately
5. **Use secrets management** for sensitive data
6. **Enable monitoring and logging**
7. **Configure autoscaling** (HPA)
8. **Use health checks** (already included)

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
