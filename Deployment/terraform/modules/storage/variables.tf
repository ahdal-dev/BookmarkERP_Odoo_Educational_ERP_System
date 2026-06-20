# ============================================================================
# modules/storage/variables.tf
# ============================================================================

variable "project_id" { type = string }
variable "region" { type = string }
variable "name_prefix" { type = string }
variable "labels" {
  type    = map(string)
  default = {}
}

variable "backup_retention_days" {
  description = "Days before backup objects are deleted."
  type        = number
  default     = 30
}

variable "upload_retention_days" {
  description = "Days before OCR upload objects are deleted."
  type        = number
  default     = 7
}
