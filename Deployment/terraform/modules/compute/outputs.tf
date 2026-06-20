# ============================================================================
# modules/compute/outputs.tf
# ============================================================================

output "proxy_external_ip" {
  description = "Static external IP attached to the proxy VM."
  value       = google_compute_address.proxy.address
}

output "proxy_service_account_email" {
  value = google_service_account.proxy.email
}

output "app_service_account_email" {
  value = google_service_account.app.email
}

output "ai_service_account_email" {
  value = google_service_account.ai.email
}

output "app_instance_name" {
  value = var.deploy_app_vm ? google_compute_instance.app[0].name : null
}

output "ai_instance_name" {
  value = var.deploy_ai_vm ? google_compute_instance.ai[0].name : null
}
