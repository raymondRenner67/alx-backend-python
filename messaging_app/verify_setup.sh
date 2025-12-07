#!/bin/bash
# Verification script for Docker Compose setup

echo "========================================="
echo "Docker Compose Multi-Container Verification"
echo "========================================="
echo ""

# Check if .env file exists
echo "1. Checking .env file..."
if [ -f .env ]; then
    echo "   ✓ .env file exists"
else
    echo "   ✗ .env file not found"
    echo "   → Create .env file from .env.example"
    exit 1
fi
echo ""

# Check if Docker is running
echo "2. Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "   ✓ Docker is running"
else
    echo "   ✗ Docker is not running"
    echo "   → Start Docker Desktop"
    exit 1
fi
echo ""

# Check if docker-compose is available
echo "3. Checking Docker Compose..."
if docker-compose --version > /dev/null 2>&1; then
    echo "   ✓ Docker Compose is installed"
    docker-compose --version
else
    echo "   ✗ Docker Compose is not installed"
    exit 1
fi
echo ""

# Check if containers are running
echo "4. Checking running containers..."
if docker-compose ps | grep -q "Up"; then
    echo "   ✓ Containers are running"
    docker-compose ps
else
    echo "   ✗ Containers are not running"
    echo "   → Run: docker-compose up --build"
fi
echo ""

# Test database connection
echo "5. Testing database connection..."
if docker-compose exec -T db mysqladmin ping -h localhost --silent; then
    echo "   ✓ MySQL database is responding"
else
    echo "   ✗ Cannot connect to MySQL database"
fi
echo ""

# Test web service
echo "6. Testing web service..."
if curl -s http://localhost:8000 > /dev/null; then
    echo "   ✓ Web service is responding on port 8000"
else
    echo "   ✗ Web service is not responding"
    echo "   → Check logs: docker-compose logs web"
fi
echo ""

# Check migrations
echo "7. Checking Django migrations..."
docker-compose exec -T web python manage.py showmigrations 2>/dev/null
echo ""

echo "========================================="
echo "Verification Complete"
echo "========================================="
echo ""
echo "Next steps:"
echo "  - Access app: http://localhost:8000"
echo "  - View logs: docker-compose logs -f"
echo "  - Create superuser: docker-compose exec web python manage.py createsuperuser"
echo ""