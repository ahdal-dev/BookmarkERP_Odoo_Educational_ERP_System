# ============================================================================
# environments/trial-credits.tfvars  ->  ~$76 / month (full stack)
# ----------------------------------------------------------------------------
# Full 3-VM deployment funded by the $300 free-trial credits (~3.9 months).
#   - proxy : e2-micro      (Always-Free)        nginx + React SPA
#   - app   : e2-standard-2 (~$49/mo)            odoo + gateway + pg/redis/rabbitmq
#   - ai    : e2-medium     (~$25/mo)            ocr + predictors + agent + worker
#
# Apply:
#   terraform apply -var-file=environments/trial-credits.tfvars
# ============================================================================

environment = "trial-credits"
region      = "us-central1"
zone        = "us-central1-a"

proxy_machine_type = "e2-micro"      # Always-Free
app_machine_type   = "e2-standard-2" # 2 vCPU / 8 GB
ai_machine_type    = "e2-medium"     # 1 vCPU / 4 GB

proxy_disk_gb = 10
app_disk_gb   = 50
ai_disk_gb    = 30
disk_type     = "pd-standard"

deploy_app_vm = true
deploy_ai_vm  = true

backup_retention_days = 30
upload_retention_days = 7

enable_dns = false
# enable_dns    = true
# dns_domain    = "erp.example.com."
# dns_zone_name = "edu-erp-zone"

# Lock SSH down to your IP (override here or in terraform.tfvars).
# ssh_source_ranges = ["YOUR.IP.ADDR.ESS/32"]
