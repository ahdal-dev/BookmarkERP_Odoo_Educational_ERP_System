# ============================================================================
# environments/free-tier.tfvars  ->  $0.00 / month (Always-Free only)
# ----------------------------------------------------------------------------
# Deploys ONLY the e2-micro proxy VM. The App and AI VMs are skipped, so this
# is a minimal "landing page / static SPA + nginx" footprint that stays inside
# the GCP Always-Free allowance. Use this to validate networking/IaC at $0
# before turning on the paid VMs.
#
# Apply:
#   terraform apply -var-file=environments/free-tier.tfvars
# ============================================================================

environment = "free-tier"
region      = "us-central1" # Free-Tier eligible region
zone        = "us-central1-a"

# Only the always-free micro.
proxy_machine_type = "e2-micro"
proxy_disk_gb      = 10
disk_type          = "pd-standard" # Free Tier requires Standard PD

# Skip the paid VMs entirely.
deploy_app_vm = false
deploy_ai_vm  = false

# Keep storage tiny.
backup_retention_days = 7
upload_retention_days = 3

enable_dns = false

# Lock SSH down to your IP (override here or in terraform.tfvars).
# ssh_source_ranges = ["YOUR.IP.ADDR.ESS/32"]
