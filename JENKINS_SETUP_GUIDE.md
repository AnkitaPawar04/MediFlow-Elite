# Jenkins Setup Guide for MediFlow-Elite (Ubuntu EC2)

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [DevOps Concepts Explained](#devops-concepts-explained)
4. [Initial Jenkins Configuration](#initial-jenkins-configuration)
5. [Troubleshooting](#troubleshooting)
6. [After Installation](#after-installation)

---

## Prerequisites

- Ubuntu 20.04 LTS or higher (on AWS EC2)
- SSH access to your EC2 instance
- sudo privileges
- Security group configured to allow inbound traffic on port 8080

---

## Step-by-Step Installation

### Step 1: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

**Explanation:**
- `sudo`: Run commands with superuser privileges (essential for system-level installations)
- `apt update`: Refreshes the package index from repositories. This ensures you get the latest available package versions
- `apt upgrade -y`: Upgrades all installed packages to their latest versions. The `-y` flag automatically confirms the operation
- **Why**: Keeping the system updated ensures security patches and compatibility with Jenkins requirements

**DevOps Concept:** *System Hardening* - Keeping systems patched and updated is a critical security practice in DevOps CI/CD pipelines.

---

### Step 2: Install Java (OpenJDK 17)

```bash
sudo apt install openjdk-17-jdk -y
```

**Explanation:**
- `openjdk-17-jdk`: OpenJDK 17 JDK (Java Development Kit) package
- This includes the Java Runtime Environment (JRE) and development tools
- **Why**: Jenkins requires Java to run. OpenJDK 17 is a Long-Term Support (LTS) version, ensuring stability and extended support

**Verify Java Installation:**

```bash
java -version
```

**Expected Output:**
```
openjdk version "17.0.x" ...
```

**DevOps Concept:** *Dependency Management* - Jenkins depends on Java. Using LTS versions ensures production stability and reduces compatibility issues.

---

### Step 3: Set JAVA_HOME Environment Variable

```bash
# Find Java installation path
which java
# Or more reliably:
sudo update-alternatives --list java
```

**Expected Output:**
```
/usr/lib/jvm/java-17-openjdk-amd64/bin/java
```

**Set the environment variable:**

```bash
# Add to ~/.bashrc or /etc/profile.d/jenkins.sh
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' | sudo tee -a /etc/profile.d/java.sh
source /etc/profile.d/java.sh
```

**Explanation:**
- `JAVA_HOME`: An environment variable that tells Jenkins where Java is installed
- `/etc/profile.d/`: Directory for shell scripts that are sourced by login shells
- `tee -a`: Redirects output to both terminal and file (append mode)
- **Why**: Jenkins needs to know where Java is located to execute properly. Setting JAVA_HOME ensures consistency across all processes

**Verify:**

```bash
echo $JAVA_HOME
# Should output: /usr/lib/jvm/java-17-openjdk-amd64
```

---

### Step 4: Add Jenkins Repository

Jenkins maintains its own Ubuntu repository for stable releases:

```bash
# Add Jenkins repository key
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add Jenkins repository
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
```

**Explanation:**
- `curl -fsSL`: Downloads the Jenkins GPG key
  - `-f`: Fail silently on HTTP errors
  - `-s`: Silent mode (no progress bar)
  - `-S`: Show errors despite silent mode
  - `-L`: Follow redirects
- `tee`: Writes output to file and console
- GPG key signing: Ensures package authenticity and prevents man-in-the-middle attacks

**DevOps Concept:** *Secure Package Management* - Using signed repositories and GPG keys is a security best practice in DevOps. This verifies that packages come from legitimate sources.

```bash
# Update package list after adding new repository
sudo apt update
```

---

### Step 5: Install Jenkins

```bash
sudo apt install jenkins -y
```

**Explanation:**
- This installs the Jenkins package from the official repository
- Includes Jenkins service configuration and systemd integration
- **Why**: Using the official repository ensures you get vetted, stable releases with security patches

---

### Step 6: Install Additional Dependencies

```bash
# Git (for version control integration)
sudo apt install git -y

# Maven (for Java project builds) - Optional but recommended
sudo apt install maven -y

# curl and wget (for downloading resources)
sudo apt install curl wget -y
```

**Explanation:**
- **Git**: Jenkins needs Git to clone repositories and manage source code
- **Maven**: Build automation tool for Java projects (common in CI/CD pipelines)
- **curl/wget**: CLI tools for downloading files and making HTTP requests
- **Why**: These tools are commonly used by Jenkins jobs to build, test, and deploy applications

**DevOps Concept:** *Plugin Dependencies* - Many Jenkins plugins depend on external tools. Pre-installing them prevents job failures.

---

### Step 7: Start and Enable Jenkins Service

```bash
# Start Jenkins immediately
sudo systemctl start jenkins

# Enable Jenkins to start on system boot
sudo systemctl enable jenkins
```

**Explanation:**
- `systemctl start jenkins`: Starts the Jenkins service immediately
- `systemctl enable jenkins`: Creates symbolic links to auto-start Jenkins on boot
- **Why**: You want Jenkins running continuously. The `enable` command ensures it survives server restarts

**DevOps Concept:** *Service Management* - Using systemd to manage services ensures reliable, reproducible service startup and shutdown. This is essential for production environments.

**Verify Jenkins is running:**

```bash
sudo systemctl status jenkins
```

**Expected Output:**
```
● jenkins.service - Jenkins Automation Server
   Loaded: loaded (/lib/systemd/jenkins.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

---

### Step 8: Configure Firewall (UFW - Uncomplicated Firewall)

```bash
# Check firewall status
sudo ufw status

# If firewall is inactive, enable it (recommended for production)
sudo ufw enable

# Allow SSH (port 22) to avoid lockout
sudo ufw allow 22/tcp

# Allow Jenkins (port 8080)
sudo ufw allow 8080/tcp

# Verify rules
sudo ufw status numbered
```

**Explanation:**
- `ufw`: Ubuntu's simplified firewall management interface
- `ufw allow 8080/tcp`: Opens port 8080 for TCP traffic (required for Jenkins web interface)
- **Why**: A firewall restricts unauthorized access. Only exposing necessary ports is a security best practice

**DevOps Concept:** *Network Security* - Firewalls are a critical part of defense-in-depth strategy. Rules should follow the principle of least privilege (only open what's necessary).

**AWS EC2 Security Group Alternative:**

If using AWS EC2, you may also need to configure the Security Group:

```
EC2 Dashboard → Security Groups → Your Instance's Security Group
Inbound Rules:
  - Type: Custom TCP
  - Port Range: 8080
  - Source: 0.0.0.0/0 (or your IP for better security)
  
  - Type: SSH
  - Port: 22
  - Source: 0.0.0.0/0 (or your IP)
```

---

### Step 9: Retrieve Initial Admin Password

```bash
# Get the initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**Expected Output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Explanation:**
- Jenkins creates a temporary admin password on first startup
- This password is stored in a secure file with restricted permissions
- **Why**: This ensures only authorized users (with sudo access) can retrieve the initial password
- **Store this password safely**: Copy it to a secure location (password manager, encrypted file, etc.)

---

### Step 10: Access Jenkins via Browser

```
http://<your-ec2-public-ip>:8080
```

**To find your EC2 public IP:**

From your EC2 instance:
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

Or:
```bash
hostname -I
```

**In Jenkins UI:**
1. Paste the initial admin password from Step 9
2. Click "Continue"
3. Click "Install suggested plugins" (recommended for beginners)
4. Create your first admin user
5. Confirm Jenkins URL
6. Complete setup

**DevOps Concept:** *Infrastructure as Code & Automation* - Manual setup is error-prone. In production, consider automating this with:
- Terraform/CloudFormation for EC2
- User data scripts or Ansible for software installation
- Jenkins Configuration as Code (JCasC) for Jenkins setup

---

## DevOps Concepts Explained

### 1. **Continuous Integration (CI)**
Jenkins enables CI by:
- Automatically pulling code from version control (Git)
- Running automated tests
- Building applications
- Providing instant feedback to developers

### 2. **Automation**
Jenkins automates:
- Build compilation
- Testing (unit, integration, security)
- Deployment to staging/production
- Artifact creation

### 3. **Monitoring & Logging**
Jenkins tracks:
- Build success/failure rates
- Build history
- Performance metrics
- Logs for debugging

**Command for viewing logs:**
```bash
sudo journalctl -u jenkins -f  # Follow Jenkins logs in real-time
```

### 4. **Security & Access Control**
- Role-based access control (RBAC)
- User authentication and authorization
- Credential management for API keys, SSH keys
- Audit trails for compliance

### 5. **Scalability**
Jenkins supports:
- Master-slave (Agent) architecture
- Distributed builds across multiple machines
- Container-based agents (Docker)
- Cloud integrations (AWS, Azure, GCP)

---

## Initial Jenkins Configuration

### Configure Jenkins Home Directory

```bash
# Default Jenkins home
echo $JENKINS_HOME
# Default: /var/lib/jenkins

# Check disk space
df -h /var/lib/jenkins
```

### Install Essential Plugins

After initial setup, install these plugins from "Manage Jenkins" → "Manage Plugins":

- **Git Plugin**: Git repository integration
- **GitHub Integration Plugin**: GitHub-specific features
- **Pipeline**: Build aggregation from multiple jobs
- **Blue Ocean**: Modern UI for pipeline visualization
- **Email Extension**: Advanced email notifications
- **SonarQube Scanner**: Code quality analysis
- **Docker**: Docker integration for container builds
- **AWS CodeDeploy**: AWS deployment integration
- **Slack Notification**: Slack integration for notifications

---

## Troubleshooting

### Issue 1: Jenkins Service Won't Start

**Symptoms:** `sudo systemctl status jenkins` shows "inactive" or "failed"

**Root Causes & Solutions:**

```bash
# Check Jenkins logs
sudo journalctl -u jenkins -n 50  # Last 50 lines

# Check if port 8080 is already in use
sudo netstat -tuln | grep 8080
# or
sudo ss -tuln | grep 8080

# Kill process on port 8080 (if needed)
sudo lsof -i :8080  # Identify process
sudo kill -9 <PID>  # Force kill

# Restart Jenkins
sudo systemctl restart jenkins
```

### Issue 2: Java Not Found Error

**Symptoms:** "java: command not found" or similar

```bash
# Reinstall Java
sudo apt install openjdk-17-jdk -y

# Verify installation
java -version

# Set JAVA_HOME again
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' | sudo tee -a /etc/profile.d/java.sh
```

### Issue 3: Port 8080 Connection Refused

**Symptoms:** Cannot access `http://<ip>:8080` in browser

```bash
# Verify Jenkins is listening on port 8080
sudo netstat -tuln | grep 8080

# Check firewall rules
sudo ufw status

# If needed, reopen port 8080
sudo ufw delete allow 8080/tcp
sudo ufw allow 8080/tcp

# Check AWS Security Group inbound rules
# EC2 Console → Security Groups → Verify port 8080 is allowed
```

### Issue 4: Permission Denied Errors

**Symptoms:** Jenkins job fails with "Permission denied"

```bash
# Check Jenkins user
ps aux | grep jenkins

# Jenkins runs as 'jenkins' user
# Grant permissions if needed:
sudo usermod -a -G docker jenkins  # For Docker integration
sudo usermod -a -G sudo jenkins    # For sudo commands (cautious!)

# Restart Jenkins after permission changes
sudo systemctl restart jenkins
```

### Issue 5: Out of Memory (OOM) Errors

**Symptoms:** "java.lang.OutOfMemoryError" in logs

```bash
# Edit Jenkins systemd service
sudo nano /etc/systemd/system/jenkins.service.d/override.conf

# Add memory settings (example: 2GB heap):
[Service]
Environment="JAVA_OPTS=-Xmx2048m -Xms1024m"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart jenkins
```

**Explanation of Java memory flags:**
- `-Xmx2048m`: Maximum heap size (2GB)
- `-Xms1024m`: Initial heap size (1GB)
- Adjust based on your EC2 instance size

### Issue 6: Initial Admin Password Lost

**Symptoms:** Cannot log in, forgot the initial password

```bash
# Reset admin password (via Jenkins CLI or manual)

# Option 1: View password again
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# Option 2: Reset password via Groovy script
# In Jenkins UI: Manage Jenkins → Script Console
# Paste the following:
def user = jenkins.model.Jenkins.instance.getSecurityRealm().createAccount("admin", "newpassword")
user.save()
jenkins.model.Jenkins.instance.save()

# Option 3: Edit configuration directly (advanced)
sudo nano /var/lib/jenkins/users/admin/config.xml
# Find and replace hash, then restart Jenkins
```

---

## After Installation

### 1. Configure Email Notifications

Jenkins → Manage Jenkins → Configure System → Email Notification

```
SMTP server: smtp.gmail.com
SMTP port: 587
Use SMTP Authentication: ✓
Username: your-email@gmail.com
Password: app-password (generate in Gmail settings)
```

### 2. Set Up Your First Job

**Create a Pipeline Job:**
```
Jenkins → New Item → Enter name → Pipeline → OK
```

**Sample Pipeline Script (Declarative Pipeline):**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo/mediflow-elite.git'
            }
        }
        
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production...'
                // Add your deployment commands here
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

### 3. Integrate with GitHub

1. Go to Jenkins → Manage Jenkins → Manage Credentials
2. Add GitHub credentials (Personal Access Token)
3. Create a new job and select "GitHub Project"
4. Paste your repository URL
5. Configure webhook in GitHub settings for automatic triggers

### 4. Monitor Jenkins Health

```bash
# Check Jenkins system logs
sudo tail -f /var/log/jenkins/jenkins.log

# Monitor resource usage
top  # Real-time process monitoring
df -h  # Disk space
free -h  # Memory usage
```

### 5. Regular Maintenance

```bash
# Backup Jenkins home directory
sudo tar -czf jenkins-backup-$(date +%Y%m%d).tar.gz /var/lib/jenkins

# Update Jenkins
sudo apt update
sudo apt upgrade jenkins -y

# Restart after updates
sudo systemctl restart jenkins
```

---

## Quick Reference Commands

```bash
# Check Jenkins status
sudo systemctl status jenkins

# Start Jenkins
sudo systemctl start jenkins

# Stop Jenkins
sudo systemctl stop jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# View Jenkins logs
sudo journalctl -u jenkins -f

# Check port 8080
sudo netstat -tuln | grep 8080

# Test Jenkins API (should return JSON if running)
curl http://localhost:8080/api/json

# Get Jenkins version
curl -s http://localhost:8080 | grep "Proudly powered"
```

---

## Security Best Practices for Production

1. **Always use HTTPS** with SSL certificates (Let's Encrypt)
2. **Restrict access** with VPN or bastion host
3. **Enable authentication** (LDAP, OAuth, etc.)
4. **Regular backups** of Jenkins configuration
5. **Keep Jenkins updated** with security patches
6. **Monitor logs** for suspicious activity
7. **Use Jenkins agents** for resource-intensive jobs
8. **Implement credential rotation** for API keys
9. **Enable audit logging** for compliance
10. **Use Jenkins Configuration as Code (JCasC)** for reproducible setups

---

## Useful Resources

- [Jenkins Official Documentation](https://jenkins.io/doc/)
- [Jenkins Best Practices](https://jenkins.io/doc/book/pipeline/pipeline-best-practices/)
- [GitHub Jenkins Integration](https://github.com/jenkinsci/github-plugin)
- [Jenkins Docker Integration](https://jenkins.io/doc/book/installing/#docker)
- [Kubernetes Jenkins Deployment](https://jenkins.io/doc/book/installing/#kubernetes)

---

**Last Updated:** April 2026
**For MediFlow-Elite DevOps Setup**
