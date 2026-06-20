# Bookmark Academic ERP — GCP Deployment Guide (Terraform IaC, Free-Tier Optimised)

Infrastructure-as-Code deployment of the decoupled **Bookmark Academic ERP** to
Google Cloud Platform, sized for the **GCP Free Tier** + **$300 free-trial credits**.
The strategy is **Docker Compose on 3 GCE VMs** (not full GKE) to stay well inside
the credit budget.

> All paths in this guide are relative to the repository root unless noted.
> Terraform lives in `Deployment/terraform/`; compose + config live in `Deployment/`.

---

## 1. Deployment Overview

### 3-VM topology

```
                              Internet
                                 │  80 / 443  (+ SSH from your IP only)
                                 ▼
        ┌───────────────────────────────────────────────┐
        │  PROXY VM  ·  e2-micro (1 GB) · ALWAYS FREE      │  external static IP
        │  nginx 1.25  +  React SPA static build           │  10.0.0.10
        └───────────────────────────────────────────────┘
                                 │  VPC internal (10.0.0.0/24)
            ┌────────────────────┴───────────────────────┐
            ▼                                              ▼
 ┌────────────────────────────────┐        ┌────────────────────────────────┐
 │ APP VM · e2-standard-2 (8 GB)   │        │ AI VM · e2-medium (4 GB)        │
 │ NO public IP · 10.0.0.11        │        │ NO public IP · 10.0.0.12        │
 │  • Odoo 19 (+ custom addons)    │◄──────►│  • OCR microservice  :5000      │
 │  • FastAPI gateway     :8000    │  VPC   │  • Grade predictor   :8000      │
 │  • PostgreSQL 15       :5432    │        │  • Student perf.     :5002      │
 │  • Redis 7             :6379    │        │  • Academic agent    :8001      │
 │  • RabbitMQ 3          :5672    │        │  • Agent worker (MQ consumer)   │
 └────────────────────────────────┘        └────────────────────────────────┘
            │                                              │
            └──────────────► Cloud NAT ◄───────────────────┘
                       (outbound to OpenRouter / Mistral / image pulls)
```

- **Proxy VM** is the only machine with a public IP. It serves the SPA and
  reverse-proxies `/api` → gateway and `/web` → Odoo over the VPC.
- **App VM** and **AI VM** have **no public IP**; egress is via **Cloud NAT** and
  admin access is via **IAP SSH tunnelling**.
- Cross-VM service URLs use **static internal IPs** wired by Terraform and
  injected into each VM's `.env`.

### What gets created by Terraform
Custom VPC + subnet, Cloud Router + Cloud NAT, 6 firewall rules, 3 GCE VMs with
3 least-privilege service accounts, a static external IP, 2 GCS buckets
(backups + uploads), 10 Secret Manager secrets, and (optionally) a Cloud DNS
zone + A record.

---

## 2. Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Terraform | >= 1.5 | `terraform -version` |
| gcloud CLI | latest | `gcloud version` |
| Docker + Compose v2 | latest | only needed if you build/test locally |
| Git | any | to clone the repo onto the VMs |
| A GCP project | — | with a **billing account** linked (trial credits count as billing) |

```bash
gcloud auth login
gcloud auth application-default login      # credentials Terraform uses
gcloud config set project YOUR_PROJECT_ID
```

---

## 3. GCP APIs to Enable

```bash
gcloud services enable \
  compute.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  iap.googleapis.com \
  dns.googleapis.com
```

---

## 4. Step-by-Step Deployment Plan

### Phase 1 — Project setup & auth
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
# Enable the APIs from section 3.
```

### Phase 2 — Create the Terraform state bucket (one time)
The state bucket must exist before `terraform init` (it can't be created by the
config that uses it).
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://YOUR_TF_STATE_BUCKET
gsutil versioning set on gs://YOUR_TF_STATE_BUCKET
```
Put the name in `Deployment/terraform/backend.tf` **or** pass it at init time
(below).

