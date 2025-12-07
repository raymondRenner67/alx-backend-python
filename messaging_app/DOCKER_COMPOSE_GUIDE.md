# Docker Compose Multi-Container Setup Guide

## Overview

This setup includes:
- **web**: Django messaging app
- **db**: MySQL 8.0 database

All configuration is managed through environment variables in `.env` file.

---

## Quick Start

### 1. Ensure you have the `.env` file

The `.env` file contains all environment variables and should NOT be pushed to GitHub.

```bash
# Copy from example if needed
cp .env.example .env
```

### 2. Build and start all services

```powershell
docker-compose up --build
```

### 3. Access the application

Open your browser: http://localhost:8000

---

## Detailed Setup

### Environment Variables

The `.env` file contains:

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# MySQL Database Settings
MYSQL_DATABASE=messaging_app
MYSQL_USER=messaging_user
MYSQL_PASSWORD=your-password
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_HOST=db
MYSQL_PORT=3306
```

**Important**: Never commit `.env` to version control!

### Services Configuration

#### Web Service (Django App)
- Builds from local Dockerfile
- Runs migrations automatically
- Exposed on port 8000
- Uses environment variables from `.env`
- Depends on MySQL database

#### DB Service (MySQL)
- Uses official MySQL 8.0 image
- Persistent data storage with Docker volume
- Exposed on port 3306
- Health check enabled
- Configured via environment variables

---

## Docker Compose Commands

### Start services
```powershell
# Build and start
docker-compose up --build

# Start in detached mode (background)
docker-compose up -d

# Start specific service
docker-compose up web
```

### Stop services
```powershell
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes database data)
docker-compose down -v
```

### View logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Execute commands in containers
```powershell
# Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Run tests
docker-compose exec web python manage.py test

# Access bash in web container
docker-compose exec web bash

# Access MySQL CLI
docker-compose exec db mysql -u messaging_user -p messaging_app
```

### Rebuild services
```powershell
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build web

# Rebuild with no cache
docker-compose build --no-cache
```

---

## Verification Steps

### 1. Check if services are running
```powershell
docker-compose ps
```

You should see both `web` and `db` services running.

### 2. Check database connection

```powershell
# Access web container
docker-compose exec web python manage.py dbshell
```

Or check Django's database configuration:
```powershell
docker-compose exec web python manage.py check --database default
```

### 3. Test the application

```powershell
# Check if app responds
curl http://localhost:8000

# Or open in browser
start http://localhost:8000
```

### 4. Verify MySQL connection

```powershell
# Connect to MySQL
docker-compose exec db mysql -u messaging_user -p

# Enter the password from your .env file
# Then run:
SHOW DATABASES;
USE messaging_app;
SHOW TABLES;
```

---

## Database Management

### Create initial migration
```powershell
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Backup database
```powershell
docker-compose exec db mysqldump -u messaging_user -p messaging_app > backup.sql
```

### Restore database
```powershell
docker-compose exec -T db mysql -u messaging_user -p messaging_app < backup.sql
```

### Reset database
```powershell
# Stop services and remove volumes
docker-compose down -v

# Start fresh
docker-compose up --build
```

---

## Troubleshooting

### Database connection errors

**Issue**: Web service can't connect to database

**Solutions**:
1. Ensure database is fully started (check with health check)
2. Verify environment variables in `.env`
3. Check logs: `docker-compose logs db`
4. Restart services: `docker-compose restart`

### Port conflicts

**Issue**: Port 8000 or 3306 already in use

**Solutions**:
1. Stop conflicting services
2. Or modify ports in `docker-compose.yml`:
   ```yaml
   ports:
     - "8080:8000"  # Use different host port
   ```

### Permission errors

**Issue**: Cannot write to volumes

**Solution**:
```powershell
# On Windows, ensure Docker has access to the drive
# Docker Desktop > Settings > Resources > File Sharing
```

### MySQL initialization fails

**Solutions**:
1. Remove volumes and restart:
   ```powershell
   docker-compose down -v
   docker-compose up --build
   ```
2. Check MySQL logs:
   ```powershell
   docker-compose logs db
   ```

### Migrations not applying

**Solutions**:
1. Run manually:
   ```powershell
   docker-compose exec web python manage.py migrate
   ```
2. Check for migration conflicts:
   ```powershell
   docker-compose exec web python manage.py showmigrations
   ```

---

## Development Workflow

### Making code changes

1. Edit your code (changes reflect immediately due to volume mounting)
2. If models changed, create migrations:
   ```powershell
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```
3. Restart if needed:
   ```powershell
   docker-compose restart web
   ```

### Adding new dependencies

1. Update `requirements.txt`
2. Rebuild the web service:
   ```powershell
   docker-compose build web
   docker-compose up -d
   ```

---

## Production Considerations

For production deployment:

1. **Change DEBUG to False**
   ```env
   DEBUG=False
   ```

2. **Use strong SECRET_KEY**
   ```env
   SECRET_KEY=generate-a-strong-random-key
   ```

3. **Secure database passwords**
   ```env
   MYSQL_PASSWORD=use-strong-password
   MYSQL_ROOT_PASSWORD=use-strong-password
   ```

4. **Configure ALLOWED_HOSTS**
   ```env
   DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

5. **Use production server (Gunicorn)**
   Update docker-compose.yml:
   ```yaml
   command: gunicorn messaging_app.wsgi:application --bind 0.0.0.0:8000
   ```

6. **Set up proper backups**
7. **Use secrets management** (Docker secrets, AWS Secrets Manager, etc.)
8. **Enable SSL/TLS**
9. **Set up monitoring and logging**

---

## Clean Up

### Stop everything
```powershell
docker-compose down
```

### Remove all data (including database)
```powershell
docker-compose down -v
```

### Remove images
```powershell
docker-compose down --rmi all
```

---

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Database Settings](https://docs.djangoproject.com/en/stable/ref/settings/#databases)
- [MySQL Docker Hub](https://hub.docker.com/_/mysql)
- [Django Environment Variables](https://django-environ.readthedocs.io/)

---

## Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify `.env` configuration
3. Ensure Docker is running
4. Try clean rebuild: `docker-compose down -v && docker-compose up --build`