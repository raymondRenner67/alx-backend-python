# CI/CD Setup Guide

This guide covers setting up Jenkins and GitHub Actions for the messaging app.

## Table of Contents
- [Jenkins Setup](#jenkins-setup)
- [GitHub Actions Setup](#github-actions-setup)
- [Docker Hub Setup](#docker-hub-setup)

---

## Jenkins Setup

### Prerequisites
- Docker installed on your system
- GitHub account with repository access
- Docker Hub account

### 1. Run Jenkins in Docker

```powershell
# Create a network for Jenkins
docker network create jenkins

# Run Jenkins LTS container
docker run -d `
  --name jenkins `
  --restart=unless-stopped `
  --network jenkins `
  -p 8080:8080 -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts
```

### 2. Access Jenkins

1. Open browser: http://localhost:8080
2. Get initial admin password:
   ```powershell
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. Install suggested plugins
4. Create admin user

### 3. Install Required Plugins

Navigate to: **Manage Jenkins** → **Manage Plugins** → **Available**

Install these plugins:
- **Git plugin** (for GitHub integration)
- **Pipeline** (for Jenkinsfile support)
- **Docker Pipeline** (for Docker commands)
- **ShiningPanda** (for Python virtualenv)
- **Credentials Binding** (for secure credentials)
- **JUnit** (for test result publishing)
- **HTML Publisher** (for coverage reports)

### 4. Configure Credentials

#### GitHub Credentials
1. Go to **Manage Jenkins** → **Manage Credentials**
2. Click on **(global)** domain
3. **Add Credentials**
   - Kind: **Username with password**
   - Scope: **Global**
   - Username: Your GitHub username
   - Password: [GitHub Personal Access Token](https://github.com/settings/tokens)
   - ID: `github-credentials`
   - Description: GitHub Access Token

#### Docker Hub Credentials
1. **Add Credentials** (same location)
   - Kind: **Username with password**
   - Scope: **Global**
   - Username: Your Docker Hub username
   - Password: Your Docker Hub password
   - ID: `docker-hub-credentials`
   - Description: Docker Hub Credentials

### 5. Create Pipeline Job

1. **New Item** → Enter name: `messaging-app-pipeline`
2. Select **Pipeline** → **OK**
3. Under **Pipeline** section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/raymondRenner67/alx-backend-python.git`
   - Credentials: Select `github-credentials`
   - Branch: `*/main`
   - Script Path: `messaging_app/Jenkinsfile`
4. **Save**

### 6. Enable Docker in Jenkins Container

```powershell
# Install Docker CLI in Jenkins container
docker exec -u root jenkins apt-get update
docker exec -u root jenkins apt-get install -y docker.io
docker exec -u root jenkins usermod -aG docker jenkins
docker restart jenkins
```

### 7. Run Pipeline

1. Click **Build Now**
2. Monitor **Console Output**
3. View test results and coverage reports

---

## GitHub Actions Setup

### 1. Configure Repository Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:
- **DOCKER_USERNAME**: Your Docker Hub username
- **DOCKER_PASSWORD**: Your Docker Hub password or access token

### 2. Workflow Files

The following workflows are already configured:

#### CI Workflow (`.github/workflows/ci.yml`)
**Triggers:** Push/PR to `main` or `develop` branches

**Jobs:**
- Sets up MySQL 8.0 service
- Installs Python 3.10
- Runs flake8 code quality checks
- Executes pytest with coverage
- Uploads coverage to Codecov
- Uploads test results and HTML coverage as artifacts

#### Deployment Workflow (`.github/workflows/dep.yml`)
**Triggers:** Push to `main`, version tags (`v*`), manual trigger

**Jobs:**
- Builds Docker image
- Tags with multiple conventions (branch, SHA, semver, latest)
- Pushes to Docker Hub
- Uses build cache for faster builds

### 3. View Workflow Runs

1. Go to **Actions** tab in GitHub repository
2. Select workflow (CI or Deploy)
3. View run details, logs, and artifacts

### 4. Download Artifacts

After workflow completion:
1. Go to completed workflow run
2. Scroll to **Artifacts** section
3. Download:
   - `test-results` (JUnit XML)
   - `coverage-report` (HTML coverage)

---

## Docker Hub Setup

### 1. Create Repository

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Click **Create Repository**
3. Name: `messaging-app`
4. Visibility: **Public** or **Private**
5. **Create**

### 2. Generate Access Token (Recommended)

1. **Account Settings** → **Security**
2. **New Access Token**
3. Description: `GitHub Actions / Jenkins`
4. Access permissions: **Read, Write, Delete**
5. **Generate**
6. Copy token (shown only once)
7. Use this token as password in Jenkins/GitHub secrets

---

## Environment Variables

### For Jenkins Pipeline

Update `Jenkinsfile` if needed:
```groovy
environment {
    DOCKER_IMAGE = "your-dockerhub-username/messaging-app"
    DOCKER_CREDENTIALS = credentials('docker-hub-credentials')
}
```

### For GitHub Actions

Secrets are automatically injected:
- `${{ secrets.DOCKER_USERNAME }}`
- `${{ secrets.DOCKER_PASSWORD }}`

---

## Testing the Setup

### Test Jenkins Pipeline

```powershell
# Make a code change
cd messaging_app
# Edit a file...

# Commit and push
git add .
git commit -m "Test Jenkins pipeline"
git push origin main

# Check Jenkins: http://localhost:8080
```

### Test GitHub Actions

```powershell
# Same steps - push triggers both
git push origin main

# Check GitHub Actions:
# https://github.com/raymondRenner67/alx-backend-python/actions
```

### Verify Docker Image

```powershell
# After successful pipeline/workflow
docker pull your-dockerhub-username/messaging-app:latest
docker images | grep messaging-app
```

---

## Troubleshooting

### Jenkins Issues

**Issue:** "Permission denied" for Docker socket
```powershell
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

**Issue:** Python dependencies fail
- Install `python3-venv` in Jenkins container:
  ```powershell
  docker exec -u root jenkins apt-get install -y python3-venv
  ```

**Issue:** MySQL connection fails in tests
- Ensure MySQL service is running
- Check environment variables in Jenkinsfile

### GitHub Actions Issues

**Issue:** Docker push fails
- Verify Docker Hub credentials in repository secrets
- Check Docker Hub repository exists
- Ensure access token has write permissions

**Issue:** MySQL service not ready
- Increase health check retries in `ci.yml`
- Add longer wait time before tests

**Issue:** Coverage upload fails
- Set `fail_ci_if_error: false` in codecov action
- Check if Codecov token is needed for private repos

---

## Pipeline Stages Overview

### Jenkins Pipeline

1. **Checkout** - Clone repository
2. **Setup Python Environment** - Create venv and install deps
3. **Run Tests** - Execute pytest with coverage
4. **Generate Test Report** - Publish JUnit and HTML reports
5. **Build Docker Image** - Build and tag image
6. **Push Docker Image** - Push to Docker Hub

### GitHub Actions CI

1. **Checkout code**
2. **Setup Python 3.10**
3. **Install dependencies**
4. **Code quality checks** (flake8)
5. **Run tests** with MySQL service
6. **Upload coverage** to Codecov
7. **Upload artifacts**

### GitHub Actions Deploy

1. **Checkout code**
2. **Setup Docker Buildx**
3. **Login to Docker Hub**
4. **Build and push** with caching
5. **Verify image**

---

## Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [coverage.py](https://coverage.readthedocs.io/)

---

## Next Steps

1. ✅ Set up Jenkins with Docker
2. ✅ Configure Jenkins credentials
3. ✅ Create pipeline job
4. ✅ Add GitHub secrets for Actions
5. ✅ Test both CI/CD systems
6. 📝 Monitor builds and fix issues
7. 📝 Optimize pipeline performance
8. 📝 Add deployment to Kubernetes (future)