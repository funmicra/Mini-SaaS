# ------------------------
# Outputs
# ------------------------
output "proxy_public_ip" {
  description = "Public IPv4 of the proxy instance"
  value       = tolist(linode_instance.proxy.ipv4)[0]
}

output "private_ips" {
  description = "Private IPs of workload nodes"
  value       = [
    for i in linode_instance.private : i.interface[0].ipv4[0].vpc
  ]
}

output "proxy_id" {
  value = linode_instance.proxy.id
}

output "instance_ids" {
  value = [
    for vm in linode_instance.private : vm.id
  ]
}

output "vpc_id" {
  description = "Terraform ID of the private VPC"
  value       = linode_vpc.private.id
}