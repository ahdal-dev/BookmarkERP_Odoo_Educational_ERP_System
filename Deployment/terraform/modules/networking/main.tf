# ============================================================================
# modules/networking/main.tf - VPC, Subnet, Cloud Router, Cloud NAT
# ============================================================================

# Custom-mode VPC: we define our own subnets (no auto subnets) for tight control.
resource "google_compute_network" "vpc" {
  name                    = "${var.name_prefix}-vpc"
  project                 = var.project_id
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

# Single regional subnet. Private Google Access lets the no-public-IP VMs reach
# Google APIs (Secret Manager, GCS, Artifact Registry) without a NAT hop.
resource "google_compute_subnetwork" "subnet" {
  name                     = "${var.name_prefix}-subnet"
  project                  = var.project_id
  region                   = var.region
  network                  = google_compute_network.vpc.id
  ip_cidr_range            = var.subnet_cidr
  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Cloud Router is required to attach Cloud NAT.
resource "google_compute_router" "router" {
  name    = "${var.name_prefix}-router"
  project = var.project_id
  region  = var.region
  network = google_compute_network.vpc.id
}

# Cloud NAT gives the App/AI VMs (which have NO external IP) outbound internet
# access for calls to Mistral / OpenRouter / OpenAI and for pulling images.
resource "google_compute_router_nat" "nat" {
  name                               = "${var.name_prefix}-nat"
  project                            = var.project_id
  region                             = var.region
  router                             = google_compute_router.router.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}
