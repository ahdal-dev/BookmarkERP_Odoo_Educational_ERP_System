# ============================================================================
# modules/networking/outputs.tf
# ============================================================================

output "network_self_link" {
  description = "Self link of the VPC network."
  value       = google_compute_network.vpc.self_link
}

output "network_id" {
  description = "ID of the VPC network."
  value       = google_compute_network.vpc.id
}

output "subnet_self_link" {
  description = "Self link of the regional subnet."
  value       = google_compute_subnetwork.subnet.self_link
}

output "subnet_id" {
  description = "ID of the regional subnet."
  value       = google_compute_subnetwork.subnet.id
}
