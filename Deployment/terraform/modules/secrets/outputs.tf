# ============================================================================
# modules/secrets/outputs.tf
# ============================================================================

output "secret_ids" {
  description = "Full secret IDs created (name_prefix-<short-name>)."
  value       = [for s in google_secret_manager_secret.this : s.secret_id]
}
