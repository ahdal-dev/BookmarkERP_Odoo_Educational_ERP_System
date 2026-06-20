# ============================================================================
# backend.tf - Remote State (Google Cloud Storage)
# ============================================================================
# Terraform state is stored in a versioned GCS bucket so the team shares one
# source of truth and state is never committed to git.
#
# The bucket name CANNOT be a variable (backends are initialised before
# variables are evaluated). Two options:
#
#   1. Hard-code the bucket below, OR
#   2. Leave `bucket` out and pass it at init time (recommended):
#        terraform init -backend-config="bucket=YOUR_TF_STATE_BUCKET"
#
# Create the bucket BEFORE the first `terraform init` (see Deployment/CLAUDE.md
# Phase 2):
#   gsutil mb -p PROJECT_ID -l us-central1 gs://YOUR_TF_STATE_BUCKET
#   gsutil versioning set on gs://YOUR_TF_STATE_BUCKET
# ============================================================================

terraform {
  backend "gcs" {
    bucket = "edu-erp-tfstate" # CHANGE ME or override with -backend-config
    prefix = "terraform/state"
  }
}
