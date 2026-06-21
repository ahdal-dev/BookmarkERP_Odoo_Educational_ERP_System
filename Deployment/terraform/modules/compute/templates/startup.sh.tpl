#!/usr/bin/env bash
# ============================================================================
# Unified GCE startup script (rendered per-VM by Terraform templatefile).
# role=${role}  compose=${compose_file}
# Terraform injects: ${name_prefix}, ${app_ip}, ${ai_ip}, ${repo_url},
#                    ${repo_branch}, ${compose_file}, ${role}
# Bash variables are escaped as $${VAR} so Terraform leaves them intact.
# ============================================================================
set -euo pipefail
exec > >(tee -a /var/log/edu-erp-startup.log) 2>&1
echo "[startup] role=${role} $(date -u)"

export DEBIAN_FRONTEND=noninteractive

# --- Optional swap (the 1GB e2-micro proxy benefits from this) --------------
%{ if enable_swap ~}
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
%{ endif ~}

# --- Docker Engine + Compose plugin -----------------------------------------
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

# --- Supporting tools -------------------------------------------------------
apt-get update -y
apt-get install -y git gettext-base jq

mkdir -p /opt/edu-erp

# --- Secret -> .env renderer (uses the VM's attached service account) --------
cat > /usr/local/bin/edu-fetch-secrets.sh <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
PREFIX="${name_prefix}"
get() { gcloud secrets versions access latest --secret="$${PREFIX}-$$1" 2>/dev/null || echo ""; }
umask 077
cat > /opt/edu-erp/.env <<ENV
# Rendered from Secret Manager on $(date -u)
POSTGRES_PASSWORD=$$(get postgres-password)
ODOO_PASSWORD=$$(get odoo-password)
ODOO_MASTER_PASSWORD=$$(get odoo-password)
JWT_SECRET_KEY=$$(get jwt-secret-key)
CHATBOT_SHARED_SECRET=$$(get chatbot-shared-secret)
OPENROUTER_API_KEY=$$(get openrouter-api-key)
OPENROUTER_MODEL=openai/gpt-4o-mini
MISTRAL_API_KEY=$$(get mistral-api-key)
RABBITMQ_USER=$$(get rabbitmq-user)
RABBITMQ_PASSWORD=$$(get rabbitmq-password)
REDIS_PASSWORD=$$(get redis-password)
GRAFANA_PASSWORD=$$(get grafana-password)
APP_SERVER_IP=${app_ip}
AI_SERVER_IP=${ai_ip}
ENV
echo "[secrets] wrote /opt/edu-erp/.env"
EOS
chmod +x /usr/local/bin/edu-fetch-secrets.sh

# --- One-shot deploy helper -------------------------------------------------
cat > /usr/local/bin/edu-deploy.sh <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
REPO_URL="${repo_url}"
REPO_BRANCH="${repo_branch}"
COMPOSE_FILE="${compose_file}"
DIR=/opt/edu-erp/repo
if [ -n "$${REPO_URL}" ]; then
  if [ ! -d "$${DIR}/.git" ]; then
    git clone --branch "$${REPO_BRANCH}" "$${REPO_URL}" "$${DIR}"
  else
    git -C "$${DIR}" fetch --all && git -C "$${DIR}" reset --hard "origin/$${REPO_BRANCH}"
  fi
else
  echo "repo_url not set - copy the repo to $${DIR} manually, then re-run edu-deploy.sh" >&2
  exit 0
fi
/usr/local/bin/edu-fetch-secrets.sh
cp /opt/edu-erp/.env "$${DIR}/Deployment/.env"
cd "$${DIR}/Deployment"
docker compose -f "$${COMPOSE_FILE}" --env-file .env up -d
EOS
chmod +x /usr/local/bin/edu-deploy.sh

# --- Optional auto-deploy ----------------------------------------------------
%{ if auto_deploy && repo_url != "" ~}
/usr/local/bin/edu-deploy.sh || echo "[deploy] auto-deploy failed; run edu-deploy.sh manually"
%{ endif ~}

echo "[startup] done role=${role}"
