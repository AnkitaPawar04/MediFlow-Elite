# Jenkins Quick Reference & Troubleshooting Cheat Sheet

## Table of Contents
1. [Essential Commands](#essential-commands)
2. [Troubleshooting Flowchart](#troubleshooting-flowchart)
3. [Common Issues Quick Fixes](#common-issues-quick-fixes)
4. [Jenkins Configuration](#jenkins-configuration)
5. [Port Conflicts Resolution](#port-conflicts-resolution)
6. [Performance Tuning](#performance-tuning)
7. [Backup & Recovery](#backup--recovery)
8. [Security Checks](#security-checks)

---

## Essential Commands

### Service Management

```bash
# Start Jenkins
sudo systemctl start jenkins

# Stop Jenkins (graceful)
sudo systemctl stop jenkins

# Force stop Jenkins
sudo systemctl kill jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Enable on boot
sudo systemctl enable jenkins

# Disable on boot
sudo systemctl disable jenkins

# Check status
sudo systemctl status jenkins

# View service configuration
sudo systemctl show jenkins
```

### Logs & Debugging

```bash
# View Jenkins logs (last 50 lines)
sudo journalctl -u jenkins -n 50

# View Jenkins logs (follow in real-time)
sudo journalctl -u jenkins -f

# View logs with timestamps
sudo journalctl -u jenkins --since today

# Save logs to file
sudo journalctl -u jenkins > jenkins-logs.txt

# View application logs (detailed)
sudo tail -f /var/lib/jenkins/logs/jenkins.log

# Check for errors
sudo grep -i error /var/lib/jenkins/logs/*

# View startup log
cat /var/lib/jenkins/init.log
```

### Port & Network

```bash
# Check if port 8080 is listening
sudo netstat -tuln | grep 8080

# Alternative (newer systems)
sudo ss -tuln | grep 8080

# See what process is using port 8080
sudo lsof -i :8080

# See all network connections
sudo netstat -tuln

# Test connection to Jenkins
curl http://localhost:8080

# Test from remote machine
curl http://<jenkins-ip>:8080

# Check DNS resolution
nslookup jenkins.example.com
```

### Java & Memory

```bash
# Check Java version
java -version

# Find Java installation
which java

# List all Java installations
update-alternatives --list java

# Check Java processes
ps aux | grep java

# Monitor Java memory usage
jps -l

# Detailed Java info
jinfo <pid>
```

### Firewall

```bash
# Check UFW status
sudo ufw status

# Check UFW rules (numbered)
sudo ufw status numbered

# View specific port rules
sudo ufw show added

# List all rules
iptables -L -n
```

### Jenkins CLI

```bash
# Get Jenkins version
curl -s http://localhost:8080 | grep -i "poweredby"

# Test Jenkins API
curl http://localhost:8080/api/json

# Get Jenkins system info
curl http://localhost:8080/api/xml

# Get all jobs
curl http://localhost:8080/api/json | grep 'name'

# Trigger a job
curl -X POST http://localhost:8080/job/job-name/build

# Get job status
curl http://localhost:8080/job/job-name/lastBuild/api/json

# Get console output
curl http://localhost:8080/job/job-name/lastBuild/consoleText
```

---

## Troubleshooting Flowchart

```
Jenkins Not Working?
│
├─→ Error: "Connection refused"
│   ├─→ Check if service is running: sudo systemctl status jenkins
│   ├─→ Check if port is listening: sudo netstat -tuln | grep 8080
│   ├─→ Check logs: sudo journalctl -u jenkins -n 50
│   └─→ Restart: sudo systemctl restart jenkins
│
├─→ Error: "Port already in use"
│   ├─→ Find process: sudo lsof -i :8080
│   ├─→ Kill process: sudo kill -9 <PID>
│   ├─→ Change Jenkins port:
│   │   └─→ sudo nano /etc/default/jenkins (HTTP_PORT=8090)
│   └─→ Restart: sudo systemctl restart jenkins
│
├─→ Error: "Permission denied" or "Access denied"
│   ├─→ Check permissions: ls -la /var/lib/jenkins/
│   ├─→ Fix ownership: sudo chown -R jenkins:jenkins /var/lib/jenkins
│   ├─→ Check firewall: sudo ufw status
│   └─→ Allow port: sudo ufw allow 8080/tcp
│
├─→ Error: "Out of Memory"
│   ├─→ Check memory: free -h
│   ├─→ Check Java settings: grep JAVA_OPTS /etc/default/jenkins
│   ├─→ Increase heap:
│   │   └─→ Edit /etc/default/jenkins (-Xmx2048m)
│   └─→ Restart: sudo systemctl restart jenkins
│
├─→ Error: "Java not found"
│   ├─→ Install Java: sudo apt install openjdk-17-jdk
│   ├─→ Set JAVA_HOME: export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
│   ├─→ Verify: echo $JAVA_HOME
│   └─→ Restart: sudo systemctl restart jenkins
│
└─→ Error: "Initial password not found"
    ├─→ Wait 5 minutes for Jenkins to initialize
    ├─→ Check directory: sudo ls -la /var/lib/jenkins/secrets/
    ├─→ View password: sudo cat /var/lib/jenkins/secrets/initialAdminPassword
    └─→ Reset password: Manage Jenkins → Security → User Management
```

---

## Common Issues Quick Fixes

### Issue 1: Jenkins Service Fails to Start

**Error:** `systemctl status jenkins` shows `failed`

**Quick Fix:**
```bash
# Step 1: Check logs
sudo journalctl -u jenkins -n 100 | tail -30

# Step 2: Check Java
java -version

# Step 3: Check Jenkins home permissions
ls -la /var/lib/jenkins/

# Step 4: Reinstall if corrupted
sudo apt reinstall jenkins

# Step 5: Restart
sudo systemctl restart jenkins
```

### Issue 2: Cannot Access Jenkins via Browser

**Error:** `Connection refused` or `Connection timed out`

**Quick Fix:**
```bash
# Step 1: Verify Jenkins is running
sudo systemctl status jenkins

# Step 2: Check if port is listening
sudo netstat -tuln | grep 8080

# Step 3: Check firewall
sudo ufw status
sudo ufw allow 8080/tcp

# Step 4: Check AWS Security Group (if on EC2)
# Go to EC2 Dashboard → Security Groups → Add inbound rule for port 8080

# Step 5: Try localhost first
curl http://localhost:8080
```

### Issue 3: Jobs Fail with "Workspace Not Found"

**Error:** `No such file or directory: /var/lib/jenkins/workspace/...`

**Quick Fix:**
```bash
# Step 1: Check disk space
df -h

# Step 2: Check permissions
ls -la /var/lib/jenkins/workspace/

# Step 3: Fix ownership
sudo chown -R jenkins:jenkins /var/lib/jenkins/workspace/

# Step 4: Give execute permissions
sudo chmod 755 /var/lib/jenkins/workspace/

# Step 5: Clean up old workspaces (optional)
# Go to Jenkins → Job → Delete → Delete all files
```

### Issue 4: Git Command Not Found in Jobs

**Error:** `git: command not found`

**Quick Fix:**
```bash
# Step 1: Install Git
sudo apt install git -y

# Step 2: Verify installation
git --version

# Step 3: Check permissions for Jenkins user
sudo -u jenkins git --version

# Step 4: Configure Git for Jenkins user
sudo -u jenkins git config --global user.name "Jenkins"
sudo -u jenkins git config --global user.email "jenkins@mediflow.local"

# Step 5: Test in Jenkins job
echo $(git --version)
```

### Issue 5: Docker Command Not Found in Jobs

**Error:** `docker: command not found`

**Quick Fix:**
```bash
# Step 1: Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Step 2: Add Jenkins user to docker group
sudo usermod -aG docker jenkins

# Step 3: Verify permissions
sudo -u jenkins docker ps

# Step 4: Restart Jenkins
sudo systemctl restart jenkins

# Step 5: Test in job
docker ps
```

### Issue 6: Plugins Not Loading

**Error:** Plugins show as "failed to load" in Jenkins UI

**Quick Fix:**
```bash
# Step 1: Stop Jenkins
sudo systemctl stop jenkins

# Step 2: Clear plugin cache
sudo rm -rf /var/lib/jenkins/plugins/*/

# Step 3: Remove broken plugins
sudo rm /var/lib/jenkins/plugins/*.jpi.bak

# Step 4: Start Jenkins
sudo systemctl start jenkins

# Step 5: Reinstall plugins from Jenkins UI
# Manage Jenkins → Manage Plugins → Install from scratch
```

### Issue 7: Jenkins Slow/Hanging

**Error:** Pages loading slowly, builds refusing to start

**Quick Fix:**
```bash
# Step 1: Check memory usage
free -h
top -p $(pgrep -f "jenkins.war")

# Step 2: Check disk space
df -h /var/lib/jenkins

# Step 3: Check running processes
ps aux | grep java

# Step 4: Restart Jenkins
sudo systemctl restart jenkins

# Step 5: Increase heap size (if memory available)
sudo nano /etc/default/jenkins
# Change: JAVA_OPTS="-Xmx2048m -Xms1024m"
sudo systemctl restart jenkins
```

---

## Jenkins Configuration

### Change Jenkins Port

```bash
# Edit Jenkins configuration
sudo nano /etc/default/jenkins

# Find the line:
# HTTP_PORT=8080

# Change to:
# HTTP_PORT=8090

# Or set JENKINS_PORT=8090

# Save and restart
sudo systemctl restart jenkins
```

### Change Jenkins Home Directory

```bash
# Stop Jenkins
sudo systemctl stop jenkins

# Create new directory
sudo mkdir -p /home/jenkins-data
sudo chown -R jenkins:jenkins /home/jenkins-data

# Edit Jenkins configuration
sudo nano /etc/default/jenkins

# Change:
# JENKINS_HOME=/var/lib/jenkins-data

# Restart
sudo systemctl restart jenkins
```

### Configure HTTPS/SSL

```bash
# Use reverse proxy (Nginx/Apache) instead for easier SSL

# OR generate self-signed certificate:
sudo openssl req -new -newkey rsa:2048 -days 365 -nodes \
                 -out /var/lib/jenkins/jenkins.crt \
                 -keyout /var/lib/jenkins/jenkins.key

# Configure Jenkins to use HTTPS
sudo nano /etc/default/jenkins
# Add: --httpPort=-1 --httpsPort=8443 \
#      --httpsKeyStore=/var/lib/jenkins/keystorefile \
#      --httpsKeyStorePassword=password

# Restart
sudo systemctl restart jenkins
```

---

## Port Conflicts Resolution

### Find What's Using Port 8080

```bash
# Method 1: Using lsof
sudo lsof -i :8080
# Output: COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
#         java    1234 jenkins 10u IPv4 12345 0t0 TCP *:8080 (LISTEN)

# Method 2: Using netstat
sudo netstat -tuln | grep 8080
# Output: tcp 0 0 0.0.0.0:8080 0.0.0.0:* LISTEN

# Method 3: Using ss (newer)
sudo ss -tuln | grep 8080

# Find PID and process name
ps -p <PID> -o comm=
```

### Kill Process Using Port 8080

```bash
# Method 1: Kill by port number
sudo fuser -k 8080/tcp

# Method 2: Kill by PID
sudo kill -9 <PID>

# Method 3: Proper shutdown
sudo kill <PID>  # Graceful shutdown
sleep 5
sudo kill -9 <PID>  # Force if needed
```

### Change Jenkins Port

```bash
# Edit Jenkins defaults
sudo nano /etc/default/jenkins

# Find line with HTTP_PORT=8080
# Change to HTTP_PORT=8090

# Or add to JENKINS_JAVA_OPTIONS:
# --httpPort=8090

# Save and restart
sudo systemctl restart jenkins

# Verify
sudo ss -tuln | grep 8090
```

---

## Performance Tuning

### Heap Memory Optimization

```bash
# View current settings
grep JAVA_OPTS /etc/default/jenkins

# Edit configuration
sudo nano /etc/default/jenkins

# Small instance (< 4GB RAM):
# JAVA_OPTS="-Xmx1024m -Xms512m"

# Medium instance (4-8GB RAM):
# JAVA_OPTS="-Xmx2048m -Xms1024m"

# Large instance (> 8GB RAM):
# JAVA_OPTS="-Xmx4096m -Xms2048m"

# Add garbage collection tuning:
# JAVA_OPTS="-Xmx2048m -Xms1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Restart
sudo systemctl restart jenkins
```

### Optimize Disk Usage

```bash
# Check Jenkins home size
du -sh /var/lib/jenkins/

# Clean old builds
# Jenkins UI → Manage Jenkins → Configure → Discard old builds

# Or delete manually:
sudo rm -rf /var/lib/jenkins/jobs/*/builds/*/

# Clean workspace
sudo rm -rf /var/lib/jenkins/workspace/*/

# Archive old buildslogs
sudo tar -czf /backup/jenkins-builds-old.tar.gz /var/lib/jenkins/jobs/*/builds/

# Remove workspace files
sudo find /var/lib/jenkins/workspace -type f -mtime +30 -delete
```

### Monitor Performance

```bash
# Real-time resource monitoring
top -p $(pgrep -f "jenkins.war")

# Memory usage over time
watch -n 5 'free -h && echo "---" && ps aux | grep jenkins | grep -v grep'

# Number of Java threads
ps -eLf | grep java | wc -l

# Disk I/O monitoring
iotop -p $(pgrep -f "jenkins.war")

# Build queue status
curl -s http://localhost:8080/api/json | grep -A 20 '"queue"'
```

---

## Backup & Recovery

### Backup Jenkins Configuration

```bash
# Backup Jenkins home directory
sudo tar -czf ~/jenkins-backup-$(date +%Y%m%d-%H%M%S).tar.gz /var/lib/jenkins/

# Verify backup
tar -tzf ~/jenkins-backup-*.tar.gz | head -20

# List all backups
ls -lh ~/jenkins-backup-*.tar.gz
```

### Backup to External Storage (AWS S3)

```bash
# Install AWS CLI
sudo apt install awscli -y

# Configure credentials
aws configure

# Create backup script
cat > /usr/local/bin/jenkins-backup.sh << 'EOF'
#!/bin/bash
BACKUP_FILE="jenkins-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
sudo tar -czf /tmp/$BACKUP_FILE /var/lib/jenkins/
aws s3 cp /tmp/$BACKUP_FILE s3://my-jenkins-backups/
rm /tmp/$BACKUP_FILE
EOF

# Make executable
chmod +x /usr/local/bin/jenkins-backup.sh

# Schedule backup (daily at 2 AM)
echo "0 2 * * * /usr/local/bin/jenkins-backup.sh" | crontab -
```

### Restore from Backup

```bash
# List backups
ls -la jenkins-backup-*.tar.gz

# Stop Jenkins
sudo systemctl stop jenkins

# Backup current data
sudo mv /var/lib/jenkins /var/lib/jenkins.backup

# Restore backup
sudo tar -xzf jenkins-backup-*.tar.gz -C /

# Fix permissions
sudo chown -R jenkins:jenkins /var/lib/jenkins

# Start Jenkins
sudo systemctl start jenkins

# Verify
curl http://localhost:8080
```

---

## Security Checks

### Security Audit Checklist

```bash
# 1. Check if Jenkins requires authentication
curl -I http://localhost:8080/
# Look for "401 Unauthorized"

# 2. Check Jenkins version (outdated?)
curl -s http://localhost:8080 | grep -i "Version"

# 3. Check installed plugins for vulnerabilities
# Jenkins UI → Manage Jenkins → Manage Plugins

# 4. Verify HTTPS (if exposed)
curl -I https://jenkins.example.com/

# 5. Check file permissions
ls -la /var/lib/jenkins/secrets/
# Should show: -rw------- (only Jenkins user can read)

# 6. Audit Jenkins users
sudo find /var/lib/jenkins/users -name "config.xml" | xargs grep -l "userId"

# 7. Check for default credentials
grep -r "admin" /var/lib/jenkins/config.xml || echo "Default admin checked"
```

### Harden Jenkins Security

```bash
# 1. Change initial password immediately
# Jenkins UI → Manage Jenkins → Security → User Management

# 2. Configure LDAP/OAuth
# Jenkins UI → Manage Jenkins → Configure Security

# 3. Enable CSRF protection
# Jenkins UI → Manage Jenkins → Configure Security → Prevent Cross Site Request Forgery

# 4. Disable script console (if not needed)
# Jenkins UI → Manage Jenkins → Configure Security

# 5. Update all plugins
# Jenkins UI → Manage Jenkins → Manage Plugins → Updates

# 6. Configure API tokens instead of passwords
# Your Profile → API Token → Generate

# 7. Limit node access
# Jenkins UI → Manage Jenkins → Configure Global Security

# 8. Enable audit logs
echo "JAVA_OPTS=\"\$JAVA_OPTS -Dcom.cloudbees.jenkins.plugins.kubernetes.audit=true\"" | sudo tee -a /etc/default/jenkins
```

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Start Jenkins | `sudo systemctl start jenkins` |
| Stop Jenkins | `sudo systemctl stop jenkins` |
| Restart Jenkins | `sudo systemctl restart jenkins` |
| Status | `sudo systemctl status jenkins` |
| Enable on boot | `sudo systemctl enable jenkins` |
| View logs | `sudo journalctl -u jenkins -f` |
| Check port | `sudo netstat -tuln \| grep 8080` |
| Get initial password | `sudo cat /var/lib/jenkins/secrets/initialAdminPassword` |
| Check Java version | `java -version` |
| Check disk space | `df -h /var/lib/jenkins/` |
| Backup Jenkins | `sudo tar -czf jenkins-backup.tar.gz /var/lib/jenkins/` |
| Test Jenkins API | `curl http://localhost:8080/api/json` |

---

## When to Escalate

Contact Jenkins Administration when:
- ✓ Repeated failures despite troubleshooting
- ✓ Security/authentication issues
- ✓ Need for infrastructure changes
- ✓ Plugin compatibility issues
- ✓ Performance issues requiring tuning
- ✓ Backup/disaster recovery

## Support Resources

- **Official Docs**: https://jenkins.io/doc/
- **Community Chat**: https://jenkins.io/chat/
- **Issue Tracker**: https://issues.jenkins.io/
- **Jenkins for DevOps**: https://www.Jenkins.io/doc/book/

---

**Last Updated:** April 2026
**For MediFlow-Elite DevOps**
