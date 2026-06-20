# ============================================================================
# outputs.tf - Root Outputs (IPs, URLs, helper commands)
# ============================================================================

output "proxy_external_ip" {
  description = "Public static IP of the proxy VM. Point your DNS A record here."
  value       = module.compute.proxy_external_ip
}

output "proxy_internal_ip" {
  description = "Internal IP of the proxy VM."
  value       = var.proxy_internal_ip
}

output "app_internal_ip" {
  description = "Internal IP of the app VM (no public IP - reach via IAP)."
  value       = var.app_internal_ip
}

output "ai_internal_ip" {
  description = "Internal IP of the AI VM (no public IP - reach via IAP)."
  value       = var.ai_internal_ip
}

output "app_url" {
  description = "Public URL once DNS/proxy are up."
  value       = var.enable_dns && var.dns_domain != "" ? "https://${trimsuffix(var.dns_domain, ".")}" : "http://${module.compute.proxy_external_ip}"
}

output "vpc_network" {
  description = "Self link of the custom VPC."
  value       = module.networking.network_self_link
}

output "backups_bucket" {
  description = "GCS bucket for database backups."
  value       = module.storage.backups_bucket_name
}

output "uploads_bucket" {
  description = "GCS bucket for OCR uploads."
  value       = module.storage.uploads_bucket_name
}

output "secret_ids" {
  description = "Secret Manager secret IDs created for the deployment."
  value       = module.secrets.secret_ids
}

# ----------------------------------------------------------------------------
# Convenience: ready-to-paste IAP SSH commands (App/AI have no public IP)
# ----------------------------------------------------------------------------
output "ssh_proxy" {
  description = "SSH to the proxy VM."
  value       = "gcloud compute ssh ${var.name_prefix}-proxy --zone ${var.zone} --project ${var.project_id}"
}

output "ssh_app_via_iap" {
  description = "SSH to the app VM through IAP (no public IP)."
  value       = "gcloud compute ssh ${var.name_prefix}-app --zone ${var.zone} --project ${var.project_id} --tunnel-through-iap"
}

output "ssh_ai_via_iap" {
  description = "SSH to the AI VM through IAP (no public IP)."
  value       = "gcloud compute ssh ${var.name_prefix}-ai --zone ${var.zone} --project ${var.project_id} --tunnel-through-iap"
}
