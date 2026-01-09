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