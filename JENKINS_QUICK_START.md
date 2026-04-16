# Jenkins Quick Start - Step-by-Step Activation Guide

## ⚡ 5-Minute Quick Start

### **Step 1: Connect to Your Ubuntu EC2 Instance**

```bash
# From your local machine
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Example:
ssh -i ~/Downloads/mediflow-key.pem ubuntu@3.84.65.123
```

---

## 🔧 **Step 2: Run the Automated Setup (Recommended - 5 minutes)**

Copy and paste this **ONE command** into your Ubuntu terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/your-org/mediflow-elite/jenkins-setup.sh | sudo bash
```

**OR download and run locally:**

```bash
# Download the script
sudo wget https://raw.githubusercontent.com/your-org/mediflow-elite/jenkins-setup.sh -O /tmp/jenkins-setup.sh

# Run it
sudo bash /tmp/jenkins-setup.sh
```

**Expected output:**
```
[INFO] Step 1: Updating system packages...
[SUCCESS] System packages updated
[INFO] Step 2: Installing OpenJDK 17...
[SUCCESS] Java installed successfully: openjdk version "17.0.x"
...
✓ JENKINS INSTALLATION COMPLETE!

JENKINS INITIAL ADMIN PASSWORD:
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

Jenkins should be accessible at: http://YOUR_IP:8080
```

---

## 🛠️ **Step 3: Manual Installation (If Script Doesn't Work)**

Run these commands **one at a time**:

### **3.1 Update System**
```bash
sudo apt update
sudo apt upgrade -y
```
*This updates package manager and system packages*

### **3.2 Install Java**
```bash
sudo apt install openjdk-17-jdk -y
```
*Verify:*
```bash
java -version
# Should show: openjdk version "17.0.x"
```

### **3.3 Add Jenkins Repository**
```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
```

### **3.4 Install Jenkins**
```bash
sudo apt install jenkins -y
```

### **3.5 Install Dependencies**
```bash
sudo apt install -y git maven curl wget
```

### **3.6 Start Jenkins**
```bash
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

### **3.7 Allow Firewall Port**
```bash
# Enable firewall (if not already)
sudo ufw --force enable

# Allow SSH and Jenkins ports
sudo ufw allow 22/tcp
sudo ufw allow 8080/tcp

# Verify
sudo ufw status
```

### **3.8 Get Initial Admin Password**
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**Copy the password that appears** - you'll need it in the next step.

---

## ✅ **Step 4: Verify Jenkins is Running**

Check all these to confirm Jenkins is ready:

### **4.1 Service Status**
```bash
sudo systemctl status jenkins
```
**Should show:** `Active: active (running)`

### **4.2 Port is Listening**
```bash
sudo netstat -tuln | grep 8080
```
**Should show:** `tcp    0    0 0.0.0.0:8080    0.0.0.0:*    LISTEN`

### **4.3 Can Reach Jenkins Locally**
```bash
curl http://localhost:8080
```
**Should show HTML content (not an error)**

---

## 🌐 **Step 5: Access Jenkins via Browser**

### **5.1 Find Your Public IP**

**If on AWS EC2, run:**
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

**Or from your local machine:**
```bash
wget -q O- http://169.254.169.254/latest/meta-data/public-ipv4
```

### **5.2 Open in Browser**

**Go to:**
```
http://YOUR-PUBLIC-IP:8080
```

**Example:**
```
http://3.84.65.123:8080
```

---

## 🔐 **Step 6: Initial Jenkins Configuration**

### **6.1 Unlock Jenkins**
1. You'll see the "Unlock Jenkins" page
2. Paste the password from Step 3.8 into the password field
3. Click "Continue"

### **6.2 Customize Jenkins**
1. Click "Install suggested plugins"
2. Wait for plugins to install (takes 2-3 minutes)

### **6.3 Create Admin User**
Fill in the form:
- **Username:** `admin` (or your preferred name)
- **Password:** Create a strong password
- **Full name:** Your name
- **Email:** your-email@example.com
- Click "Save and Continue"

### **6.4 Jenkins URL Configuration**
- Jenkins URL should be: `http://YOUR-PUBLIC-IP:8080/`
- Click "Save and Finish"

### **6.5 Success Page**
You should see "Jenkins is ready!" 
- Click "Start using Jenkins"

---

## 🎯 **Step 7: Verify Jenkins is Fully Configured**

### **7.1 Check Dashboard**
You should see the Jenkins dashboard with:
- Job list (empty initially)
- Build queue
- System load

### **7.2 Test Jenkins is Working**
Go to **Manage Jenkins** → **Script Console**

