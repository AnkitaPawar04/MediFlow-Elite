#!/bin/bash

################################################################################
# Jenkins Automated Setup Script for MediFlow-Elite
# OS: Ubuntu 20.04 LTS or higher
# This script automates the complete Jenkins installation and configuration
# Run with: sudo bash jenkins-setup.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

################################################################################
# Check if running as root/sudo
################################################################################
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use: sudo bash $0)"
   exit 1
fi

################################################################################
# Step 1: System Update
################################################################################
log_info "Step 1: Updating system packages..."
apt-get update
apt-get upgrade -y
log_success "System packages updated"

################################################################################
# Step 2: Install Java (OpenJDK 17)
################################################################################
log_info "Step 2: Installing OpenJDK 17..."
apt-get install -y openjdk-17-jdk

# Verify Java installation
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | grep -E 'version')
    log_success "Java installed successfully: $JAVA_VERSION"
else
    log_error "Java installation failed"
    exit 1
fi

################################################################################
# Step 3: Set JAVA_HOME environment variable
################################################################################
log_info "Step 3: Setting JAVA_HOME environment variable..."
JAVA_HOME=$(update-alternatives --list java | head -n 1 | xargs dirname | xargs dirname)

if [ ! -d "$JAVA_HOME" ]; then
    JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
fi

echo "export JAVA_HOME=$JAVA_HOME" | tee /etc/profile.d/java.sh
source /etc/profile.d/java.sh

log_success "JAVA_HOME set to: $JAVA_HOME"

################################################################################
# Step 4: Add Jenkins Repository
################################################################################
log_info "Step 4: Adding Jenkins repository..."

# Download and add Jenkins GPG key
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add Jenkins repository
sh -c 'echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

# Update package list
apt-get update
log_success "Jenkins repository added"

################################################################################
# Step 5: Install Jenkins
################################################################################
log_info "Step 5: Installing Jenkins..."
apt-get install -y jenkins
log_success "Jenkins installed successfully"

################################################################################
# Step 6: Install Dependencies
################################################################################
log_info "Step 6: Installing dependencies (Git, Maven, curl, wget)..."
apt-get install -y git maven curl wget
log_success "Dependencies installed"

################################################################################
# Step 7: Start and Enable Jenkins Service
################################################################################
log_info "Step 7: Starting and enabling Jenkins service..."

# Start Jenkins
systemctl start jenkins

# Enable on boot
systemctl enable jenkins

# Wait for Jenkins to start
sleep 5

# Check if Jenkins is running
if systemctl is-active --quiet jenkins; then
    log_success "Jenkins service started and enabled"
else
    log_error "Jenkins service failed to start"
    log_info "Checking logs:"
    journalctl -u jenkins -n 20
    exit 1
fi

################################################################################
# Step 8: Configure Firewall (UFW)
################################################################################
log_info "Step 8: Configuring firewall..."

# Check if UFW is installed
if ! command -v ufw &> /dev/null; then
    log_warning "UFW not installed, skipping firewall configuration"
else
    # Enable UFW if not already enabled
    if ! ufw status | grep -q "Status: active"; then
        log_info "Enabling UFW..."
        ufw --force enable
    fi
    
    # Allow SSH (critical!)
    ufw allow 22/tcp
    
    # Allow Jenkins
    ufw allow 8080/tcp
    
    log_success "Firewall configured: SSH (22) and Jenkins (8080) ports allowed"
fi

################################################################################
# Step 9: Retrieve Initial Admin Password
################################################################################
log_info "Step 9: Retrieving initial admin password..."

# Wait for Jenkins to fully initialize
log_info "Waiting for Jenkins to fully initialize..."
for i in {1..60}; do
    if [ -f /var/lib/jenkins/secrets/initialAdminPassword ]; then
        break
    fi
    sleep 1
done

if [ -f /var/lib/jenkins/secrets/initialAdminPassword ]; then
    ADMIN_PASSWORD=$(cat /var/lib/jenkins/secrets/initialAdminPassword)
    log_success "Initial admin password retrieved"
    echo ""
    echo -e "${YELLOW}===============================================${NC}"
    echo -e "${YELLOW}JENKINS INITIAL ADMIN PASSWORD:${NC}"
    echo -e "${GREEN}$ADMIN_PASSWORD${NC}"
    echo -e "${YELLOW}===============================================${NC}"
    echo ""
else
    log_warning "Could not retrieve initial admin password"
fi

################################################################################
# Step 10: Verify Jenkins Accessibility
################################################################################
log_info "Step 10: Verifying Jenkins accessibility..."

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
log_success "Jenkins should be accessible at: http://$LOCAL_IP:8080"

# For AWS EC2
log_info "For AWS EC2, get your public IP with:"
echo "  curl http://169.254.169.254/latest/meta-data/public-ipv4"

################################################################################
# Post-Installation Information
################################################################################
cat << 'EOF'

════════════════════════════════════════════════════════════════════════════════
✓ JENKINS INSTALLATION COMPLETE!
════════════════════════════════════════════════════════════════════════════════

NEXT STEPS:

1. Open Jenkins in your browser:
   http://<your-ip>:8080

2. Use the password shown above to login

3. Install suggested plugins when prompted

4. Create your first admin user

5. Configure Jenkins:
   - Install additional plugins (GitHub, Docker, SonarQube, etc.)
   - Configure email notifications
   - Set up credentials for GitHub/AWS/etc.

USEFUL COMMANDS:

  Check Jenkins status:
    sudo systemctl status jenkins

  View Jenkins logs:
    sudo journalctl -u jenkins -f

  Check if port 8080 is listening:
    sudo netstat -tuln | grep 8080

  Restart Jenkins:
    sudo systemctl restart jenkins

  Backup Jenkins:
    sudo tar -czf jenkins-backup.tar.gz /var/lib/jenkins

SECURITY RECOMMENDATIONS:

  - Change the initial password immediately
  - Enable authentication (LDAP, OAuth, etc.)
  - Configure HTTPS/SSL
  - Restrict access with firewall rules
  - Enable audit logging
  - Keep Jenkins and plugins updated

DOCUMENTATION:

  - Official Jenkins Docs: https://jenkins.io/doc/
  - Jenkins Best Practices: https://jenkins.io/doc/book/pipeline/pipeline-best-practices/
  - GitHub Integration: https://github.com/jenkinsci/github-plugin

════════════════════════════════════════════════════════════════════════════════
EOF

################################################################################
# Final Status
################################################################################
log_success "Jenkins setup completed successfully!"
log_info "Initial admin password: $ADMIN_PASSWORD"

exit 0
