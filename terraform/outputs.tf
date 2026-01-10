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
