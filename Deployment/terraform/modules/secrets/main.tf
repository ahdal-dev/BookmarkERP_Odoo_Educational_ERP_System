# ============================================================================
# modules/secrets/main.tf - Secret Manager containers, versions & IAM
# ============================================================================
# Creates one secret per credential. A *version* is only created when a
# non-empty value is supplied via var.secret_values (otherwise add it later
# with `gcloud secrets versions add`). Each VM service account is granted
# secretAccessor on every secret (minimal privilege: read-only).
# ============================================================================

locals {
  # Fixed set of secret short-names. The actual secret_id is name_prefix-<name>.
  secret_names = [
    "odoo-password",
    "postgres-password",
    "jwt-secret-key",
    "chatbot-shared-secret",
    "openrouter-api-key",
    "mistral-api-key",
    "rabbitmq-user",
    "rabbitmq-password",
    "redis-password",
    "grafana-password",
  ]

  # Only create versions for entries that were actually provided.
  provided_values = {
    for k, v in var.secret_values : k => v if v != ""
  }
}

resource "google_secret_manager_secret" "this" {
  for_each  = toset(local.secret_names)
  project   = var.project_id
  secret_id = "${var.name_prefix}-${each.value}"
  labels    = var.labels

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "this" {
  for_each    = local.provided_values
  secret      = google_secret_manager_secret.this[each.key].id
  secret_data = each.value
}

# Grant each VM service account read access to every secret.
resource "google_secret_manager_secret_iam_member" "accessor" {
  for_each = {
    # Cartesian product of secrets x service accounts
    for pair in setproduct(local.secret_names, var.accessor_service_accounts) :
    "${pair[0]}::${pair[1]}" => {
      secret = pair[0]
      sa     = pair[1]
    }
  }

  project   = var.project_id
  secret_id = google_secret_manager_secret.this[each.value.secret].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${each.value.sa}"
}
