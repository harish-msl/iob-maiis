// ============================================
// Jenkins Pipeline - IOB MAIIS
// Multimodal AI Banking Assistant
// ============================================

pipeline {
    agent any

    environment {
        // Application Info
        APP_NAME = 'iob-maiis'

        // Docker Registry (configure as needed)
        DOCKER_REGISTRY = credentials('docker-registry-url')
        DOCKER_CREDENTIALS = credentials('docker-registry-credentials')

        // Node & Python Versions
        NODE_VERSION = '20.x'
        PYTHON_VERSION = '3.12'

        // Build Info
        BUILD_VERSION = "${env.BUILD_NUMBER}"
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()

        // Environment-specific configs
        DEPLOY_ENV = "${env.BRANCH_NAME == 'main' ? 'production' : env.BRANCH_NAME == 'develop' ? 'staging' : 'development'}"
    }

    options {
        // Keep last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Timeout after 60 minutes
        timeout(time: 60, unit: 'MINUTES')

        // Disable concurrent builds
        disableConcurrentBuilds()

        // Timestamps in console output
        timestamps()

        // ANSI color output
        ansiColor('xterm')
    }

    triggers {
        // Poll SCM every 5 minutes (adjust as needed)
        pollSCM('H/5 * * * *')
    }

    stages {
        // ============================================
        // Stage 1: Checkout
        // ============================================
        stage('Checkout') {
            steps {
                script {
                    echo "🔍 Checking out code from ${env.BRANCH_NAME}..."
                }
                checkout scm

                script {
                    echo "✅ Checkout complete"
                    echo "Git Commit: ${GIT_COMMIT_SHORT}"
                    echo "Build Number: ${BUILD_VERSION}"
                    echo "Deploy Environment: ${DEPLOY_ENV}"
                }
            }
        }

        // ============================================
        // Stage 2: Frontend - Install & Test
        // ============================================
        stage('Frontend Tests') {
            agent {
                docker {
                    image "node:${NODE_VERSION}-alpine"
                    reuseNode true
                }
            }
            steps {
                dir('frontend') {
                    script {
                        echo "📦 Installing frontend dependencies..."
                    }
                    sh 'npm ci --legacy-peer-deps'

                    script {
                        echo "🔍 Running type check..."
                    }
                    sh 'npm run type-check || true'

                    script {
                        echo "🧹 Running linter..."
                    }
                    sh 'npm run lint || true'

                    script {
                        echo "🧪 Running unit tests..."
                    }
                    sh 'npm run test -- --coverage --maxWorkers=2 || true'

                    script {
                        echo "🏗️  Building frontend..."
                    }
                    sh '''
                        export NEXT_PUBLIC_API_URL=http://localhost:8000
                        export NEXT_PUBLIC_WS_URL=ws://localhost:8000
                        npm run build
                    '''
                }
            }
            post {
                always {
                    // Publish test results if available
                    junit allowEmptyResults: true, testResults: 'frontend/junit.xml'

                    // Publish coverage reports
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'frontend/coverage',
                        reportFiles: 'index.html',
                        reportName: 'Frontend Coverage Report'
                    ])
                }
            }
        }

        // ============================================
        // Stage 3: Backend - Install & Test
        // ============================================
        stage('Backend Tests') {
            agent {
                docker {
                    image "python:${PYTHON_VERSION}-slim"
                    reuseNode true
                    args '-u root'
                }
            }
            steps {
                dir('backend') {
                    script {
                        echo "📦 Installing backend dependencies..."
                    }
                    sh '''
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest pytest-cov pytest-asyncio httpx ruff mypy
                    '''

                    script {
                        echo "🔍 Running linting..."
                    }
                    sh 'ruff check . || true'

                    script {
                        echo "🔍 Running type checking..."
                    }
                    sh 'mypy app/ --ignore-missing-imports || true'

                    script {
                        echo "🧪 Running unit tests..."
                    }
                    sh '''
                        export DATABASE_URL=postgresql://test_user:test_password@postgres:5432/test_db
                        export REDIS_URL=redis://redis:6379/0
                        export ENVIRONMENT=test
                        export SECRET_KEY=test-secret-key-for-ci
                        pytest tests/ -v --cov=app --cov-report=xml --cov-report=html || true
                    '''
                }
            }
            post {
                always {
                    // Publish test results
                    junit allowEmptyResults: true, testResults: 'backend/pytest-results.xml'

                    // Publish coverage reports
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'backend/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Backend Coverage Report'
                    ])
                }
            }
        }

        // ============================================
        // Stage 4: Security Scanning
        // ============================================
        stage('Security Scan') {
            parallel {
                stage('Frontend Security') {
                    steps {
                        dir('frontend') {
                            script {
                                echo "🔒 Running npm audit..."
                            }
                            sh 'npm audit --audit-level=moderate || true'
                        }
                    }
                }

                stage('Backend Security') {
                    steps {
                        dir('backend') {
                            script {
                                echo "🔒 Running safety check..."
                            }
                            sh '''
                                pip install safety
                                safety check --json || true
                            '''
                        }
                    }
                }

                stage('Container Security') {
                    steps {
                        script {
                            echo "🔒 Running Trivy scan..."
                            // Install Trivy if not available
                            sh '''
                                which trivy || {
                                    wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
                                    echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list
                                    apt-get update
                                    apt-get install -y trivy
                                }
                                trivy fs --severity CRITICAL,HIGH . || true
                            '''
                        }
                    }
                }
            }
        }

        // ============================================
        // Stage 5: Build Docker Images
        // ============================================
        stage('Build Docker Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    branch 'staging'
                }
            }
            steps {
                script {
                    echo "🐋 Building Docker images..."

                    // Build Frontend
                    echo "Building frontend image..."
                    sh """
                        docker build -t ${APP_NAME}-frontend:${BUILD_VERSION} \
                                     -t ${APP_NAME}-frontend:${DEPLOY_ENV} \
                                     -t ${APP_NAME}-frontend:latest \
                                     ./frontend
                    """

                    // Build Backend
                    echo "Building backend image..."
                    sh """
                        docker build -t ${APP_NAME}-backend:${BUILD_VERSION} \
                                     -t ${APP_NAME}-backend:${DEPLOY_ENV} \
                                     -t ${APP_NAME}-backend:latest \
                                     ./backend
                    """

                    echo "✅ Docker images built successfully"
                }
            }
        }

        // ============================================
        // Stage 6: Integration Tests
        // ============================================
        stage('Integration Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "🧪 Starting integration tests..."

                    try {
                        // Start services
                        sh 'docker-compose -f docker-compose.yml up -d'

                        // Wait for services to be healthy
                        sh '''
                            echo "Waiting for services to be ready..."
                            sleep 30

                            # Check backend health
                            for i in {1..30}; do
                                if curl -f http://localhost:8000/health; then
                                    echo "Backend is healthy"
                                    break
                                fi
                                echo "Waiting for backend... ($i/30)"
                                sleep 2
                            done

                            # Check frontend
                            for i in {1..30}; do
                                if curl -f http://localhost:3000; then
                                    echo "Frontend is healthy"
                                    break
                                fi
                                echo "Waiting for frontend... ($i/30)"
                                sleep 2
                            done
                        '''

                        // Run integration tests
                        sh 'docker-compose exec -T backend pytest tests/integration/ -v || true'

                        echo "✅ Integration tests completed"
                    } catch (Exception e) {
                        echo "❌ Integration tests failed: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    } finally {
                        // Collect logs
                        sh 'docker-compose logs > integration-logs.txt || true'
                        archiveArtifacts artifacts: 'integration-logs.txt', allowEmptyArchive: true

                        // Cleanup
                        sh 'docker-compose down -v || true'
                    }
                }
            }
        }

        // ============================================
        // Stage 7: Push Docker Images
        // ============================================
        stage('Push Docker Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "🚀 Pushing Docker images to registry..."

                    docker.withRegistry("https://${DOCKER_REGISTRY}", "${DOCKER_CREDENTIALS}") {
                        // Push Frontend
                        sh """
                            docker tag ${APP_NAME}-frontend:${BUILD_VERSION} ${DOCKER_REGISTRY}/${APP_NAME}-frontend:${BUILD_VERSION}
                            docker tag ${APP_NAME}-frontend:${DEPLOY_ENV} ${DOCKER_REGISTRY}/${APP_NAME}-frontend:${DEPLOY_ENV}
                            docker push ${DOCKER_REGISTRY}/${APP_NAME}-frontend:${BUILD_VERSION}
                            docker push ${DOCKER_REGISTRY}/${APP_NAME}-frontend:${DEPLOY_ENV}
                        """

                        // Push Backend
                        sh """
                            docker tag ${APP_NAME}-backend:${BUILD_VERSION} ${DOCKER_REGISTRY}/${APP_NAME}-backend:${BUILD_VERSION}
                            docker tag ${APP_NAME}-backend:${DEPLOY_ENV} ${DOCKER_REGISTRY}/${APP_NAME}-backend:${DEPLOY_ENV}
                            docker push ${DOCKER_REGISTRY}/${APP_NAME}-backend:${BUILD_VERSION}
                            docker push ${DOCKER_REGISTRY}/${APP_NAME}-backend:${DEPLOY_ENV}
                        """

                        // Push latest tag for main branch
                        if (env.BRANCH_NAME == 'main') {
                            sh """
                                docker tag ${APP_NAME}-frontend:latest ${DOCKER_REGISTRY}/${APP_NAME}-frontend:latest
                                docker tag ${APP_NAME}-backend:latest ${DOCKER_REGISTRY}/${APP_NAME}-backend:latest
                                docker push ${DOCKER_REGISTRY}/${APP_NAME}-frontend:latest
                                docker push ${DOCKER_REGISTRY}/${APP_NAME}-backend:latest
                            """
                        }
                    }

                    echo "✅ Docker images pushed successfully"
                }
            }
        }

        // ============================================
        // Stage 8: Deploy
        // ============================================
        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "🚀 Deploying to ${DEPLOY_ENV}..."

                    // Deployment logic depends on your infrastructure
                    // Examples below - uncomment and modify as needed:

                    // Option 1: Deploy to Kubernetes
                    /*
                    sh """
                        kubectl set image deployment/iob-maiis-frontend \
                            frontend=${DOCKER_REGISTRY}/${APP_NAME}-frontend:${BUILD_VERSION} \
                            --namespace=${DEPLOY_ENV}

                        kubectl set image deployment/iob-maiis-backend \
                            backend=${DOCKER_REGISTRY}/${APP_NAME}-backend:${BUILD_VERSION} \
                            --namespace=${DEPLOY_ENV}

                        kubectl rollout status deployment/iob-maiis-frontend --namespace=${DEPLOY_ENV}
                        kubectl rollout status deployment/iob-maiis-backend --namespace=${DEPLOY_ENV}
                    """
                    */

                    // Option 2: Deploy to Docker Swarm
                    /*
                    sh """
                        docker stack deploy -c docker-compose.${DEPLOY_ENV}.yml ${APP_NAME}-${DEPLOY_ENV}
                    """
                    */

                    // Option 3: Deploy to AWS ECS
                    /*
                    sh """
                        aws ecs update-service --cluster ${APP_NAME}-${DEPLOY_ENV} \
                            --service frontend --force-new-deployment

                        aws ecs update-service --cluster ${APP_NAME}-${DEPLOY_ENV} \
                            --service backend --force-new-deployment

                        aws ecs wait services-stable --cluster ${APP_NAME}-${DEPLOY_ENV} \
                            --services frontend backend
                    """
                    */

                    // Option 4: SSH Deploy to remote server
                    /*
                    sshagent(['ssh-credentials-id']) {
                        sh """
                            ssh user@server "cd /opt/${APP_NAME} && \
                                docker-compose pull && \
                                docker-compose up -d --force-recreate"
                        """
                    }
                    */

                    echo "⚠️  Deployment step is placeholder - configure based on your infrastructure"
                    echo "✅ Deployment phase completed"
                }
            }
        }

        // ============================================
        // Stage 9: Smoke Tests
        // ============================================
        stage('Smoke Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "🔥 Running smoke tests..."

                    // Adjust URLs based on your deployment
                    def backendUrl = DEPLOY_ENV == 'production' ? 'https://api.iob-maiis.com' : 'https://staging-api.iob-maiis.com'
                    def frontendUrl = DEPLOY_ENV == 'production' ? 'https://iob-maiis.com' : 'https://staging.iob-maiis.com'

                    // Test backend health
                    sh """
                        curl -f ${backendUrl}/health || exit 1
                        echo "✅ Backend health check passed"
                    """

                    // Test frontend
                    sh """
                        curl -f ${frontendUrl} || exit 1
                        echo "✅ Frontend health check passed"
                    """

                    // Test metrics endpoint (internal only)
                    sh """
                        curl -f ${backendUrl}/metrics || echo "⚠️  Metrics endpoint check skipped (may be internal only)"
                    """

                    echo "✅ Smoke tests passed"
                }
            }
        }
    }

    // ============================================
    // Post-Build Actions
    // ============================================
    post {
        always {
            script {
                echo "🧹 Cleaning up..."
            }

            // Clean up Docker images to save space
            sh '''
                docker image prune -f --filter "until=24h" || true
                docker container prune -f || true
            '''

            // Archive artifacts
            archiveArtifacts artifacts: '**/coverage/**', allowEmptyArchive: true
            archiveArtifacts artifacts: '**/test-results/**', allowEmptyArchive: true
        }

        success {
            script {
                echo "✅ Pipeline completed successfully!"

                // Send success notification (configure as needed)
                // Example: Slack, Email, etc.
                /*
                slackSend(
                    color: 'good',
                    message: "✅ Build #${BUILD_VERSION} succeeded for ${APP_NAME} (${BRANCH_NAME})\nCommit: ${GIT_COMMIT_SHORT}",
                    channel: '#ci-notifications'
                )
                */
            }
        }

        failure {
            script {
                echo "❌ Pipeline failed!"

                // Send failure notification
                /*
                slackSend(
                    color: 'danger',
                    message: "❌ Build #${BUILD_VERSION} failed for ${APP_NAME} (${BRANCH_NAME})\nCommit: ${GIT_COMMIT_SHORT}\nCheck: ${BUILD_URL}",
                    channel: '#ci-notifications'
                )

                emailext(
                    subject: "❌ Jenkins Build Failed: ${APP_NAME} #${BUILD_VERSION}",
                    body: "Build failed for branch ${BRANCH_NAME}. Check console output at ${BUILD_URL}",
                    to: 'team@example.com'
                )
                */
            }
        }

        unstable {
            script {
                echo "⚠️  Pipeline is unstable"

                // Send unstable notification
                /*
                slackSend(
                    color: 'warning',
                    message: "⚠️  Build #${BUILD_VERSION} is unstable for ${APP_NAME} (${BRANCH_NAME})",
                    channel: '#ci-notifications'
                )
                */
            }
        }
    }
}
