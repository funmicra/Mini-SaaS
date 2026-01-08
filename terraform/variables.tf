# ------------------------
# Variables
# ------------------------
variable "linode_token" {
  sensitive   = true
}

variable "region" {
  default = "de-fra-2"
}

variable "proxy_stackscript_id" {
  default = 1975956
}

variable "private_stackscript_id" {
  default = 1975967
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