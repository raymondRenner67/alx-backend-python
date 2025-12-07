# Quick Start Guide - Windows PowerShell

## Build and Run the Docker Container

### Step 1: Navigate to the project directory
```powershell
cd C:\Users\Latitude7480\Downloads\pf\alx-backend-python\messaging_app
```

### Step 2: Build the Docker image
```powershell
docker build -t messaging-app:latest .
```

### Step 3: Run the container
```powershell
docker run -p 8000:8000 messaging-app:latest
```

### Step 4: Access the application
Open your browser and navigate to: http://localhost:8000

---

## Alternative: Using Docker Compose

### Build and start all services
```powershell
docker-compose up --build
```

### Run in background (detached mode)
```powershell
docker-compose up -d --build
```

### View logs
```powershell
docker-compose logs -f
```

### Stop services
```powershell
docker-compose down
```

---

## Common Commands

### List running containers
```powershell
docker ps
```

### View container logs
```powershell
docker logs <container-id>
```

### Stop a running container
```powershell
docker stop <container-id>
```

### Remove a container
```powershell
docker rm <container-id>
```

### Execute command in running container
```powershell
docker exec -it <container-id> python manage.py migrate
docker exec -it <container-id> python manage.py createsuperuser
```

### Clean up (remove all stopped containers and unused images)
```powershell
docker system prune -a
```

---

## Troubleshooting

### If port 8000 is already in use:
```powershell
# Use a different port
docker run -p 8080:8000 messaging-app:latest
```

### If build fails, try clean build:
```powershell
docker build --no-cache -t messaging-app:latest .
```

### Check if Docker is running:
```powershell
docker --version
docker ps
```

---

## Verification Steps

1. **Check if container is running:**
   ```powershell
   docker ps
   ```

2. **Test the application:**
   ```powershell
   curl http://localhost:8000
   # Or open in browser: http://localhost:8000
   ```

3. **View application logs:**
   ```powershell
   docker logs -f <container-id>
   ```

---

## Running Django Management Commands

```powershell
# Apply migrations
docker exec -it <container-id> python manage.py migrate

# Create superuser
docker exec -it <container-id> python manage.py createsuperuser

# Run tests
docker exec -it <container-id> python manage.py test

# Access Django shell
docker exec -it <container-id> python manage.py shell

# Collect static files
docker exec -it <container-id> python manage.py collectstatic
```

Replace `<container-id>` with the actual container ID from `docker ps`