### Phase 3 — terraform init / plan / apply
```bash
cd Deployment/terraform

cp terraform.tfvars.example terraform.tfvars   # edit: project_id, ssh_source_ranges, ...

terraform init -backend-config="bucket=YOUR_TF_STATE_BUCKET"

# Full deployment (3 VMs, ~$76/mo on trial credits):
terraform plan  -var-file=environments/trial-credits.tfvars
terraform apply -var-file=environments/trial-credits.tfvars

# OR the $0 always-free footprint (proxy VM only):
# terraform apply -var-file=environments/free-tier.tfvars
```
Note the outputs — especially `proxy_external_ip`, the `ssh_*` commands, and
`backups_bucket`.

### Phase 3b — Populate the secrets
If you left `secret_values` empty (recommended), add versions now:
```bash
P=edu-erp   # = name_prefix
printf '%s' "$(openssl rand -hex 24)"      | gcloud secrets versions add $P-postgres-password    --data-file=-
printf '%s' "$(openssl rand -hex 24)"      | gcloud secrets versions add $P-odoo-password        --data-file=-
printf '%s' "$(openssl rand -hex 32)"      | gcloud secrets versions add $P-jwt-secret-key       --data-file=-
printf '%s' "$(openssl rand -hex 16)"      | gcloud secrets versions add $P-chatbot-shared-secret --data-file=-
printf '%s' "erp"                          | gcloud secrets versions add $P-rabbitmq-user         --data-file=-
printf '%s' "$(openssl rand -hex 16)"      | gcloud secrets versions add $P-rabbitmq-password     --data-file=-
printf '%s' "$(openssl rand -hex 16)"      | gcloud secrets versions add $P-redis-password        --data-file=-
printf '%s' "$(openssl rand -hex 16)"      | gcloud secrets versions add $P-grafana-password      --data-file=-
printf '%s' "sk-or-..."                    | gcloud secrets versions add $P-openrouter-api-key    --data-file=-
printf '%s' "your-mistral-key"             | gcloud secrets versions add $P-mistral-api-key       --data-file=-
```

### Phase 4 — Verify each VM is up and Docker is installed
```bash
# Proxy (has public IP)
gcloud compute ssh edu-erp-proxy --zone us-central1-a
# App / AI (no public IP → IAP tunnel)
gcloud compute ssh edu-erp-app --zone us-central1-a --tunnel-through-iap
gcloud compute ssh edu-erp-ai  --zone us-central1-a --tunnel-through-iap

# On each VM:
sudo tail -n 40 /var/log/edu-erp-startup.log
docker --version && docker compose version
```

### Phase 5 — Get the repo + secrets onto the App VM
On the **App VM**:
```bash
sudo git clone -b main https://github.com/Noureqo1/Odoo_Educational_ERP_System.git /opt/edu-erp/repo
sudo /usr/local/bin/edu-fetch-secrets.sh          # renders /opt/edu-erp/.env from Secret Manager
sudo cp /opt/edu-erp/.env /opt/edu-erp/repo/Deployment/.env
cd /opt/edu-erp/repo/Deployment
```
> `config/odoo.conf` is already in the repo with the correct `addons_path`. The
> addons are mounted from `../addons/edu_mangment` and `../addons/open_edu_cat`.

### Phase 6 — Start the App server
```bash
cd /opt/edu-erp/repo/Deployment
sudo docker compose -f docker-compose.app.yml --env-file .env up -d
sudo docker compose -f docker-compose.app.yml ps
```

### Phase 7 — Install the custom Odoo modules
This creates the `edu_demo_new` database and installs the modules + their
dependencies (OpenEduCat etc. resolve automatically).
```bash
sudo docker exec edu_erp_odoo odoo -d edu_demo_new \
  -i edu_mang_auth,edu_mang_academic,edu_mang_admission,edu_mang_petition,edu_mang_notification,edu_mang_audit,edu_mang_support,edu_mang_waitlist,edu_portal_gateway,custom_registration,custom_chatbot_admin \
  --stop-after-init
sudo docker compose -f docker-compose.app.yml restart odoo
```
Optional — seed demo data (courses, enrollments, grades, petitions):
```bash
sudo docker exec -i edu_erp_odoo odoo shell -d edu_demo_new --no-http \
  < /opt/edu-erp/repo/addons/edu_mangment/_scripts/seed_demo_data.py
```

