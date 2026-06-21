# ============================================================================
# main.tf - Root Module (provider + module wiring)
# ============================================================================
# Topology (3-VM Docker-Compose-on-GCE, Free-Tier optimised):
#
#   Internet
#      |  (80/443, SSH from your IP)
#   [ proxy VM  e2-micro  | external static IP ]  nginx + React SPA
#      |  (VPC internal)
#   [ app VM  e2-standard-2 | no external IP ]    odoo + gateway + pg + redis + rabbitmq
#   [ ai  VM  e2-medium     | no external IP ]    ocr + predictors + agent + worker
#      |
#   Cloud NAT  ->  outbound to LLM/OCR APIs
# ============================================================================

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

locals {
  # Cross-VM service URLs derived from the static internal IPs. These are
  # injected into the per-VM .env so containers on one VM can reach services
  # on another over the VPC.
  app_ip = var.app_internal_ip
  ai_ip  = var.ai_internal_ip
}

# ----------------------------------------------------------------------------
# Networking: custom VPC, regional subnet, Cloud Router + Cloud NAT
# ----------------------------------------------------------------------------
module "networking" {
  source = "./modules/networking"

  project_id  = var.project_id
  region      = var.region
  name_prefix = var.name_prefix
  subnet_cidr = var.subnet_cidr
}

# ----------------------------------------------------------------------------
# Firewall: ingress to proxy, internal mesh, IAP SSH, ICMP
# ----------------------------------------------------------------------------
module "firewall" {
  source = "./modules/firewall"

  project_id        = var.project_id
  name_prefix       = var.name_prefix
  network_self_link = module.networking.network_self_link
  subnet_cidr       = var.subnet_cidr
  ssh_source_ranges = var.ssh_source_ranges

  proxy_tag = "${var.name_prefix}-proxy"
  app_tag   = "${var.name_prefix}-app"
  ai_tag    = "${var.name_prefix}-ai"
}

# ----------------------------------------------------------------------------
# Storage: state (referenced), backups, uploads buckets
# ----------------------------------------------------------------------------
module "storage" {
  source = "./modules/storage"

  project_id            = var.project_id
  region                = var.region
  name_prefix           = var.name_prefix
  labels                = var.labels
  backup_retention_days = var.backup_retention_days
  upload_retention_days = var.upload_retention_days
}

# ----------------------------------------------------------------------------
# Compute: 3 VMs + per-VM service accounts + startup scripts
# ----------------------------------------------------------------------------
module "compute" {
  source = "./modules/compute"

  project_id  = var.project_id
  region      = var.region
  zone        = var.zone
  name_prefix = var.name_prefix
  labels      = var.labels

  subnet_self_link = module.networking.subnet_self_link

  proxy_machine_type = var.proxy_machine_type
  app_machine_type   = var.app_machine_type
  ai_machine_type    = var.ai_machine_type

  proxy_disk_gb = var.proxy_disk_gb
  app_disk_gb   = var.app_disk_gb
  ai_disk_gb    = var.ai_disk_gb
  disk_type     = var.disk_type
  vm_image      = var.vm_image

  proxy_internal_ip = var.proxy_internal_ip
  app_internal_ip   = var.app_internal_ip
  ai_internal_ip    = var.ai_internal_ip

  deploy_app_vm = var.deploy_app_vm
  deploy_ai_vm  = var.deploy_ai_vm

  # Cross-VM wiring for the rendered .env files
  app_ip = local.app_ip
  ai_ip  = local.ai_ip

  # Optional auto-deploy
  repo_url    = var.repo_url
  repo_branch = var.repo_branch
  auto_deploy = var.auto_deploy

  # Backups bucket the app SA may write to
  backups_bucket = module.storage.backups_bucket_name
}

# ----------------------------------------------------------------------------
# Secrets: Secret Manager containers + IAM grants to the VM service accounts
# ----------------------------------------------------------------------------
module "secrets" {
  source = "./modules/secrets"

  project_id    = var.project_id
  region        = var.region
  name_prefix   = var.name_prefix
  labels        = var.labels
  secret_values = var.secret_values

  # Each VM SA gets secretAccessor on every secret (minimal: accessor only).
  accessor_service_accounts = compact([
    module.compute.proxy_service_account_email,
    module.compute.app_service_account_email,
    module.compute.ai_service_account_email,
  ])
}

# ----------------------------------------------------------------------------
# DNS (optional): managed zone + A record pointing at the proxy external IP
# ----------------------------------------------------------------------------
module "dns" {
  source = "./modules/dns"

  enable_dns    = var.enable_dns
  project_id    = var.project_id
  dns_zone_name = var.dns_zone_name
  dns_domain    = var.dns_domain
  proxy_ip      = module.compute.proxy_external_ip
}
