# ------------------------
# VPC
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
  label  = "proxy-node"
  region = var.region
  type   = "g6-nanode-1"
  image  = "linode/ubuntu24.04"

  private_ip = "192.168.33.250"
  ipv4       = true
  vpc_id     = linode_vpc.private.id
}

# Passwordless Ansible user on Proxy
resource "linode_user" "ansible_proxy" {
  username   = "ansible"
  restricted = false
  ssh_keys   = [file("terraform/ssh_key.b64")]
  linode_id  = linode_instance.proxy.id
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

  private_ip = "192.168.33.${10 + count.index}"
  vpc_id     = linode_vpc.private.id
}

# Passwordless Ansible user on Private nodes
resource "linode_user" "ansible_private" {
  count      = var.private_count
  username   = "ansible"
  restricted = false
  ssh_keys   = [file("terraform/ssh_key.b64")]
  linode_id  = linode_instance.private[count.index].id
}

# ------------------------
# Firewall — Proxy Node
# ------------------------
resource "linode_firewall" "proxy_fw" {
  label = "fw-proxy"

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

  linodes = [linode_instance.proxy.id]
}

# ------------------------
# Firewall — Private Nodes
# ------------------------
resource "linode_firewall" "private_fw" {
  label = "fw-private"

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

  linodes = [for vm in linode_instance.private : vm.id]
}