# Docker Build and Run Instructions

## Quick Start

### 1. Build the Docker Image

```bash
cd messaging_app
docker build -t messaging-app:latest .
```

### 2. Run the Container

```bash
docker run -p 8000:8000 messaging-app:latest
```

### 3. Access the Application

Open your browser and go to: `http://localhost:8000`

---

## Detailed Instructions

### Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (optional but recommended)

### Building the Image

Build with a specific tag:
```bash
docker build -t messaging-app:v1.0 .
```

Build with no cache (clean build):
```bash
docker build --no-cache -t messaging-app:latest .
```

View build progress:
```bash
docker build -t messaging-app:latest . --progress=plain
```

### Running the Container

**Basic run:**
```bash
docker run -p 8000:8000 messaging-app:latest
```

**Run in detached mode:**
```bash
docker run -d -p 8000:8000 --name messaging-app-container messaging-app:latest
```

**Run with environment variables:**
```bash
docker run -p 8000:8000 \
  -e DEBUG=1 \
  -e DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1" \
  messaging-app:latest
```

**Run with volume mounting (for development):**
```bash
docker run -p 8000:8000 \
  -v $(pwd):/app \
  messaging-app:latest
```

### Using Docker Compose

**Start all services:**
```bash
docker-compose up --build
```

**Run in background:**
```bash
docker-compose up -d --build
```

**Stop services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f web
```

### Container Management

**List running containers:**
```bash
docker ps
```

**Stop a container:**
```bash
docker stop messaging-app-container
```

**Start a stopped container:**
```bash
docker start messaging-app-container
```

**Remove a container:**
```bash
docker rm messaging-app-container
```

**View container logs:**
```bash
docker logs messaging-app-container
docker logs -f messaging-app-container  # Follow logs
```

**Execute commands in running container:**
```bash
docker exec -it messaging-app-container bash
docker exec -it messaging-app-container python manage.py shell
```

### Image Management

**List images:**
```bash
docker images
```

**Remove an image:**
```bash
docker rmi messaging-app:latest
```

**Tag an image:**
```bash
docker tag messaging-app:latest messaging-app:v1.0
```

### Running Django Commands

**Apply migrations:**
```bash
docker exec -it messaging-app-container python manage.py migrate
```

**Create superuser:**
```bash
docker exec -it messaging-app-container python manage.py createsuperuser
```

**Collect static files:**
```bash
docker exec -it messaging-app-container python manage.py collectstatic
```

**Run tests:**
```bash
docker exec -it messaging-app-container python manage.py test
```

### Troubleshooting

**Port already in use:**
```bash
# Use a different port
docker run -p 8080:8000 messaging-app:latest
```

**View container details:**
```bash
docker inspect messaging-app-container
```

**Access container shell:**
```bash
docker exec -it messaging-app-container /bin/bash
```

**Check container resource usage:**
```bash
docker stats messaging-app-container
```

**Clean up all stopped containers:**
```bash
docker container prune
```

**Clean up unused images:**
```bash
docker image prune -a
```

### Production Deployment

For production, use the production Dockerfile:

```bash
docker build -f Dockerfile.prod -t messaging-app:prod .
docker run -d -p 8000:8000 --name messaging-app-prod messaging-app:prod
```

### Health Check

Test if the application is running:
```bash
curl http://localhost:8000
```

### Environment Variables

Common environment variables you can set:

- `DEBUG`: Set to 0 for production
- `SECRET_KEY`: Django secret key
- `DJANGO_ALLOWED_HOSTS`: Space-separated list of allowed hosts
- `DATABASE_URL`: Database connection string

Example:
```bash
docker run -p 8000:8000 \
  -e DEBUG=0 \
  -e SECRET_KEY="your-secret-key" \
  -e DJANGO_ALLOWED_HOSTS="example.com www.example.com" \
  messaging-app:latest
```

### Multi-Stage Build (Advanced)

For smaller production images, create a multi-stage build in your Dockerfile:

```dockerfile
# Build stage
FROM python:3.10-slim as builder
# ... build dependencies

# Runtime stage
FROM python:3.10-slim
# ... copy from builder
```

### Docker Hub Deployment

**Login to Docker Hub:**
```bash
docker login
```

**Tag image for Docker Hub:**
```bash
docker tag messaging-app:latest yourusername/messaging-app:latest
```

**Push to Docker Hub:**
```bash
docker push yourusername/messaging-app:latest
```

**Pull from Docker Hub:**
```bash
docker pull yourusername/messaging-app:latest
```

## Verification

After running the container, verify it's working:

1. Check if container is running:
   ```bash
   docker ps
   ```

2. Check application logs:
   ```bash
   docker logs messaging-app-container
   ```

3. Access the application:
   ```bash
   curl http://localhost:8000
   ```

4. Check application health:
   ```bash
   docker exec messaging-app-container python manage.py check
   ```

## Common Issues

**Issue: Port 8000 is already in use**
- Solution: Stop the service using port 8000 or use a different port

**Issue: Container exits immediately**
- Solution: Check logs with `docker logs messaging-app-container`

**Issue: Cannot connect to database**
- Solution: Ensure database service is running and accessible

**Issue: Permission denied errors**
- Solution: Check file permissions or run with appropriate user