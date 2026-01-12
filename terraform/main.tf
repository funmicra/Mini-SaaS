# ======================
# Provider
# ======================
provider "aws" {
  region  = "eu-central-1" # change to your region
  profile = "deploy"
}

# ======================
# Variables
# ======================
variable "instance_type" {
  default = "t3.micro"
}

variable "ssh_key_name" {
  default = "mini-saas-key" # your imported RSA key
}

variable "automation_pubkey" {
  default = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFX4JO+5+o85gZSKnFY1QfL8XaQRYANL6L/l6PDl4jRs funmicra@Titanas"
}

# ======================
# Data source for latest Ubuntu AMIs
# ======================
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# ======================
# VPC & Subnets
# ======================
resource "aws_vpc" "mini_saas_vpc" {
  cidr_block           = "192.168.33.0/24"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "mini-saas-vpc" }
}

data "aws_availability_zones" "available" {}

resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.mini_saas_vpc.id
  cidr_block              = "192.168.33.0/25"
  map_public_ip_on_launch = false
  availability_zone       = "eu-central-1a"
  tags                    = { Name = "mini-saas-private" }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.mini_saas_vpc.id
  cidr_block              = "192.168.33.128/25"
  map_public_ip_on_launch = true
  availability_zone       = "eu-central-1a"
  tags                    = { Name = "mini-saas-public" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.mini_saas_vpc.id
  tags   = { Name = "mini-saas-igw" }
}

# ======================
# Public Route Table
# ======================
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.mini_saas_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = { Name = "mini-saas-public-rt" }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# ======================
# NAT Gateway for Private Subnet
# ======================
resource "aws_eip" "nat_eip" {
  domain = "vpc"
  tags   = { Name = "mini-saas-nat-eip" }
}

resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet.id
  tags          = { Name = "mini-saas-nat" }
  depends_on    = [aws_internet_gateway.igw]
}

# Private Route Table
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.mini_saas_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = { Name = "mini-saas-private-rt" }
}

resource "aws_route_table_association" "private_assoc" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_rt.id
}

# ======================
# Security Groups
# ======================
resource "aws_security_group" "frontend_sg" {
  name        = "frontend-sg"
  description = "Allow SSH and HTTP from anywhere"
  vpc_id      = aws_vpc.mini_saas_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "backend_sg" {
  name        = "backend-sg"
  description = "Allow only frontend subnet access"
  vpc_id      = aws_vpc.mini_saas_vpc.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["192.168.33.128/25"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ======================
# Cloud-init user_data template
# ======================
locals {
  cloud_init = <<-EOF
                #cloud-config
                users:
                  - name: ansible
                    gecos: "Automation User"
                    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
                    groups: sudo
                    shell: /bin/bash
                    ssh_authorized_keys:
                      - ${var.automation_pubkey}
                EOF
}

# ======================
# EC2 Instances
# ======================
resource "aws_instance" "frontend" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public_subnet.id
  key_name               = var.ssh_key_name
  vpc_security_group_ids = [aws_security_group.frontend_sg.id]
  user_data              = local.cloud_init
  tags                   = { Name = "mini-saas-frontend" }
}

resource "aws_instance" "backend" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.private_subnet.id
  key_name                    = var.ssh_key_name
  vpc_security_group_ids      = [aws_security_group.backend_sg.id]
  associate_public_ip_address = false
  user_data                   = local.cloud_init
  tags                        = { Name = "mini-saas-backend" }
}

# ======================
# Outputs
# ======================

# Frontend
output "frontend_public_ip" {
  description = "Public IP of the frontend EC2"
  value       = aws_instance.frontend.public_ip
}

output "frontend_private_ip" {
  description = "Private IP of the frontend EC2"
  value       = aws_instance.frontend.private_ip
}

output "frontend_instance_id" {
  description = "EC2 instance ID of frontend"
  value       = aws_instance.frontend.id
}

output "frontend_sg_id" {
  description = "Security group ID of frontend"
  value       = aws_security_group.frontend_sg.id
}

# Backend
output "backend_private_ip" {
  description = "Private IP of the backend EC2"
  value       = aws_instance.backend.private_ip
}

output "backend_instance_id" {
  description = "EC2 instance ID of backend"
  value       = aws_instance.backend.id
}

output "backend_sg_id" {
  description = "Security group ID of backend"
  value       = aws_security_group.backend_sg.id
}

# Subnets & VPC
output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.public_subnet.id
}

output "private_subnet_id" {
  description = "ID of the private subnet"
  value       = aws_subnet.private_subnet.id
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.mini_saas_vpc.id
}

# NAT Gateway
output "nat_gateway_id" {
  description = "NAT Gateway ID"
  value       = aws_nat_gateway.nat_gw.id
}

output "nat_eip" {
  description = "NAT Gateway Elastic IP"
  value       = aws_eip.nat_eip.public_ip
}