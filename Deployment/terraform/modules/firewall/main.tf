# ============================================================================
# modules/firewall/main.tf - VPC Firewall Rules
# ============================================================================
# Default GCP behaviour is "deny all ingress / allow all egress". We add the
# minimum ingress needed and keep everything else denied.
#
# Rules:
#   1. Public HTTP/HTTPS -> proxy VM only
#   2. SSH from your IP   -> proxy VM only
#   3. SSH from IAP range -> all VMs (App/AI have no public IP)
#   4. Internal mesh      -> all VMs talk to each other on any port
#   5. ICMP               -> health checks / debugging within the subnet
#   6. Explicit deny-all  -> low-priority catch-all (belt and suspenders)
# ============================================================================

# 1. Public web traffic to the proxy only.
resource "google_compute_firewall" "allow_web" {
  name      = "${var.name_prefix}-allow-web"
  project   = var.project_id
  network   = var.network_self_link
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = [var.proxy_tag]
}

# 2. Direct SSH only to the proxy, only from your IP(s).
resource "google_compute_firewall" "allow_ssh_admin" {
  name      = "${var.name_prefix}-allow-ssh-admin"
  project   = var.project_id
  network   = var.network_self_link
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = var.ssh_source_ranges
  target_tags   = [var.proxy_tag]
}

# 3. IAP TCP forwarding range -> SSH to ALL VMs (so App/AI need no public IP).
#    35.235.240.0/20 is Google's fixed IAP range.
resource "google_compute_firewall" "allow_iap_ssh" {
  name      = "${var.name_prefix}-allow-iap-ssh"
  project   = var.project_id
  network   = var.network_self_link
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]
  target_tags   = [var.proxy_tag, var.app_tag, var.ai_tag]
}

# 4. Full internal mesh between the three VMs over the VPC subnet.
#    This is what lets nginx reach the app VM, the gateway reach the AI VM,
#    and the AI VM reach Odoo/RabbitMQ on the app VM.
resource "google_compute_firewall" "allow_internal" {
  name      = "${var.name_prefix}-allow-internal"
  project   = var.project_id
  network   = var.network_self_link
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [var.subnet_cidr]
  target_tags   = [var.proxy_tag, var.app_tag, var.ai_tag]
}

# 5. ICMP from anywhere to the proxy (ping / health checks). Optional but handy.
resource "google_compute_firewall" "allow_icmp" {
  name      = "${var.name_prefix}-allow-icmp"
  project   = var.project_id
  network   = var.network_self_link
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "icmp"
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = [var.proxy_tag]
}

# 6. Explicit low-priority deny-all ingress. GCP already implicitly denies, but
#    this makes intent obvious and logs blocked attempts.
resource "google_compute_firewall" "deny_all_ingress" {
  name      = "${var.name_prefix}-deny-all-ingress"
  project   = var.project_id
  network   = var.network_self_link
  direction = "INGRESS"
  priority  = 65534

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}
