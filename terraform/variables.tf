# ------------------------
# Variables
# ------------------------
variable "linode_token" {
  sensitive   = true
}

variable "region" {
  default = "de-fra-2"
}

variable "username" {
  type      = string
  sensitive = true
}

variable "private_count" {
  default = 1
}

variable "user_password" {
  type      = string
  sensitive = true
}

variable "ssh_pubkey_path" {
  description = "Path to the public SSH key for Ansible"
  default     = "terraform/ansible.pub"
}

variable "ansible_email" {
  description = "Email for the Ansible user"
  default     = "el.funmicra@gmail.com"
}