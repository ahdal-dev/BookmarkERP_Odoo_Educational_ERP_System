# ============================================================================
# modules/dns/variables.tf
# ============================================================================

variable "enable_dns" {
  type    = bool
  default = false
}
variable "project_id" { type = string }
variable "dns_zone_name" {
  type    = string
  default = "edu-erp-zone"
}
variable "dns_domain" {
  description = "FQDN with trailing dot, e.g. erp.example.com."
  type        = string
  default     = ""
}
variable "proxy_ip" {
  description = "Proxy external IP the A record points to."
  type        = string
}
