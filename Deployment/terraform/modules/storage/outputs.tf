# ============================================================================
# modules/storage/outputs.tf
# ============================================================================

output "backups_bucket_name" {
  value = google_storage_bucket.backups.name
}

output "uploads_bucket_name" {
  value = google_storage_bucket.uploads.name
}

output "backups_bucket_url" {
  value = google_storage_bucket.backups.url
}

output "uploads_bucket_url" {
  value = google_storage_bucket.uploads.url
}
