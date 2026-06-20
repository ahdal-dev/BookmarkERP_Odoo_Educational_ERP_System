# ============================================================================
# modules/dns/outputs.tf
# ============================================================================

output "name_servers" {
  description = "Delegate these NS records at your registrar (empty if DNS disabled)."
  value       = var.enable_dns ? google_dns_managed_zone.zone[0].name_servers : []
}

output "zone_name" {
  value = var.enable_dns ? google_dns_managed_zone.zone[0].name : null
}
