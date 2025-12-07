# Verification script for Docker Compose setup (PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Docker Compose Multi-Container Verification" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
Write-Host "1. Checking .env file..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "   ✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "   ✗ .env file not found" -ForegroundColor Red
    Write-Host "   → Create .env file from .env.example" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if Docker is running
Write-Host "2. Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "   ✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Docker is not running" -ForegroundColor Red
    Write-Host "   → Start Docker Desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if docker-compose is available
Write-Host "3. Checking Docker Compose..." -ForegroundColor Yellow
try {
    $version = docker-compose --version
    Write-Host "   ✓ Docker Compose is installed" -ForegroundColor Green
    Write-Host "   $version" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Docker Compose is not installed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if containers are running
Write-Host "4. Checking running containers..." -ForegroundColor Yellow
$containers = docker-compose ps
if ($containers -match "Up") {
    Write-Host "   ✓ Containers are running" -ForegroundColor Green
    docker-compose ps
} else {
    Write-Host "   ✗ Containers are not running" -ForegroundColor Red
    Write-Host "   → Run: docker-compose up --build" -ForegroundColor Yellow
}
Write-Host ""

# Test database connection
Write-Host "5. Testing database connection..." -ForegroundColor Yellow
try {
    $result = docker-compose exec -T db mysqladmin ping -h localhost --silent 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ MySQL database is responding" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Cannot connect to MySQL database" -ForegroundColor Red
    }
} catch {
    Write-Host "   ✗ Cannot connect to MySQL database" -ForegroundColor Red
}
Write-Host ""

# Test web service
Write-Host "6. Testing web service..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000 -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "   ✓ Web service is responding on port 8000" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Web service is not responding" -ForegroundColor Red
    Write-Host "   → Check logs: docker-compose logs web" -ForegroundColor Yellow
}
Write-Host ""

# Check migrations
Write-Host "7. Checking Django migrations..." -ForegroundColor Yellow
try {
    docker-compose exec -T web python manage.py showmigrations 2>$null
} catch {
    Write-Host "   Could not check migrations" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Verification Complete" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  - Access app: http://localhost:8000"
Write-Host "  - View logs: docker-compose logs -f"
Write-Host "  - Create superuser: docker-compose exec web python manage.py createsuperuser"
Write-Host ""