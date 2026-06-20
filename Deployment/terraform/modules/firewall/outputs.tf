# ============================================================================
# modules/firewall/outputs.tf
# ============================================================================

output "firewall_rule_names" {
  description = "Names of all firewall rules created by this module."
  value = [
    google_compute_firewall.allow_web.name,
    google_compute_firewall.allow_ssh_admin.name,
    google_compute_firewall.allow_iap_ssh.name,
    google_compute_firewall.allow_internal.name,
    google_compute_firewall.allow_icmp.name,
    google_compute_firewall.deny_all_ingress.name,
  ]
}
