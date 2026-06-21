# ============================================================================
# modules/compute/variables.tf
# ============================================================================

variable "project_id" { type = string }
variable "region" { type = string }
variable "zone" { type = string }
variable "name_prefix" { type = string }
variable "labels" {
  type    = map(string)
  default = {}
}

variable "subnet_self_link" {
  description = "Self link of the subnet the VMs attach to."
  type        = string
}

# Machine types
variable "proxy_machine_type" { type = string }
variable "app_machine_type" { type = string }
variable "ai_machine_type" { type = string }

# Disks
variable "proxy_disk_gb" { type = number }
variable "app_disk_gb" { type = number }
variable "ai_disk_gb" { type = number }
variable "disk_type" { type = string }
variable "vm_image" { type = string }

# Static internal IPs
variable "proxy_internal_ip" { type = string }
variable "app_internal_ip" { type = string }
variable "ai_internal_ip" { type = string }

# Toggles
variable "deploy_app_vm" {
  type    = bool
  default = true
}
variable "deploy_ai_vm" {
  type    = bool
  default = true
}

# Cross-VM wiring injected into the rendered .env
variable "app_ip" { type = string }
variable "ai_ip" { type = string }

# Optional auto-deploy
variable "repo_url" {
  type    = string
  default = ""
}
variable "repo_branch" {
  type    = string
  default = "main"
}
variable "auto_deploy" {
  type    = bool
  default = false
}

variable "backups_bucket" {
  description = "Name of the GCS backups bucket the app SA may write to."
  type        = string
}
