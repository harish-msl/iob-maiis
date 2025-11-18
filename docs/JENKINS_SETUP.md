# Jenkins Setup and Configuration Guide

## Overview

This guide covers setting up Jenkins CI/CD pipeline for the IOB MAIIS (Multimodal AI-Enabled Information System) project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Jenkins Installation](#jenkins-installation)
3. [Initial Configuration](#initial-configuration)
4. [Required Plugins](#required-plugins)
5. [Credentials Setup](#credentials-setup)
6. [Pipeline Configuration](#pipeline-configuration)
7. [Environment Variables](#environment-variables)
8. [Webhook Setup](#webhook-setup)
9. [Testing the Pipeline](#testing-the-pipeline)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Server**: Linux (Ubuntu 20.04+ recommended) or Windows Server
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: 2+ cores
- **Disk**: 50GB+ free space
- **Java**: OpenJDK 11 or 17

### Required Tools
- Docker & Docker Compose
- Git
- Node.js (for frontend builds)
- Python 3.12+ (for backend builds)

---

## Jenkins Installation

### Option 1: Install on Ubuntu/Debian

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Java
sudo apt install -y openjdk-17-jdk

# Add Jenkins repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install Jenkins
sudo apt update
sudo apt install -y jenkins

# Start Jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins

# Check status
sudo systemctl status jenkins
```

### Option 2: Docker Installation (Recommended for Dev)

```bash
# Create volume for Jenkins data
docker volume create jenkins_home

# Run Jenkins in Docker
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --restart unless-stopped \
  jenkins/jenkins:lts-jdk17

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Option 3: Docker Compose

Create `jenkins-docker-compose.yml`:

```yaml
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts-jdk17
    container_name: jenkins
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JENKINS_OPTS=--prefix=/jenkins
    restart: unless-stopped

volumes:
  jenkins_home:
    driver: local
```

Start Jenkins:
```bash
docker-compose -f jenkins-docker-compose.yml up -d
```

### Access Jenkins

1. Open browser: `http://your-server-ip:8080`
2. Enter initial admin password
3. Install suggested plugins
4. Create admin user
5. Configure Jenkins URL

---

## Initial Configuration

### 1. Install Required Tools in Jenkins Container (if using Docker)

```bash
# Enter Jenkins container
docker exec -it -u root jenkins bash

# Install Docker CLI
apt-get update
apt-get install -y docker.io

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install Python
apt-get install -y python3 python3-pip

# Exit container
exit
```

### 2. Configure Jenkins Security

1. Navigate to: **Manage Jenkins** > **Configure Global Security**
2. Enable **CSRF Protection**
3. Configure **Authorization**: Matrix-based security
4. Set up **Agent → Controller Security**

### 3. Configure System Settings

Navigate to: **Manage Jenkins** > **Configure System**

- **Jenkins URL**: Set your Jenkins URL
- **# of executors**: 2-4 (based on server capacity)
- **Environment variables**: Add global variables if needed

---

## Required Plugins

### Essential Plugins

Install via: **Manage Jenkins** > **Manage Plugins** > **Available**

1. **Git Plugin** - Git integration
2. **Pipeline** - Pipeline support
3. **Docker Plugin** - Docker integration
4. **Docker Pipeline** - Docker commands in pipeline
5. **Blue Ocean** - Modern UI (optional but recommended)
6. **Timestamper** - Add timestamps to console output
7. **AnsiColor** - ANSI color support
8. **Workspace Cleanup** - Clean workspace before builds
9. **Credentials Binding** - Bind credentials to environment variables
10. **SSH Agent** - SSH key management
11. **NodeJS Plugin** - Node.js installation management
12. **HTML Publisher** - Publish HTML reports
13. **JUnit Plugin** - Test results
14. **Cobertura Plugin** - Code coverage
15. **Slack Notification** - Slack integration (optional)
16. **Email Extension** - Email notifications

### Install Plugins via CLI

```bash
# List of plugins
PLUGINS="git workflow-aggregator docker-workflow blueocean timestamper ansicolor ws-cleanup credentials-binding ssh-agent nodejs htmlpublisher junit cobertura"

# Install
docker exec jenkins jenkins-plugin-cli --plugins $PLUGINS
```

### Restart Jenkins

```bash
# If using Docker
docker restart jenkins

# If installed on system
sudo systemctl restart jenkins
```

---

## Credentials Setup

Navigate to: **Manage Jenkins** > **Manage Credentials** > **(global)** > **Add Credentials**

### 1. Docker Registry Credentials

- **Kind**: Username with password
- **Scope**: Global
- **ID**: `docker-registry-credentials`
- **Username**: Your registry username
- **Password**: Your registry password/token
- **Description**: Docker Registry Credentials

### 2. Docker Registry URL

- **Kind**: Secret text
- **Scope**: Global
- **ID**: `docker-registry-url`
- **Secret**: `registry.example.com` (your registry URL)
- **Description**: Docker Registry URL

### 3. GitHub Credentials (for private repos)

- **Kind**: Username with password (or Personal Access Token)
- **Scope**: Global
- **ID**: `github-credentials`
- **Username**: Your GitHub username
- **Password**: Personal Access Token
- **Description**: GitHub Access

### 4. SSH Credentials (for deployment)

- **Kind**: SSH Username with private key
- **Scope**: Global
- **ID**: `ssh-credentials-id`
- **Username**: deployment user
- **Private Key**: Enter directly or from file
- **Description**: SSH Deploy Key

### 5. AWS Credentials (if using AWS)

- **Kind**: AWS Credentials
- **Scope**: Global
- **ID**: `aws-credentials`
- **Access Key ID**: Your AWS access key
- **Secret Access Key**: Your AWS secret key
- **Description**: AWS Deployment Credentials

### 6. Additional Secrets

Add any other credentials needed:
- Sentry DSN
- API keys
- Database credentials
- Slack webhook URL

---

## Pipeline Configuration

### Create Pipeline Job

1. **New Item** > Enter name: `iob-maiis-pipeline`
2. Select **Pipeline**
3. Click **OK**

### Configure Pipeline

#### General Settings
- **Description**: IOB MAIIS CI/CD Pipeline
- **Discard old builds**: Keep last 10 builds
- **GitHub project**: `https://github.com/harish-msl/iob-maiis`

#### Build Triggers
- **GitHub hook trigger for GITScm polling** (if using webhooks)
- OR **Poll SCM**: `H/5 * * * *` (every 5 minutes)

#### Pipeline Definition
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/harish-msl/iob-maiis.git`
- **Credentials**: Select GitHub credentials if private repo
- **Branches to build**: `*/main` or `*/develop`
- **Script Path**: `Jenkinsfile`

### Multi-Branch Pipeline (Recommended)

For automatic branch detection:

1. **New Item** > Enter name: `iob-maiis-multibranch`
2. Select **Multibranch Pipeline**
3. Click **OK**

Configure:
- **Branch Sources**: Git
- **Project Repository**: `https://github.com/harish-msl/iob-maiis.git`
- **Discover branches**: All branches
- **Build Configuration**: by Jenkinsfile
- **Scan Multibranch Pipeline Triggers**: Periodically (e.g., 5 minutes)

---

## Environment Variables

### Global Environment Variables

**Manage Jenkins** > **Configure System** > **Global properties** > **Environment variables**

Add:
```
DOCKER_REGISTRY=registry.example.com
NODE_VERSION=20.x
PYTHON_VERSION=3.12
```

### Pipeline-Specific Variables

Edit in `Jenkinsfile`:

```groovy
environment {
    DOCKER_REGISTRY = credentials('docker-registry-url')
    DOCKER_CREDENTIALS = credentials('docker-registry-credentials')
    APP_NAME = 'iob-maiis'
}
```

---

## Webhook Setup

### GitHub Webhook Configuration

1. Go to GitHub repository settings
2. Navigate to **Settings** > **Webhooks** > **Add webhook**
3. Configure:
   - **Payload URL**: `http://your-jenkins-url:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Secret**: (optional) Generate a secret token
   - **Events**: Just the push event OR Send me everything
   - **Active**: ✓

4. Click **Add webhook**

### Test Webhook

1. Make a commit and push to repository
2. Check webhook delivery in GitHub
3. Verify build triggered in Jenkins

---

## Testing the Pipeline

### Manual Trigger

1. Navigate to your pipeline job
2. Click **Build Now**
3. Monitor console output
4. Check Blue Ocean view for visual feedback

### Expected Pipeline Flow

```
Checkout → Frontend Tests → Backend Tests → Security Scan → Build Docker Images → 
Integration Tests → Push Images → Deploy → Smoke Tests
```

### Verify Each Stage

1. **Checkout**: Code pulled successfully
2. **Frontend Tests**: npm install, lint, type-check, tests pass
3. **Backend Tests**: pip install, linting, type-checking, tests pass
4. **Security Scan**: npm audit, safety check, trivy scan
5. **Build Docker**: Images built successfully
6. **Integration Tests**: Services start, health checks pass
7. **Push Images**: Images pushed to registry
8. **Deploy**: Deployment executed (configure based on your setup)
9. **Smoke Tests**: Production health checks pass

---

## Customizing the Pipeline

### Modify Jenkinsfile

The provided `Jenkinsfile` includes placeholders for deployment. Choose your deployment method:

#### Option 1: Kubernetes Deployment

Uncomment in Deploy stage:
```groovy
sh """
    kubectl set image deployment/iob-maiis-frontend \
        frontend=${DOCKER_REGISTRY}/${APP_NAME}-frontend:${BUILD_VERSION} \
        --namespace=${DEPLOY_ENV}
"""
```

#### Option 2: Docker Swarm

```groovy
sh """
    docker stack deploy -c docker-compose.${DEPLOY_ENV}.yml ${APP_NAME}-${DEPLOY_ENV}
"""
```

#### Option 3: SSH Deployment

```groovy
sshagent(['ssh-credentials-id']) {
    sh """
        ssh user@server "cd /opt/${APP_NAME} && \
            docker-compose pull && \
            docker-compose up -d --force-recreate"
    """
}
```

#### Option 4: AWS ECS

```groovy
sh """
    aws ecs update-service --cluster ${APP_NAME}-${DEPLOY_ENV} \
        --service frontend --force-new-deployment
"""
```

---

## Notifications

### Slack Notifications

1. Install **Slack Notification Plugin**
2. Configure Slack workspace integration
3. Add to Jenkinsfile:

```groovy
post {
    success {
        slackSend(
            color: 'good',
            message: "✅ Build #${BUILD_VERSION} succeeded for ${APP_NAME}",
            channel: '#ci-notifications'
        )
    }
    failure {
        slackSend(
            color: 'danger',
            message: "❌ Build #${BUILD_VERSION} failed for ${APP_NAME}",
            channel: '#ci-notifications'
        )
    }
}
```

### Email Notifications

```groovy
post {
    failure {
        emailext(
            subject: "❌ Jenkins Build Failed: ${APP_NAME} #${BUILD_VERSION}",
            body: "Build failed. Check: ${BUILD_URL}",
            to: 'team@example.com'
        )
    }
}
```

---

## Monitoring and Maintenance

### View Build History

- **Classic UI**: Job page shows build history
- **Blue Ocean**: Visual pipeline runs

### Monitor Jenkins Health

- **Manage Jenkins** > **System Information**
- Check disk space usage
- Monitor build queue
- Review system logs

### Backup Jenkins

```bash
# Backup Jenkins home directory
tar -czf jenkins-backup-$(date +%Y%m%d).tar.gz /var/jenkins_home/

# Or if using Docker
docker run --rm -v jenkins_home:/data -v $(pwd):/backup \
    alpine tar czf /backup/jenkins-backup-$(date +%Y%m%d).tar.gz /data
```

### Restore Jenkins

```bash
# Restore from backup
tar -xzf jenkins-backup-YYYYMMDD.tar.gz -C /var/jenkins_home/
```

### Update Jenkins

```bash
# If using Docker
docker pull jenkins/jenkins:lts-jdk17
docker-compose -f jenkins-docker-compose.yml up -d

# If installed on system
sudo apt update
sudo apt upgrade jenkins
```

---

## Troubleshooting

### Build Fails at Checkout

**Problem**: Permission denied or repository not found

**Solution**:
- Verify GitHub credentials are configured
- Check repository URL is correct
- Ensure Jenkins has network access to GitHub

### Docker Permission Denied

**Problem**: Cannot connect to Docker daemon

**Solution**:
```bash
# Add Jenkins user to docker group (if not using Docker)
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins

# Or in Docker, ensure socket is mounted
-v /var/run/docker.sock:/var/run/docker.sock
```

### Out of Memory Errors

**Problem**: Java heap space errors

**Solution**:
```bash
# Increase Jenkins memory
# Edit /etc/default/jenkins (or Docker command)
JAVA_ARGS="-Xmx2048m -Xms512m"

# Restart Jenkins
sudo systemctl restart jenkins
```

### Integration Tests Fail

**Problem**: Services not ready in time

**Solution**:
- Increase sleep time in wait loop
- Add more robust health checks
- Check Docker Compose logs

### Workspace Cleanup Issues

**Problem**: Disk space running out

**Solution**:
```groovy
// Add to pipeline
options {
    skipDefaultCheckout()
}

// Manual cleanup
sh 'git clean -fdx'
```

### Pipeline Syntax Errors

**Problem**: Jenkinsfile syntax issues

**Solution**:
- Use **Pipeline Syntax** tool in Jenkins
- Validate Groovy syntax
- Check for proper quoting and escaping

---

## Performance Optimization

### Parallel Execution

```groovy
stage('Tests') {
    parallel {
        stage('Frontend') { ... }
        stage('Backend') { ... }
        stage('Security') { ... }
    }
}
```

### Use Docker Cache

```groovy
docker.build("${APP_NAME}:${VERSION}", "--cache-from ${APP_NAME}:latest .")
```

### Limit Concurrent Builds

```groovy
options {
    disableConcurrentBuilds()
}
```

### Clean Old Images

```groovy
post {
    always {
        sh 'docker image prune -f --filter "until=24h"'
    }
}
```

---

## Security Best Practices

1. **Use Credentials Plugin** - Never hardcode secrets
2. **Enable CSRF Protection** - Prevent cross-site attacks
3. **Restrict Access** - Use matrix-based security
4. **Regular Updates** - Keep Jenkins and plugins updated
5. **Audit Logs** - Enable and review audit logs
6. **Limit Permissions** - Principle of least privilege
7. **Secure Jenkins URL** - Use HTTPS
8. **Scan Dependencies** - Use security scanning tools

---

## Next Steps

1. ✅ Install Jenkins
2. ✅ Configure required plugins
3. ✅ Set up credentials
4. ✅ Create pipeline job
5. ✅ Configure webhooks
6. ⏳ Test pipeline with sample build
7. ⏳ Configure notifications
8. ⏳ Set up backup strategy
9. ⏳ Document deployment process
10. ⏳ Train team on Jenkins usage

---

## Additional Resources

- **Jenkins Documentation**: https://www.jenkins.io/doc/
- **Pipeline Syntax**: https://www.jenkins.io/doc/book/pipeline/syntax/
- **Plugin Index**: https://plugins.jenkins.io/
- **Blue Ocean**: https://www.jenkins.io/doc/book/blueocean/
- **Best Practices**: https://www.jenkins.io/doc/book/pipeline/pipeline-best-practices/

---

## Support

For issues or questions:
1. Check Jenkins console logs
2. Review this documentation
3. Check Jenkins community forums
4. Review pipeline syntax documentation

---

**Last Updated**: 2025-01-17  
**Version**: 1.0.0  
**Maintainer**: IOB MAIIS DevOps Team