### Phase 8 — Start the AI services
On the **AI VM**:
```bash
sudo git clone -b main https://github.com/Noureqo1/Odoo_Educational_ERP_System.git /opt/edu-erp/repo
sudo /usr/local/bin/edu-fetch-secrets.sh
sudo cp /opt/edu-erp/.env /opt/edu-erp/repo/Deployment/.env
cd /opt/edu-erp/repo/Deployment
sudo docker compose -f docker-compose.ai.yml --env-file .env up -d --build
```
> Build is heavy (PyTorch for OCR). The e2-medium has a small swapfile from the
> startup script; if a build OOMs, build one service at a time:
> `sudo docker compose -f docker-compose.ai.yml build ocr_microservice`.

### Phase 9 — Build the React frontend and start the proxy
Build the SPA (locally or in CI — **not** on the e2-micro) and copy `dist/` up:
```bash
# On your workstation:
cd bookmark-frontend
npm ci && npm run build         # outputs bookmark-frontend/dist

PROXY_IP=$(cd ../Deployment/terraform && terraform output -raw proxy_external_ip)
# Copy via IAP-aware scp:
gcloud compute scp --recurse dist/* edu-erp-proxy:/tmp/frontend-dist --zone us-central1-a
```
On the **Proxy VM**:
```bash
sudo git clone -b main https://github.com/Noureqo1/Odoo_Educational_ERP_System.git /opt/edu-erp/repo
cd /opt/edu-erp/repo/Deployment
sudo mkdir -p frontend-dist && sudo cp -r /tmp/frontend-dist/* frontend-dist/
# nginx.conf upstreams already point at the App VM internal IP (10.0.0.11).
sudo docker compose -f docker-compose.proxy.yml up -d
```
Visit `http://PROXY_EXTERNAL_IP/`.

### Phase 10 — DNS + TLS (optional) and end-to-end check
- Point an A record at `proxy_external_ip` (or set `enable_dns=true` +
  `dns_domain` and delegate the `name_servers` output to your registrar).
- For TLS: place `fullchain.pem` / `privkey.pem` in `Deployment/nginx/ssl/`,
  uncomment the 443 block in `nginx/nginx.conf`, switch port 80 to a redirect,
  set `CORS_ORIGINS=https://your-domain` in `.env`, and
  `docker compose -f docker-compose.proxy.yml up -d` again.
- Smoke test:
  ```bash
  curl -s http://PROXY_IP/healthz
  curl -s http://PROXY_IP/health        # gateway via proxy
  curl -s http://PROXY_IP/api/v1/...    # an authenticated route
  ```

---

## 5. Custom Odoo Module Deployment

### The custom modules
`addons/edu_mangment/` (installable, each has a `__manifest__.py`):

| Module | Purpose |
|--------|---------|
| `edu_mang_auth` | 9-role RBAC security groups (XML) |
| `edu_mang_academic` | Grade scale, GPA, prerequisites, registration tiers |
| `edu_mang_admission` | Admission pipeline + document verification |
| `edu_mang_petition` | Multi-tier petition workflow |
| `edu_mang_notification` | In-app notification system |
| `edu_mang_audit` | Audit logging |
| `edu_mang_support` | Support ticket system |
| `edu_mang_waitlist` | Waitlist auto-promotion + cron |
| `edu_portal_gateway` | Odoo-side API gateway controllers |
| `custom_registration` | Course-registration workflow overrides |
| `custom_chatbot_admin` | Admin chatbot panel integration |

`addons/open_edu_cat/` provides the OpenEduCat base modules (`openeducat_core`,
`openeducat_admission`, `openeducat_exam`, … — pulled in as dependencies).

> **Note:** `addons/edu_mangment/edu_mang_website` is **controllers-only** (no
> `__manifest__.py`), so it is **not** in the `-i` install list. Add a manifest
> first if you intend to install it.

### How `addons_path` is configured
The custom directories are bind-mounted into the container and listed in
`Deployment/config/odoo.conf`:
```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons/open_edu_cat,/mnt/extra-addons/edu_mangment
```
- `/usr/lib/python3/dist-packages/odoo/addons` — Odoo 19 core (built into the image)
- `/mnt/extra-addons/open_edu_cat` — `../addons/open_edu_cat`
- `/mnt/extra-addons/edu_mangment` — `../addons/edu_mangment`

