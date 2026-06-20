# ============================================================================
# variables.tf - Root Input Variables
# ============================================================================

# ----------------------------------------------------------------------------
# Core project / location
# ----------------------------------------------------------------------------
variable "project_id" {
  description = "GCP project ID to deploy into."
  type        = string
}

variable "region" {
  description = "GCP region. Use a Free-Tier region (us-central1, us-west1, us-east1) so the e2-micro stays free."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone for the zonal GCE instances."
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Deployment environment label (free-tier | trial-credits)."
  type        = string
  default     = "trial-credits"
}

variable "name_prefix" {
  description = "Prefix applied to all resource names for easy identification."
  type        = string
  default     = "edu-erp"
}

variable "labels" {
  description = "Common labels applied to all supporting resources."
  type        = map(string)
  default = {
    project = "bookmark-academic-erp"
    managed = "terraform"
  }
}

# ----------------------------------------------------------------------------
# Networking
# ----------------------------------------------------------------------------
variable "subnet_cidr" {
  description = "Primary CIDR for the single regional subnet."
  type        = string
  default     = "10.0.0.0/24"
}

variable "ssh_source_ranges" {
  description = "CIDRs allowed to SSH directly to the proxy VM (your office/home IP). Keep this tight. App/AI VMs use IAP only."
  type        = list(string)
  default     = ["0.0.0.0/0"] # CHANGE ME to your.ip.addr.ess/32
}

# Static private IPs so cross-VM service URLs are predictable.
variable "proxy_internal_ip" {
  description = "Static internal IP for the proxy VM."
  type        = string
  default     = "10.0.0.10"
}

variable "app_internal_ip" {
  description = "Static internal IP for the app VM."
  type        = string
  default     = "10.0.0.11"
}

variable "ai_internal_ip" {
  description = "Static internal IP for the AI VM."
  type        = string
  default     = "10.0.0.12"
}

# ----------------------------------------------------------------------------
# Compute - machine types (overridden per environment tfvars)
# ----------------------------------------------------------------------------
variable "proxy_machine_type" {
  description = "Proxy VM machine type. e2-micro is Always-Free in us-central1/us-west1/us-east1."
  type        = string
  default     = "e2-micro"
}

variable "app_machine_type" {
  description = "App VM machine type (Odoo + gateway + datastores)."
  type        = string
  default     = "e2-standard-2"
}

variable "ai_machine_type" {
  description = "AI VM machine type (OCR + predictors + agent)."
  type        = string
  default     = "e2-medium"
}

variable "proxy_disk_gb" {
  description = "Proxy boot disk size (GB). Keep total Standard PD <= 30GB to stay in Free Tier."
  type        = number
  default     = 10
}

variable "app_disk_gb" {
  description = "App boot disk size (GB)."
  type        = number
  default     = 50
}

variable "ai_disk_gb" {
  description = "AI boot disk size (GB)."
  type        = number
  default     = 30
}

variable "disk_type" {
  description = "Persistent disk type. pd-standard is Free-Tier eligible; pd-balanced/pd-ssd are NOT."
  type        = string
  default     = "pd-standard"
}

variable "vm_image" {
  description = "Boot image family for the VMs."
  type        = string
  default     = "projects/debian-cloud/global/images/family/debian-12"
}

variable "deploy_ai_vm" {
  description = "Whether to create the AI VM. Set false in free-tier to keep cost at $0."
  type        = bool
  default     = true
}

variable "deploy_app_vm" {
  description = "Whether to create the App VM. Set false in free-tier (proxy-only) to keep cost at $0."
  type        = bool
  default     = true
}

# ----------------------------------------------------------------------------
# Deployment automation (optional)
# ----------------------------------------------------------------------------
variable "repo_url" {
  description = "Git URL the VM startup scripts clone for the compose/config files. Leave empty to deploy manually."
  type        = string
  default     = ""
}

variable "repo_branch" {
  description = "Git branch/ref to check out on the VMs."
  type        = string
  default     = "main"
}

variable "auto_deploy" {
  description = "If true (and repo_url set), startup scripts run docker compose automatically after boot."
  type        = bool
  default     = false
}

# ----------------------------------------------------------------------------
# Storage
# ----------------------------------------------------------------------------
variable "backup_retention_days" {
  description = "Days to retain DB backups in the backups bucket before lifecycle deletion."
  type        = number
  default     = 30
}

variable "upload_retention_days" {
  description = "Days to retain OCR uploads before lifecycle deletion."
  type        = number
  default     = 7
}

# ----------------------------------------------------------------------------
# Secrets - values are optional here; prefer adding versions via gcloud.
# Marked sensitive so they never print in plan/apply output.
# ----------------------------------------------------------------------------
variable "secret_values" {
  description = <<-EOT
    Optional map of secret_id => value. Any entry left empty ("") creates the
    secret container WITHOUT a version (add the value later with
    `gcloud secrets versions add`). Keys must match the fixed secret IDs
    defined in modules/secrets.
  EOT
  type        = map(string)
  sensitive   = true
  default     = {}
}

# ----------------------------------------------------------------------------
# DNS (optional)
# ----------------------------------------------------------------------------
variable "enable_dns" {
  description = "Create a Cloud DNS managed zone + A record for the proxy VM."
  type        = bool
  default     = false
}

variable "dns_zone_name" {
  description = "Cloud DNS managed zone resource name (lowercase, hyphens)."
  type        = string
  default     = "edu-erp-zone"
}

variable "dns_domain" {
  description = "DNS domain (FQDN with trailing dot), e.g. erp.example.com."
  type        = string
  default     = ""
}
