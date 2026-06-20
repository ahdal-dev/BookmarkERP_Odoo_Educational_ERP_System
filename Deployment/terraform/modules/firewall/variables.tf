# ============================================================================
# modules/firewall/variables.tf
# ============================================================================

variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "network_self_link" {
  description = "Self link of the VPC the rules attach to."
  type        = string
}

variable "subnet_cidr" {
  description = "Subnet CIDR used as the source range for internal mesh rules."
  type        = string
}

variable "ssh_source_ranges" {
  description = "CIDRs allowed direct SSH to the proxy VM."
  type        = list(string)
}

variable "proxy_tag" {
  description = "Network tag identifying the proxy VM."
  type        = string
}

variable "app_tag" {
  description = "Network tag identifying the app VM."
  type        = string
}

variable "ai_tag" {
  description = "Network tag identifying the AI VM."
  type        = string
}
