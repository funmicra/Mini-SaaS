# ------------------------
# VPC and Subnet
# ------------------------
resource "linode_vpc" "private" {
  label  = "private-vpc"
  region = var.region
}

resource "linode_vpc_subnet" "private" {
  label  = "private-subnet"
  vpc_id = linode_vpc.private.id
  ipv4   = "192.168.33.0/24"
}

# ------------------------
# Proxy Linode
# ------------------------
resource "linode_instance" "proxy" {
  label  = "vpc-forward-proxy"
  region = var.region
  type   = "g6-nanode-1"
  image  = "linode/ubuntu24.04"

  stackscript_id   = var.proxy_stackscript_id
 # stackscript_data = {
 #   username = var.username
 #   user_password  = var.user_password
 #   ssh_key_b64 = file("ssh_key.b64")
 # }

  # Public interface
  interface {
    purpose = "public"
  }

  # VPC interface with fixed IP
  interface {
    purpose = "vpc"
    subnet_id = linode_vpc_subnet.private.id
    
    ipv4 {
        vpc = "192.168.33.250"
    }
  }

  tags = ["gateway", "vpc", "edge"]
}

# ------------------------
# Firewall — Proxy Node
# ------------------------
resource "linode_firewall" "proxy_fw" {
  label = "fw-proxy-edge"

  inbound {
    label    = "allow-ssh"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "22"
    ipv4     = ["0.0.0.0/0"]
  }

  inbound {
    label    = "allow-http"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "80"
    ipv4     = ["0.0.0.0/0"]
  }

  inbound {
    label    = "allow-https"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "443"
    ipv4     = ["0.0.0.0/0"]
  }

  inbound_policy  = "DROP"
  outbound_policy = "ACCEPT"

  linodes = [
    linode_instance.proxy.id
  ]
}



# ------------------------
# Private Linodes
# ------------------------
resource "linode_instance" "private" {
  count  = var.private_count
  label  = "private-${count.index}"
  region = var.region
  type   = "g6-standard-1"
  image  = "linode/ubuntu24.04"

  stackscript_id   = var.private_stackscript_id
 # stackscript_data = {
 #   username = var.username
 #   user_password  = var.user_password
 #   ssh_key_b64 = file("ssh_key.b64")
 # }

  interface {
    purpose   = "vpc"
    subnet_id = linode_vpc_subnet.private.id

    ipv4 {
      vpc = "192.168.33.${10 + count.index}"
    }
  }

  tags = ["private", "workload"]
}


# ------------------------
# Firewall — Private Nodes
# ------------------------
resource "linode_firewall" "private_fw" {
  label = "fw-private-workloads"

  inbound {
    label    = "allow-ssh-from-proxy"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "22"
    ipv4     = ["192.168.33.250/32"]
  }

  inbound {
    label    = "allow-app-from-proxy"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "3000"
    ipv4     = ["192.168.33.250/32"]
  }

  inbound_policy  = "DROP"
  outbound_policy = "ACCEPT"

  linodes = [
    for vm in linode_instance.private : vm.id
  ]
}



