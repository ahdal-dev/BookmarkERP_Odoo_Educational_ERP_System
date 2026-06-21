# ============================================================================
# modules/dns/main.tf - Optional Cloud DNS managed zone + A record
# ============================================================================
# Entirely optional. Enable with var.enable_dns = true and supply a domain.
# After apply, point your registrar's NS records at the zone's name servers
# (see the name_servers output).
# ============================================================================

resource "google_dns_managed_zone" "zone" {
  count       = var.enable_dns ? 1 : 0
  project     = var.project_id
  name        = var.dns_zone_name
  dns_name    = var.dns_domain # must end with a trailing dot, e.g. "erp.example.com."
  description = "Managed zone for the Bookmark Academic ERP."
}

resource "google_dns_record_set" "a" {
  count        = var.enable_dns ? 1 : 0
  project      = var.project_id
  managed_zone = google_dns_managed_zone.zone[0].name
  name         = var.dns_domain
  type         = "A"
  ttl          = 300
  rrdatas      = [var.proxy_ip]
}
