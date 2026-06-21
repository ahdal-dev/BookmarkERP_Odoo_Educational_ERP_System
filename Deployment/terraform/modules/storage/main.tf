# ============================================================================
# modules/storage/main.tf - GCS Buckets (state, backups, uploads)
# ============================================================================
# NOTE: The Terraform *state* bucket is referenced by backend.tf and must be
# created out-of-band BEFORE `terraform init` (see CLAUDE.md Phase 2). This
# module manages the runtime buckets (backups, uploads) plus an optional,
# import-able state bucket resource for documentation.
# ============================================================================

# Database backups - lifecycle deletes objects after N days.
resource "google_storage_bucket" "backups" {
  name                        = "${var.project_id}-${var.name_prefix}-backups"
  project                     = var.project_id
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = false
  labels                      = var.labels

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = var.backup_retention_days
    }
    action {
      type = "Delete"
    }
  }
}

# OCR uploads - short-lived scratch storage.
resource "google_storage_bucket" "uploads" {
  name                        = "${var.project_id}-${var.name_prefix}-uploads"
  project                     = var.project_id
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = true
  labels                      = var.labels

  lifecycle_rule {
    condition {
      age = var.upload_retention_days
    }
    action {
      type = "Delete"
    }
  }
}
