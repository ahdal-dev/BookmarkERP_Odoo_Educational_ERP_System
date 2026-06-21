# ============================================================================
# modules/compute/main.tf - Service Accounts + 3 GCE VMs + startup scripts
# ============================================================================

# ----------------------------------------------------------------------------
# Per-VM service accounts (least privilege). secretAccessor is granted in the
# secrets module; the app SA additionally gets objectAdmin on the backups
# bucket below for pg_dump uploads.
# ----------------------------------------------------------------------------
resource "google_service_account" "proxy" {
  project      = var.project_id
  account_id   = "${var.name_prefix}-proxy-sa"
  display_name = "EDU ERP Proxy VM SA"
}

resource "google_service_account" "app" {
  project      = var.project_id
  account_id   = "${var.name_prefix}-app-sa"
  display_name = "EDU ERP App VM SA"
}

resource "google_service_account" "ai" {
  project      = var.project_id
  account_id   = "${var.name_prefix}-ai-sa"
  display_name = "EDU ERP AI VM SA"
}

# App VM may read/write database backups in GCS.
resource "google_storage_bucket_iam_member" "app_backups" {
  bucket = var.backups_bucket
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app.email}"
}

# ----------------------------------------------------------------------------
# Static external IP for the proxy (the only public entry point).
# ----------------------------------------------------------------------------
resource "google_compute_address" "proxy" {
  name         = "${var.name_prefix}-proxy-ip"
  project      = var.project_id
  region       = var.region
  address_type = "EXTERNAL"
}

# ----------------------------------------------------------------------------
# Rendered startup scripts
# ----------------------------------------------------------------------------
locals {
  common_tpl_vars = {
    name_prefix = var.name_prefix
    app_ip      = var.app_ip
    ai_ip       = var.ai_ip
    repo_url    = var.repo_url
    repo_branch = var.repo_branch
    auto_deploy = var.auto_deploy
  }

  proxy_startup = templatefile("${path.module}/templates/startup.sh.tpl", merge(local.common_tpl_vars, {
    role         = "proxy"
    compose_file = "docker-compose.proxy.yml"
    enable_swap  = true # 1GB e2-micro
  }))

  app_startup = templatefile("${path.module}/templates/startup.sh.tpl", merge(local.common_tpl_vars, {
    role         = "app"
    compose_file = "docker-compose.app.yml"
    enable_swap  = false
  }))

  ai_startup = templatefile("${path.module}/templates/startup.sh.tpl", merge(local.common_tpl_vars, {
    role         = "ai"
    compose_file = "docker-compose.ai.yml"
    enable_swap  = true # e2-medium has 4GB; small swap headroom for model loads
  }))
}

# ----------------------------------------------------------------------------
# VM 1: Proxy (ALWAYS FREE e2-micro) - public IP, nginx + React SPA
# ----------------------------------------------------------------------------
resource "google_compute_instance" "proxy" {
  name         = "${var.name_prefix}-proxy"
  project      = var.project_id
  zone         = var.zone
  machine_type = var.proxy_machine_type
  tags         = ["${var.name_prefix}-proxy"]
  labels       = var.labels

  boot_disk {
    initialize_params {
      image = var.vm_image
      size  = var.proxy_disk_gb
      type  = var.disk_type
    }
  }

  network_interface {
    subnetwork = var.subnet_self_link
    network_ip = var.proxy_internal_ip
    access_config {
      nat_ip = google_compute_address.proxy.address
    }
  }

  metadata = {
    enable-oslogin     = "TRUE"
    startup-script     = local.proxy_startup
    block-project-ssh-keys = "TRUE"
  }

  service_account {
    email  = google_service_account.proxy.email
    scopes = ["cloud-platform"]
  }

  allow_stopping_for_update = true
}

# ----------------------------------------------------------------------------
# VM 2: App (trial credits e2-standard-2) - NO public IP
# ----------------------------------------------------------------------------
resource "google_compute_instance" "app" {
  count        = var.deploy_app_vm ? 1 : 0
  name         = "${var.name_prefix}-app"
  project      = var.project_id
  zone         = var.zone
  machine_type = var.app_machine_type
  tags         = ["${var.name_prefix}-app"]
  labels       = var.labels

  boot_disk {
    initialize_params {
      image = var.vm_image
      size  = var.app_disk_gb
      type  = var.disk_type
    }
  }

  # No access_config block => no external IP. Egress is via Cloud NAT.
  network_interface {
    subnetwork = var.subnet_self_link
    network_ip = var.app_internal_ip
  }

  metadata = {
    enable-oslogin         = "TRUE"
    startup-script         = local.app_startup
    block-project-ssh-keys = "TRUE"
  }

  service_account {
    email  = google_service_account.app.email
    scopes = ["cloud-platform"]
  }

  allow_stopping_for_update = true
}

# ----------------------------------------------------------------------------
# VM 3: AI (trial credits e2-medium) - NO public IP
# ----------------------------------------------------------------------------
resource "google_compute_instance" "ai" {
  count        = var.deploy_ai_vm ? 1 : 0
  name         = "${var.name_prefix}-ai"
  project      = var.project_id
  zone         = var.zone
  machine_type = var.ai_machine_type
  tags         = ["${var.name_prefix}-ai"]
  labels       = var.labels

  boot_disk {
    initialize_params {
      image = var.vm_image
      size  = var.ai_disk_gb
      type  = var.disk_type
    }
  }

  network_interface {
    subnetwork = var.subnet_self_link
    network_ip = var.ai_internal_ip
  }

  metadata = {
    enable-oslogin         = "TRUE"
    startup-script         = local.ai_startup
    block-project-ssh-keys = "TRUE"
  }

  service_account {
    email  = google_service_account.ai.email
    scopes = ["cloud-platform"]
  }

  allow_stopping_for_update = true
}