### Volume mount strategy (docker-compose.app.yml)
```yaml
volumes:
  - ./config/odoo.conf:/etc/odoo/odoo.conf:ro
  - ../addons/edu_mangment:/mnt/extra-addons/edu_mangment:ro
  - ../addons/open_edu_cat:/mnt/extra-addons/open_edu_cat:ro
  - odoo_data:/var/lib/odoo
  - odoo_filestore:/var/lib/odoo/filestore
```

### Install (first deploy)
```bash
docker exec edu_erp_odoo odoo -d edu_demo_new \
  -i edu_mang_auth,edu_mang_academic,edu_mang_admission,edu_mang_petition,edu_mang_notification,edu_mang_audit,edu_mang_support,edu_mang_waitlist,edu_portal_gateway,custom_registration,custom_chatbot_admin \
  --stop-after-init
```

### Update (future deploys — after `git pull`)
```bash
docker exec edu_erp_odoo odoo -d edu_demo_new -u edu_mang_academic --stop-after-init
# or update everything:  -u all
docker compose -f docker-compose.app.yml restart odoo
```

---

## 6. Environment Configuration

| File | Use | VMs | Approx cost |
|------|-----|-----|-------------|
| `environments/free-tier.tfvars` | Validate IaC at $0 | proxy only | **$0.00/mo** |
| `environments/trial-credits.tfvars` | Full stack | proxy + app + ai | **~$76/mo** |

```bash
terraform apply -var-file=environments/free-tier.tfvars      # $0
terraform apply -var-file=environments/trial-credits.tfvars  # full
```
Per-deploy overrides (project id, your SSH IP, secrets, DNS) go in
`terraform.tfvars` (copied from `terraform.tfvars.example`). **Lock
`ssh_source_ranges` to your own IP** — the default `0.0.0.0/0` is for first-run
convenience only.

---

## 7. Cost Estimation (us-central1, on-demand)

| Item | Spec | Monthly |
|------|------|---------|
| Proxy VM | e2-micro (Always-Free) | **$0.00** |
| App VM | e2-standard-2 (2 vCPU/8 GB) | ~$48.92 |
| AI VM | e2-medium (1 vCPU/4 GB) | ~$24.46 |
| Persistent disk | 90 GB pd-standard (10+50+30) | ~$3.60 |
| Static external IP | 1 (in use) | ~$0.00–$2.92 |
| Cloud NAT | 1 gateway + light egress | ~$1–2 |
| GCS buckets | backups + uploads (small) | < $1 |
| Secret Manager | 10 secrets | < $1 |
| **Total** | | **≈ $76–80 / mo** |

→ **~3.7–3.9 months** on the $300 trial. Drop to **$0** by applying
`free-tier.tfvars` (proxy only) or by `terraform destroy` when idle.

**Free-Tier guardrails baked in:** `disk_type = pd-standard` (Balanced/SSD are
NOT free), micro pinned to a free region, total Standard PD kept modest.

---

## 8. Scaling-Up Path (Compose-on-VMs → GKE)

1. **Vertical first:** bump `app_machine_type` to `e2-standard-4` and re-apply.
2. **Managed data:** move PostgreSQL to **Cloud SQL** and Redis to
   **Memorystore**; drop those containers from `docker-compose.app.yml`.
3. **Registry:** push the custom images (gateway, OCR, predictors, agent) to
   **Artifact Registry**.
4. **GKE Autopilot:** the existing `k8s/` manifests are the starting point.
   Autopilot is covered by the **$74.40/mo GKE management credit** for one
   cluster. Port the compose services to Deployments/Services, add an Ingress +
   Managed Certificate, and an HPA.
5. **Stateful AI:** give the OCR/model services a `pd-ssd` PVC and node pool with
   more memory.

---

## 9. Rollback Plan

- **Infra:** Terraform state is versioned in GCS. Roll back code and
  `terraform apply` the previous `*.tfvars`, or `terraform destroy` a bad env.
- **App release (per VM):**
  ```bash
  cd /opt/edu-erp/repo && git checkout <previous-good-sha>
  cd Deployment && docker compose -f docker-compose.app.yml --env-file .env up -d --build
  ```
- **Odoo module migration gone wrong:** restore the DB from the latest GCS
  backup (section 10), then `-u` only the fixed module.