Paste this and click "Run":
```groovy
println("Jenkins is working! Version: " + Jenkins.instance.getVersion())
```

Should print your Jenkins version.

---

## 📋 **Quick Command Reference**

| Task | Command |
|------|---------|
| Check Jenkins status | `sudo systemctl status jenkins` |
| Start Jenkins | `sudo systemctl start jenkins` |
| Stop Jenkins | `sudo systemctl stop jenkins` |
| Restart Jenkins | `sudo systemctl restart jenkins` |
| View logs | `sudo journalctl -u jenkins -f` |
| Get initial password | `sudo cat /var/lib/jenkins/secrets/initialAdminPassword` |
| Check if running | `curl http://localhost:8080` |
| Get public IP | `curl http://169.254.169.254/latest/meta-data/public-ipv4` |

---

## ⚠️ **Troubleshooting - Quick Fixes**

### **Problem: Cannot access Jenkins (Connection refused)**

**Solution:**
```bash
# Check if service is running
sudo systemctl status jenkins

# Start it if not running
sudo systemctl start jenkins

# Wait 10 seconds and try again
sleep 10

# Check if port 8080 is open
sudo netstat -tuln | grep 8080

# If firewall blocked, fix it
sudo ufw allow 8080/tcp
```

### **Problem: Initial password not found**

**Solution:**
```bash
# Wait 30 seconds for Jenkins to initialize
sleep 30

# Try again
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# If still not found, check logs
sudo journalctl -u jenkins -n 50
```

### **Problem: Java not found**

**Solution:**
```bash
# Reinstall Java
sudo apt install openjdk-17-jdk -y

# Verify
java -version

# Restart Jenkins
sudo systemctl restart jenkins
```

### **Problem: Permission denied errors**

**Solution:**
```bash
# Fix Jenkins ownership
sudo chown -R jenkins:jenkins /var/lib/jenkins

# Restart
sudo systemctl restart jenkins
```

---

## 🚀 **Next Steps After Jenkins is Ready**

1. **Install Plugins**
   - Go to **Manage Jenkins** → **Manage Plugins**
   - Install: Git, Pipeline, Blue Ocean, GitHub, Docker, SonarQube

2. **Configure Git**
   - **Manage Jenkins** → **Configure System**
   - Set Git installations path

3. **Add Credentials**
   - **Manage Jenkins** → **Manage Credentials**
   - Add GitHub credentials, Docker Hub, AWS credentials

4. **Create First Job**
   - Click "New Item"
   - Enter job name
   - Select "Pipeline"
   - Configure and save

5. **Import Pipeline**
   - Clone your MediFlow-Elite repo to Jenkins
   - Point to your `Jenkinsfile`
   - Run build

---

## 📚 **Complete Documentation Available**

For more detailed information, see:

| Document | Purpose |
|----------|---------|
| `JENKINS_SETUP_GUIDE.md` | Complete step-by-step with DevOps concepts |
| `JENKINS_PIPELINE_GUIDE.md` | How to create CI/CD pipelines |
| `JENKINS_IaC_TERRAFORM_CLOUDFORMATION.md` | Automate with Terraform/CloudFormation |
| `JENKINS_QUICK_REFERENCE.md` | Commands, troubleshooting, performance tuning |

---

## ✨ **Summary**

| Step | Time | What You Get |
|------|------|-------------|
| 1. SSH to EC2 | 30 sec | Connection to server |
| 2. Run script | 5 min | Jenkins installed & running |
| 3. Access browser | 1 min | Jenkins UI loaded |
| 4. Initial config | 5 min | Admin user created |
| 5. Verify setup | 2 min | Confirmation Jenkins works |
| **Total** | **~13 minutes** | **Production-ready Jenkins** |

---

## 🎉 Success Indicators

You'll know Jenkins is working when you see:

✅ Jenkins dashboard in browser at `http://YOUR-IP:8080`  
✅ Can log in with admin credentials  
✅ No errors in Jenkins logs  
✅ "System Load" shows on dashboard  
✅ Can navigate to "Manage Jenkins" without errors  

**Congratulations! Jenkins is now enabled and ready for CI/CD! 🚀**

---

## 💡 Security Tips

1. **Change the initial password immediately** (you already did in Step 6.3)
2. **Configure HTTPS** (use reverse proxy like Nginx)
3. **Restrict port 8080** to your network only (in AWS Security Group)
4. **Enable authentication** (already on by default)
5. **Keep Jenkins updated** (go to Manage Jenkins periodically)

---

**Need help? Refer to `JENKINS_QUICK_REFERENCE.md` for troubleshooting!**

