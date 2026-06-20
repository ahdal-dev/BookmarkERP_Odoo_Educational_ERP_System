# ============================================================================
# modules/secrets/variables.tf
# ============================================================================

variable "project_id" { type = string }
variable "region" { type = string }
variable "name_prefix" { type = string }
variable "labels" {
  type    = map(string)
  default = {}
}

variable "secret_values" {
  description = "Map of secret short-name => value. Empty values create the container without a version."
  type        = map(string)
  sensitive   = true
  default     = {}
}

variable "accessor_service_accounts" {
  description = "Service account emails granted secretAccessor on every secret."
  type        = list(string)
  default     = []
}
