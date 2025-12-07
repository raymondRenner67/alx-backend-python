# Django Messaging App - Docker Setup

## Prerequisites
- Docker installed on your system
- Docker Compose (optional, but recommended)

## Building and Running with Docker

### Option 1: Using Docker directly

1. **Build the Docker image:**
   ```bash
   docker build -t messaging-app .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 messaging-app
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:8000`

### Option 2: Using Docker Compose (Recommended)

1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Running Django Commands in Docker

### Apply migrations:
```bash
docker-compose exec web python manage.py migrate
```

### Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Run tests:
```bash
docker-compose exec web python manage.py test
```

### Access Django shell:
```bash
docker-compose exec web python manage.py shell
```

## Environment Variables

Create a `.env` file in the project root with the following variables:
```
DEBUG=1
SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
DATABASE_URL=postgresql://postgres:postgres@db:5432/messaging_app
```

## Troubleshooting

### Port already in use:
```bash
# Stop any service using port 8000
docker-compose down
# Or change the port in docker-compose.yml
```

### Database connection issues:
```bash
# Rebuild containers
docker-compose down -v
docker-compose up --build
```

### View container logs:
```bash
docker-compose logs web
docker-compose logs db
```

## Production Considerations

For production deployment:
1. Set `DEBUG=False` in settings
2. Use a proper SECRET_KEY
3. Configure ALLOWED_HOSTS properly
4. Use a production-grade server (gunicorn)
5. Set up proper database backups
6. Use environment variables for sensitive data

## Docker Commands Reference

```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Remove stopped containers
docker-compose rm

# View image details
docker images

# Remove unused images
docker image prune

# Access container shell
docker-compose exec web bash
```