# ============================================================================
# modules/networking/variables.tf
# ============================================================================

variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "Region for the subnet, router and NAT."
  type        = string
}

variable "name_prefix" {
  description = "Resource name prefix."
  type        = string
}

variable "subnet_cidr" {
  description = "CIDR range for the regional subnet."
  type        = string
}