- **Full teardown (stops billing):**
  ```bash
  terraform destroy -var-file=environments/trial-credits.tfvars
  ```
  Buckets with `force_destroy=false` (backups) are retained — delete manually if
  intended.

---

## 10. Maintenance Runbook

**Database backup → GCS** (run on the App VM; the app SA has objectAdmin on the
backups bucket):
```bash
BUCKET=$(cd /opt/edu-erp/repo/Deployment/terraform && terraform output -raw backups_bucket 2>/dev/null || echo YOUR_BACKUPS_BUCKET)
docker exec edu_erp_postgres pg_dump -U odoo edu_demo_new | gzip \
  | gsutil cp - gs://$BUCKET/edu_demo_new-$(date +%F-%H%M).sql.gz
```
Automate with cron (`crontab -e`): `0 2 * * * /opt/edu-erp/backup.sh`.

**Restore:**
```bash
gsutil cp gs://$BUCKET/edu_demo_new-DATE.sql.gz - | gunzip \
  | docker exec -i edu_erp_postgres psql -U odoo -d edu_demo_new
```

**Update Odoo modules:** `docker exec edu_erp_odoo odoo -d edu_demo_new -u <module> --stop-after-init && docker compose -f docker-compose.app.yml restart odoo`

**Rotate a secret:**
```bash
printf '%s' "NEW" | gcloud secrets versions add edu-erp-<name> --data-file=-
sudo /usr/local/bin/edu-fetch-secrets.sh          # re-render .env
sudo cp /opt/edu-erp/.env /opt/edu-erp/repo/Deployment/.env
docker compose -f docker-compose.app.yml --env-file .env up -d
```

**Update container images:** `git pull && docker compose -f <file> --env-file .env up -d --build`

**View logs:** `docker compose -f docker-compose.app.yml logs -f --tail=200 odoo` ·
`docker compose -f docker-compose.ai.yml logs -f academic-agent-worker` ·
startup: `sudo tail -f /var/log/edu-erp-startup.log`.

---

## 11. Security Checklist (post-deploy verification)

- [ ] **No public IPs on App/AI VMs** — `gcloud compute instances list` shows EXTERNAL_IP only for `edu-erp-proxy`.
- [ ] **Firewall verified** — `gcloud compute firewall-rules list`; web only to proxy, SSH from your IP + IAP range only, deny-all present.
- [ ] **`ssh_source_ranges` is your IP/32**, not `0.0.0.0/0`.
- [ ] **Secrets not in env files / git** — values in Secret Manager; `.env`, `terraform.tfvars`, `*.tfstate` are git-ignored.
- [ ] **SSH only via IAP** for App/AI (`--tunnel-through-iap`); OS Login enabled, project SSH keys blocked.
- [ ] **CORS restricted** — `CORS_ORIGINS=https://your-domain` (not `*`) in production.
- [ ] **JWT secret >= 32 chars** (`edu-erp-jwt-secret-key`).
- [ ] **PostgreSQL not exposed** — `5432` is `expose` only (no host port), reachable only inside the App VM's container network.
- [ ] **Redis `requirepass` enabled** — set via `REDIS_PASSWORD`; port not published.
- [ ] **Odoo DB manager disabled** — `list_db = False`, `admin_passwd` changed in `config/odoo.conf`.
- [ ] **RabbitMQ default user replaced** — `RABBITMQ_USER`/`PASSWORD` set; management UI (15672) reachable only over the VPC.
- [ ] **Student-perf image key overridden** — the hardcoded `OPENROUTER_API_KEY` in `services/student_performance_service/dockerfile` is overridden by the compose env from Secret Manager (rotate the leaked key).
- [ ] **TLS enabled** before going live (443 block + HSTS).

---

### File map (created by this IaC)

```
Deployment/
├── CLAUDE.md                      ← this guide
├── .env.example
├── .gitignore
├── docker-compose.proxy.yml
├── docker-compose.app.yml
├── docker-compose.ai.yml
├── config/odoo.conf
├── nginx/nginx.conf
└── terraform/
    ├── versions.tf  backend.tf  main.tf  variables.tf  outputs.tf
    ├── terraform.tfvars.example
    ├── environments/{free-tier,trial-credits}.tfvars
    └── modules/{networking,firewall,compute,storage,secrets,dns}/
        └── compute/templates/startup.sh.tpl
```
