# ============================================================================
# versions.tf - Required Terraform & Provider Versions
# ============================================================================
# Pins Terraform and the Google providers so plans are reproducible across
# machines. The google-beta provider is included for resources that are only
# exposed in beta (e.g. some Secret Manager / OS Login features).
# ============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.40"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.40"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
