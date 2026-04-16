# Jenkins Pipeline Guide for MediFlow-Elite

## Table of Contents
1. [Pipeline Basics](#pipeline-basics)
2. [Declarative Pipeline Example](#declarative-pipeline-example)
3. [MediFlow-Elite Pipeline](#mediflow-elite-pipeline)
4. [Pipeline Best Practices](#pipeline-best-practices)
5. [Common Issues & Solutions](#common-issues--solutions)

---

## Pipeline Basics

### What is a Jenkins Pipeline?

A Jenkins Pipeline is a suite of plugins that supports implementing and integrating continuous delivery pipelines into Jenkins. It provides an extensible set of tools for modeling simple-to-complex delivery pipelines.

**Key Benefits:**
- **Version Control**: Pipeline code is stored in your repository
- **Durability**: Pipelines survive Jenkins restarts
- **Pausing**: Pipelines can pause and wait for human input
- **Versatility**: Supports complex logic, parallel execution, conditional steps

### Pipeline Syntax

Jenkins supports two syntaxes:

1. **Declarative Pipeline** (recommended for beginners)
   - Easier to read
   - Limited flexibility
   - Preferred for simple to moderate workflows

2. **Scripted Pipeline** (more powerful)
   - Full Groovy syntax
   - Maximum flexibility
   - Steeper learning curve

---

## Declarative Pipeline Example

### Basic Structure

```groovy
pipeline {
    agent any                          // Where to run the pipeline
    
    options {
        timeout(time: 1, unit: 'HOURS')  // Timeout safety
        timestamps()                      // Add timestamps to console output
    }
    
    environment {
        // Define global environment variables
        BUILD_ID = "${BUILD_NUMBER}"
        PROJECT_NAME = "mediflow-elite"
    }
    
    stages {
        stage('Stage Name') {
            steps {
                // Commands to execute
                echo 'Building...'
            }
        }
    }
    
    post {
        // Actions after all stages (always runs)
        always {
            junit testResults: '**/test-results.xml'  // Publish test results
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

---

## MediFlow-Elite Pipeline

### Complete CI/CD Pipeline for MediFlow-Elite

Create a new file in your repository root: `Jenkinsfile`

```groovy
// ============================================================================
// Jenkins Pipeline for MediFlow-Elite Hospital Management Platform
// ============================================================================

pipeline {
    agent any
    
    // ======================== OPTIONS ========================
    options {
        // Keep only last 30 builds
        buildDiscarder(logRotator(numToKeepStr: '30'))
        
        // Timeout after 1 hour
        timeout(time: 1, unit: 'HOURS')
        
        // Add timestamps to console output
        timestamps()
        
        // Disable concurrent builds
        disableConcurrentBuilds()
    }
    
    // ======================== ENVIRONMENT ========================
    environment {
        // Global environment variables
        PYTHON_VERSION = '3.10'
        DJANGO_SETTINGS = 'config.settings.production'
        PROJECT_DIR = "${WORKSPACE}/MediFlow-Hospital-Management-Platform"
        DOCKER_REGISTRY = 'docker.io'
        IMAGE_NAME = 'mediflow-elite'
        IMAGE_TAG = "${BUILD_NUMBER}"
        
        // AWS Configuration (store credentials in Jenkins)
        AWS_DEFAULT_REGION = 'us-east-1'
        AWS_CREDENTIALS = credentials('aws-credentials')
    }
    
    // ======================== TRIGGERS ========================
    triggers {
        // Poll SCM every 15 minutes
        pollSCM('H/15 * * * *')
        
        // Or use webhook trigger (GitHub/GitLab)
        // githubPush()
    }
    
    // ======================== PARAMETERS ========================
    parameters {
        string(
            name: 'ENVIRONMENT',
            defaultValue: 'staging',
            description: 'Deployment environment (dev, staging, production)',
            trim: true
        )
        booleanParam(
            name: 'RUN_SECURITY_TESTS',
            defaultValue: true,
            description: 'Run security scans'
        )
    }
    
    // ======================== STAGES ========================
    stages {
        // -------- Stage 1: Checkout --------
        stage('Checkout') {
            steps {
                echo '===== Checking out source code ====='
                checkout scm
                sh 'git log --oneline -1'
            }
        }
        
        // -------- Stage 2: Build Setup --------
        stage('Build Setup') {
            steps {
                echo '===== Setting up build environment ====='
                
                // Create virtual environment
                sh '''
                    cd ${PROJECT_DIR}/hms
                    python${PYTHON_VERSION} -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r ../requirements.txt
                    pip list
                '''
            }
        }
        
        // -------- Stage 3: Code Quality --------
        stage('Code Quality') {
            parallel {
                // Linting with pylint
                stage('Linting') {
                    steps {
                        echo '===== Running Pylint ====='
                        sh '''
                            cd ${PROJECT_DIR}/hms
                            . venv/bin/activate
                            pylint --rcfile=.pylintrc accounts/ doctors/ patients/ bookings/ \
                                --exit-zero \
                                --output-format=json > pylint-report.json || true
                        '''
                    }
                }
                
                // Code formatting check with Black
                stage('Code Format') {
                    steps {
                        echo '===== Checking code format with Black ====='
                        sh '''
                            cd ${PROJECT_DIR}/hms
                            . venv/bin/activate
                            black --check accounts/ doctors/ patients/ bookings/ || true
                        '''
                    }
                }
                
                // Type checking with mypy
                stage('Type Check') {
                    steps {
                        echo '===== Running mypy type checker ====='
                        sh '''
                            cd ${PROJECT_DIR}/hms
                            . venv/bin/activate
                            mypy accounts/ doctors/ --ignore-missing-imports || true
                        '''
                    }
                }
            }
        }
        
        // -------- Stage 4: Unit Tests --------
        stage('Unit Tests') {
            steps {
                echo '===== Running Django unit tests ====='
                sh '''
                    cd ${PROJECT_DIR}/hms
                    . venv/bin/activate
                    python manage.py test \
                        --verbosity=2 \
                        --no-input \
                        --pdb-trace=no \
                        --keepdb \
                        --parallel 4 \
                        2>&1 | tee test-results.txt || true
                '''
            }
            post {
                always {
                    junit testResults: 'MediFlow-Hospital-Management-Platform/hms/test-results.xml',
                          skipPublishingChecks: true,
                          allowEmptyResults: true
                }
            }
        }
        
        // -------- Stage 5: Security Scans --------
        stage('Security Scans') {
            when {
                expression { params.RUN_SECURITY_TESTS == true }
            }
            parallel {
                // OWASP Dependency Check
                stage('Dependency Check') {
                    steps {
                        echo '===== Running OWASP Dependency Check ====='
                        sh '''
                            cd ${PROJECT_DIR}
                            # Install dependency-check if not present
                            if [ ! -d "dependency-check" ]; then
                                wget -q https://github.com/jeremylong/DependencyCheck_Builder/releases/download/v7.0.0/dependency-check_Linux_x64.sh
                                chmod +x dependency-check_Linux_x64.sh
                                ./dependency-check_Linux_x64.sh
                            fi
                            
                            # Run scan
                            ./dependency-check/bin/dependency-check.sh \
                                --project "MediFlow-Elite" \
                                --scan . \
                                --out dependency-check-report \
                                --format JSON \
                                --format HTML || true
                        '''
                    }
                }
                
                // Bandit for Python security
                stage('Bandit Security') {
                    steps {
                        echo '===== Running Bandit security scan ====='
                        sh '''
                            cd ${PROJECT_DIR}/hms
                            . venv/bin/activate
                            bandit -r accounts/ doctors/ patients/ bookings/ \
                                -f json -o bandit-report.json || true
                        '''
                    }
                }
                
                // SonarQube Code Quality
                stage('SonarQube') {
                    when {
                        expression { 
                            fileExists('sonar-project.properties') 
                        }
                    }
                    steps {
                        echo '===== Running SonarQube analysis ====='
                        sh '''
                            ./gradlew sonarqube \
                                -Dsonar.projectKey=mediflow-elite \
                                -Dsonar.host.url=http://sonarqube:9000 || true
                        '''
                    }
                }
            }
        }
        
        // -------- Stage 6: Build Artifacts --------
        stage('Build Artifacts') {
            steps {
                echo '===== Building application artifacts ====='
                sh '''
                    cd ${PROJECT_DIR}/hms
                    . venv/bin/activate
                    
                    # Static files collection
                    python manage.py collectstatic --noinput
                    
                    # Create distribution package
                    python -m pip install wheel
                    python setup.py bdist_wheel
                '''
            }
        }
        
        // -------- Stage 7: Docker Build --------
        stage('Build Docker Image') {
            when {
                branch 'main'  // Only on main branch
            }
            steps {
                echo '===== Building Docker image ====='
                sh '''
                    cd ${PROJECT_DIR}
                    
                    # Build Docker image
                    docker build \
                        -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest \
                        -f Dockerfile .
                    
                    # Show image info
                    docker images | grep ${IMAGE_NAME}
                '''
            }
        }
        
        // -------- Stage 8: Docker Security Scan --------
        stage('Docker Security Scan') {
            when {
                branch 'main'
            }
            steps {
                echo '===== Scanning Docker image for vulnerabilities ====='
                sh '''
                    # Using Trivy for container scanning
                    if ! command -v trivy &> /dev/null; then
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
                    fi
                    
                    trivy image \
                        --severity HIGH,CRITICAL \
                        --output trivy-report.json \
                        --format json \
                        ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} || true
                '''
            }
        }
        
        // -------- Stage 9: Push to Registry --------
        stage('Push Docker Image') {
            when {
                branch 'main'
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            environment {
                DOCKER_CREDS = credentials('docker-hub-credentials')
            }
            steps {
                echo '===== Pushing Docker image to registry ====='
                sh '''
                    echo ${DOCKER_CREDS_PSW} | docker login -u ${DOCKER_CREDS_USR} --password-stdin
                    
                    docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
                    
                    docker logout
                '''
            }
        }
        
        // -------- Stage 10: Deploy to Staging --------
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo '===== Deploying to staging environment ====='
                sh '''
                    cd ${PROJECT_DIR}
                    
                    # Deploy to AWS or your infrastructure
                    # Example using Ansible:
                    ansible-playbook deploy/staging-deploy.yml \
                        -i deploy/hosts.ini \
                        -e "version=${BUILD_NUMBER}"
                '''
            }
        }
        
        // -------- Stage 11: Deploy to Production --------
        stage('Deploy to Production') {
            when {
                branch 'main'
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
            }
            steps {
                echo '===== Deploying to production environment ====='
                sh '''
                    cd ${PROJECT_DIR}
                    
                    # Deploy to production
                    ansible-playbook deploy/prod-deploy.yml \
                        -i deploy/hosts.ini \
                        -e "version=${BUILD_NUMBER}"
                '''
            }
        }
        
        // -------- Stage 12: Smoke Tests --------
        stage('Smoke Tests') {
            when {
                expression {
                    currentBuild.result == null || currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo '===== Running smoke tests ====='
                sh '''
                    cd ${PROJECT_DIR}
                    . venv/bin/activate
                    
                    # Run smoke tests
                    python manage.py test tests/smoke --verbosity=2
                '''
            }
        }
    }
    
    // ======================== POST ACTIONS ========================
    post {
        always {
            echo '===== Cleaning up workspace ====='
            
            // Publish test results
            junit testResults: '**/test-results*.xml',
                  skipPublishingChecks: true,
                  allowEmptyResults: true
            
            // Archive logs and reports
            archiveArtifacts artifacts: '**/reports/**,**/logs/**',
                             allowEmptyArchive: true
            
            // Cleanup Docker images
            sh '''
                docker system prune -f --volumes || true
            '''
        }
        
        success {
            echo '✓ Pipeline completed successfully!'
            // Send success notification
            sh '''
                # Notify Slack (configure in Jenkins)
                curl -X POST -H 'Content-type: application/json' \
                    --data '{"text":"✓ MediFlow-Elite build #${BUILD_NUMBER} succeeded"}' \
                    ${SLACK_WEBHOOK_URL} || true
            '''
        }
        
        failure {
            echo '✗ Pipeline failed!'
            // Send failure notification
            sh '''
                curl -X POST -H 'Content-type: application/json' \
                    --data '{"text":"✗ MediFlow-Elite build #${BUILD_NUMBER} FAILED: ${BUILD_URL}"}' \
                    ${SLACK_WEBHOOK_URL} || true
            '''
        }
        
        unstable {
            echo '! Pipeline unstable (warnings but passed)'
        }
        
        cleanup {
            // Always cleanup
            deleteDir()
        }
    }
}
```

---

## Dockerfile for MediFlow-Elite

### File: `Dockerfile`

```dockerfile
# Multi-stage build for optimization

# ========== Stage 1: Builder ==========
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY MediFlow-Hospital-Management-Platform/requirements.txt .

# Create wheel files
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ========== Stage 2: Runtime ==========
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 django

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install Python packages from wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY MediFlow-Hospital-Management-Platform ./

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

# Run application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

## Pipeline Best Practices

### 1. **Use Declarative Syntax**
- Easier to maintain and understand
- Better IDE support
- Follows structure

### 2. **Keep Pipelines DRY (Don't Repeat Yourself)**
```groovy
// Create reusable functions
def runTests() {
    sh '''
        . venv/bin/activate
        python manage.py test
    '''
}

// Use in pipeline
stage('Test') {
    steps {
        script {
            runTests()
        }
    }
}
```

### 3. **Use Environment Variables**
```groovy
environment {
    // Global
    PROJECT_NAME = "mediflow"
}

stage('Example') {
    environment {
        // Stage-specific
        BUILD_ENV = "staging"
    }
    steps {
        echo "Building ${PROJECT_NAME} for ${BUILD_ENV}"
    }
}
```

### 4. **Implement Timeout**
```groovy
options {
    timeout(time: 30, unit: 'MINUTES')
}
```

### 5. **Use Parallel Execution**
```groovy
parallel {
    stage('Test 1') { steps { sh 'test1' } }
    stage('Test 2') { steps { sh 'test2' } }
    stage('Test 3') { steps { sh 'test3' } }
}
```

### 6. **Archive Artifacts**
```groovy
post {
    always {
        archiveArtifacts artifacts: 'dist/**,reports/**'
    }
}
```

### 7. **Credentials Management**
```groovy
// Define credentials in Jenkins
// Use them securely in pipeline
withCredentials([
    file(credentialsId: 'aws-credentials', variable: 'AWS_CREDS'),
    string(credentialsId: 'docker-token', variable: 'DOCKER_TOKEN')
]) {
    sh '''
        export AWS_SHARED_CREDENTIALS_FILE=${AWS_CREDS}
        echo ${DOCKER_TOKEN} | docker login -u user --password-stdin
    '''
}
```

---

## Common Issues & Solutions

### Issue: "Command not found" in Pipeline

```groovy
// Solution 1: Full path
sh '/usr/local/bin/docker --version'

// Solution 2: Activate environment
sh '''
    . venv/bin/activate
    python --version
'''
```

### Issue: Permission Denied

```groovy
// Solution: Run with sudo or proper permissions
sh 'sudo systemctl restart service' || true

// Or configure Jenkins user with sudo
```

### Issue: Out of Memory

```groovy
options {
    // Set higher timeout for memory-intensive tasks
    timeout(time: 60, unit: 'MINUTES')
}
```

### Issue: Tests Timeout

```groovy
stage('Tests') {
    options {
        timeout(time: 30, unit: 'MINUTES')
    }
    steps {
        sh 'python manage.py test --timeout=60'
    }
}
```

### Issue: Docker Cannot Start

```bash
# Check Docker daemon
sudo systemctl status docker
sudo systemctl restart docker

# Grant Jenkins user Docker access
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

---

## Monitoring and Logs

### View Pipeline Logs

```bash
# In Jenkins UI:
# Job → Build Number → Console Output

# Via terminal:
curl http://jenkins:8080/job/mediflow/lastBuild/consoleText
```

### Common Metrics to Track

1. **Build Duration**: How long pipelines take
2. **Success Rate**: Percentage of successful builds
3. **Test Coverage**: Code coverage percentage
4. **Deployment Frequency**: How often you deploy
5. **Lead Time**: Time from commit to production
6. **Mean Time to Recovery**: Time to fix failures

---

## Resources

- [Jenkins Pipeline Documentation](https://jenkins.io/doc/book/pipeline/)
- [Jenkins Best Practices](https://jenkins.io/doc/book/pipeline/pipeline-best-practices/)
- [Groovy Documentation](https://groovy-lang.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

