# Infrastructure as Code for Jenkins Setup
# This guide includes Terraform and CloudFormation examples for automated deployment

## Table of Contents
1. [Terraform Configuration](#terraform-configuration)
2. [CloudFormation Template](#cloudformation-template)
3. [User Data Script](#user-data-script)
4. [Deployment Instructions](#deployment-instructions)

---

## Terraform Configuration

### File: `terraform/main.tf`

```hcl
# Configure Terraform
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "MediFlow-Elite"
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }
  }
}

# VPC Configuration
resource "aws_vpc" "jenkins_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "jenkins-vpc"
  }
}

# Public Subnet
resource "aws_subnet" "jenkins_subnet" {
  vpc_id                  = aws_vpc.jenkins_vpc.id
  cidr_block              = var.subnet_cidr
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "jenkins-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "jenkins_igw" {
  vpc_id = aws_vpc.jenkins_vpc.id

  tags = {
    Name = "jenkins-igw"
  }
}

# Route Table
resource "aws_route_table" "jenkins_rt" {
  vpc_id = aws_vpc.jenkins_vpc.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.jenkins_igw.id
  }

  tags = {
    Name = "jenkins-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "jenkins_rta" {
  subnet_id      = aws_subnet.jenkins_subnet.id
  route_table_id = aws_route_table.jenkins_rt.id
}

# Security Group
resource "aws_security_group" "jenkins_sg" {
  name        = "jenkins-security-group"
  description = "Security group for Jenkins"
  vpc_id      = aws_vpc.jenkins_vpc.id

  # SSH access (restrict to your IP in production)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr  # Restrict this!
  }

  # Jenkins web interface
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict this in production!
  }

  # Outbound - allow all
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jenkins-sg"
  }
}

# Get latest Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# EC2 Instance for Jenkins
resource "aws_instance" "jenkins" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.jenkins_subnet.id
  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]
  
  # Use IAM instance profile for AWS API access
  iam_instance_profile   = aws_iam_instance_profile.jenkins_profile.name

  # User data script for automatic setup
  user_data = base64encode(file("${path.module}/user_data.sh"))

  # Root volume configuration
  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_size
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "jenkins-root-volume"
    }
  }

  # Additional EBS volume for Jenkins data
  ebs_block_device {
    device_name = "/dev/sdf"
    volume_type = "gp3"
    volume_size = var.jenkins_volume_size
    encrypted   = true

    tags = {
      Name = "jenkins-data-volume"
    }
  }

  monitoring              = true  # Enable detailed CloudWatch monitoring
  associate_public_ip_address = true

  tags = {
    Name = "jenkins-server"
  }

  depends_on = [aws_internet_gateway.jenkins_igw]
}

# Elastic IP for Jenkins (static IP)
resource "aws_eip" "jenkins_eip" {
  instance = aws_instance.jenkins.id
  domain   = "vpc"

  tags = {
    Name = "jenkins-eip"
  }

  depends_on = [aws_internet_gateway.jenkins_igw]
}

# IAM Role for EC2 to access AWS services
resource "aws_iam_role" "jenkins_role" {
  name = "jenkins-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Jenkins to access AWS services
resource "aws_iam_role_policy" "jenkins_policy" {
  name = "jenkins-ec2-policy"
  role = aws_iam_role.jenkins_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "s3:*",
          "logs:*",
          "cloudwatch:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "jenkins_profile" {
  name = "jenkins-instance-profile"
  role = aws_iam_role.jenkins_role.name
}

# CloudWatch Log Group for Jenkins
resource "aws_cloudwatch_log_group" "jenkins_logs" {
  name              = "/aws/jenkins/logs"
  retention_in_days = 30

  tags = {
    Name = "jenkins-logs"
  }
}

# Outputs
output "jenkins_url" {
  description = "URL to access Jenkins"
  value       = "http://${aws_eip.jenkins_eip.public_ip}:8080"
}

output "jenkins_public_ip" {
  description = "Public IP of Jenkins instance"
  value       = aws_eip.jenkins_eip.public_ip
}

output "jenkins_private_ip" {
  description = "Private IP of Jenkins instance"
  value       = aws_instance.jenkins.private_ip
}

output "jenkins_instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.jenkins.id
}

output "jenkins_security_group_id" {
  description = "Security Group ID"
  value       = aws_security_group.jenkins_sg.id
}
```

### File: `terraform/variables.tf`

```hcl
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"  # 4GB RAM, 2 vCPU - suitable for small to medium deployments
}

variable "root_volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 30
}

variable "jenkins_volume_size" {
  description = "Jenkins data volume size in GB"
  type        = number
  default     = 50
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed for SSH access (restrict to your IP!)"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # CHANGE THIS IN PRODUCTION!
}
```

### File: `terraform/terraform.tfvars`

```hcl
# Customize these values for your deployment

aws_region         = "us-east-1"
environment         = "dev"
instance_type       = "t3.medium"
root_volume_size    = 30
jenkins_volume_size = 50

# IMPORTANT: Restrict SSH access to your IP!
# Replace with your actual IP: ["1.2.3.4/32"]
allowed_ssh_cidr    = ["0.0.0.0/0"]
```

---

## CloudFormation Template

### File: `cloudformation/jenkins-stack.yaml`

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'CloudFormation Template for Jenkins on EC2 - MediFlow-Elite'

Parameters:
  InstanceType:
    Type: String
    Default: t3.medium
    AllowedValues:
      - t3.small
      - t3.medium
      - t3.large
      - t3.xlarge
    Description: EC2 instance type

  RootVolumeSize:
    Type: Number
    Default: 30
    Description: Root volume size in GB

  JenkinsVolumeSize:
    Type: Number
    Default: 50
    Description: Jenkins data volume size in GB

  AllowedSSHCIDR:
    Type: String
    Default: 0.0.0.0/0
    Description: "CIDR block for SSH access (restrict to your IP!)"

Mappings:
  RegionAMI:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0  # Ubuntu 22.04 LTS (update as needed)
    us-west-2:
      AMI: ami-0d1cd67c26f5fca19
    eu-west-1:
      AMI: ami-0dad359ff462124ca

Resources:
  # VPC
  JenkinsVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: jenkins-vpc

  # Subnet
  JenkinsSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref JenkinsVPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: jenkins-subnet

  # Internet Gateway
  JenkinsIGW:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: jenkins-igw

  AttachIGW:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref JenkinsVPC
      InternetGatewayId: !Ref JenkinsIGW

  # Route Table
  JenkinsRT:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref JenkinsVPC
      Tags:
        - Key: Name
          Value: jenkins-rt

  JenkinsRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachIGW
    Properties:
      RouteTableId: !Ref JenkinsRT
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref JenkinsIGW

  RTAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref JenkinsSubnet
      RouteTableId: !Ref JenkinsRT

  # Security Group
  JenkinsSG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Jenkins
      VpcId: !Ref JenkinsVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AllowedSSHCIDR
          Description: SSH access
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0
          Description: Jenkins web interface
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
          Description: Allow all outbound
      Tags:
        - Key: Name
          Value: jenkins-sg

  # IAM Role
  JenkinsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: 'sts:AssumeRole'
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Tags:
        - Key: Name
          Value: jenkins-role

  JenkinsPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: jenkins-policy
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Action:
              - ec2:*
              - s3:*
              - logs:*
              - cloudwatch:*
            Resource: '*'
      Roles:
        - !Ref JenkinsRole

  JenkinsInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref JenkinsRole

  # EC2 Instance
  JenkinsInstance:
    Type: AWS::EC2::Instance
    DependsOn: AttachIGW
    Properties:
      ImageId: !FindInMap [RegionAMI, !Ref 'AWS::Region', AMI]
      InstanceType: !Ref InstanceType
      SubnetId: !Ref JenkinsSubnet
      SecurityGroupIds:
        - !Ref JenkinsSG
      IamInstanceProfile: !Ref JenkinsInstanceProfile
      Monitoring: true
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          set -e
          
          echo "Starting Jenkins installation..."
          apt-get update
          apt-get upgrade -y
          
          # Install Java
          apt-get install -y openjdk-17-jdk
          echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> /etc/profile.d/java.sh
          source /etc/profile.d/java.sh
          
          # Add Jenkins repository
          curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
          sh -c 'echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
          apt-get update
          
          # Install Jenkins and dependencies
          apt-get install -y jenkins git maven curl wget
          
          # Start and enable Jenkins
          systemctl start jenkins
          systemctl enable jenkins
          
          # Configure firewall
          apt-get install -y ufw
          ufw --force enable
          ufw allow 22/tcp
          ufw allow 8080/tcp
          
          # Log initial password to CloudWatch
          sleep 10
          if [ -f /var/lib/jenkins/secrets/initialAdminPassword ]; then
            ADMIN_PASSWORD=$(cat /var/lib/jenkins/secrets/initialAdminPassword)
            echo "Jenkins Initial Admin Password: $ADMIN_PASSWORD"
          fi
          
          echo "Jenkins installation completed!"
      BlockDeviceMappings:
        - DeviceName: /dev/sda1
          Ebs:
            VolumeSize: !Ref RootVolumeSize
            VolumeType: gp3
            DeleteOnTermination: true
            Encrypted: true
        - DeviceName: /dev/sdf
          Ebs:
            VolumeSize: !Ref JenkinsVolumeSize
            VolumeType: gp3
            DeleteOnTermination: false
            Encrypted: true
      Tags:
        - Key: Name
          Value: jenkins-server
        - Key: Project
          Value: MediFlow-Elite

  # Elastic IP
  JenkinsEIP:
    Type: AWS::EC2::EIP
    DependsOn: AttachIGW
    Properties:
      InstanceId: !Ref JenkinsInstance
      Domain: vpc
      Tags:
        - Key: Name
          Value: jenkins-eip

  # CloudWatch Log Group
  JenkinsLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/jenkins/logs
      RetentionInDays: 30

Outputs:
  JenkinsURL:
    Description: URL to access Jenkins
    Value: !Sub 'http://${JenkinsEIP}:8080'

  JenkinsPublicIP:
    Description: Public IP of Jenkins instance
    Value: !Ref JenkinsEIP

  JenkinsInstanceID:
    Description: EC2 Instance ID
    Value: !Ref JenkinsInstance

  SecurityGroupID:
    Description: Security Group ID
    Value: !Ref JenkinsSG
```

---

## User Data Script

### File: `user_data.sh`

```bash
#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/jenkins-setup.log)
exec 2>&1

echo "=== Jenkins Setup Started at $(date) ==="

# Update system
apt-get update
apt-get upgrade -y

# Install Java 17
echo "Installing OpenJDK 17..."
apt-get install -y openjdk-17-jdk

# Set JAVA_HOME
JAVA_HOME=$(update-alternatives --list java | head -n 1 | xargs dirname | xargs dirname)
echo "export JAVA_HOME=$JAVA_HOME" >> /etc/profile.d/java.sh
source /etc/profile.d/java.sh

# Add Jenkins repository
echo "Adding Jenkins repository..."
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
sh -c 'echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

# Update and install Jenkins
apt-get update
apt-get install -y jenkins

# Install dependencies
apt-get install -y git maven curl wget

# Start Jenkins
echo "Starting Jenkins..."
systemctl start jenkins
systemctl enable jenkins

# Wait for Jenkins to initialize
echo "Waiting for Jenkins to initialize..."
for i in {1..60}; do
  if [ -f /var/lib/jenkins/secrets/initialAdminPassword ]; then
    break
  fi
  sleep 1
done

# Configure firewall
echo "Configuring firewall..."
apt-get install -y ufw
ufw --force enable
ufw allow 22/tcp
ufw allow 8080/tcp

echo "=== Jenkins Setup Completed at $(date) ==="
echo "Jenkins is accessible at: http://<your-ip>:8080"
```

---

## Deployment Instructions

### Using Terraform

```bash
# 1. Clone/download the Terraform files
cd terraform/

# 2. Initialize Terraform
terraform init

# 3. Review planned changes
terraform plan

# 4. Apply configuration
terraform apply

# 5. Get outputs
terraform output

# 6. To destroy resources when done
terraform destroy
```

### Using CloudFormation

```bash
# Via AWS CLI
aws cloudformation create-stack \
  --stack-name jenkins-mediflow \
  --template-body file://jenkins-stack.yaml \
  --parameters \
    ParameterKey=InstanceType,ParameterValue=t3.medium \
    ParameterKey=AllowedSSHCIDR,ParameterValue=YOUR_IP/32 \
  --region us-east-1

# Check stack status
aws cloudformation describe-stacks --stack-name jenkins-mediflow

# Get outputs
aws cloudformation describe-stacks \
  --stack-name jenkins-mediflow \
  --query 'Stacks[0].Outputs'

# Delete stack
aws cloudformation delete-stack --stack-name jenkins-mediflow
```

### Via AWS Console

1. Go to AWS CloudFormation console
2. Click "Create Stack"
3. Upload `jenkins-stack.yaml`
4. Fill in parameters
5. Review and create

---

## DevOps Best Practices Applied

1. **Infrastructure as Code**: All infrastructure is version-controlled and reproducible
2. **Security**: IAM roles, encrypted volumes, restricted security groups
3. **High Availability**: Can be extended with auto-scaling, load balancing
4. **Monitoring**: CloudWatch integration and log groups
5. **Cost Optimization**: Right-sized instances, gp3 volumes, lifecycle policies
6. **Disaster Recovery**: Separate EBS volume for Jenkins data, snapshots possible
7. **Compliance**: Tagging, audit trails, encryption

---

## Troubleshooting IaC Deployments

```bash
# Terraform issues
terraform validate  # Check syntax
terraform fmt -recursive  # Format files
terraform state list  # Show resources

# CloudFormation issues
aws cloudformation describe-stack-events --stack-name jenkins-mediflow
aws cloudformation validate-template --template-body file://jenkins-stack.yaml

# EC2 instance issues
aws ec2 describe-instances --filters "Name=tag:Name,Values=jenkins-server"
ssh -i your-key.pem ubuntu@<ip>
tail -f /var/log/jenkins-setup.log
```
