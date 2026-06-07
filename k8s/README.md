# Kubernetes Migration Guide - Educational ERP System

## Overview

This directory contains production-ready Kubernetes manifests for migrating your Educational ERP system from Docker to Kubernetes. The architecture consists of microservices running on a Kubernetes cluster with proper service discovery, health checks, and security controls.

## Directory Structure

```
k8s/
├── config/                          # Global configuration and shared resources
│   ├── configmap.yaml               # Global ConfigMap for all services
│   ├── secret.yaml                  # Global Secret with sensitive data
│   ├── postgres-deployment.yaml     # PostgreSQL database deployment
│   ├── postgres-service.yaml        # PostgreSQL service
│   ├── postgres-serviceaccount.yaml # PostgreSQL service account
│   └── postgres-initdb-configmap.yaml
│
├── fastapi/                         # FastAPI Gateway service
│   ├── deployment.yaml              # FastAPI deployment with health probes
│   ├── service.yaml                 # ClusterIP service for internal discovery
│   └── serviceaccount.yaml          # Service account for RBAC
│
├── odoo/                            # Odoo ERP service
│   ├── deployment.yaml              # Odoo deployment with health probes
│   ├── service.yaml                 # ClusterIP service for internal discovery
│   ├── serviceaccount.yaml          # Service account for RBAC
│   └── configmap.yaml               # Odoo-specific configuration
│
├── nginx/                           # NGINX API Gateway
│   ├── deployment.yaml              # NGINX deployment with health probes
│   ├── service.yaml                 # LoadBalancer service for external access
│   ├── serviceaccount.yaml          # Service account for RBAC
│   ├── configmap.yaml               # NGINX configuration
│   └── conf-d-configmap.yaml        # Additional NGINX conf.d configurations
│
├── ocr/                             # OCR Microservice
│   ├── deployment.yaml              # OCR deployment with health probes
│   ├── service.yaml                 # ClusterIP service for internal discovery
│   └── serviceaccount.yaml          # Service account for RBAC
│
└── README.md                        # This file
```

## Microservices Architecture

### Service Communication Flow

```
Internet → NGINX Service (LoadBalancer:80/443)
         ↓
       NGINX Pod (Reverse Proxy)
         ↓
FastAPI Service (ClusterIP:8000)
         ├→ FastAPI Pod(s)
         ├→ Odoo Service (ClusterIP:8069)
         │   └→ Odoo Pod(s)
         │       ↓ (connects to)
         │       PostgreSQL Service (ClusterIP:5432)
         │           └→ PostgreSQL Pod
         │
         └→ OCR Service (ClusterIP:5000)
             └→ OCR Pod(s)
```

## Services Overview

### 1. NGINX API Gateway
- **Type**: LoadBalancer (external access)
- **Replicas**: 2 (high availability)
- **Port**: 80 (HTTP), 443 (HTTPS - configure in production)
- **Role**: Reverse proxy, rate limiting, TLS termination
- **Health Check**: `/health` endpoint

### 2. FastAPI Gateway
- **Type**: ClusterIP (internal service discovery)
- **Replicas**: 2 (high availability)
- **Port**: 8000
- **Role**: Internal API orchestration, microservice routing
- **Health Check**: `/health` endpoint

### 3. Odoo ERP
- **Type**: ClusterIP (internal service discovery)
- **Replicas**: 2 (high availability)
- **Ports**: 8069 (web), 8072 (longpolling)
- **Role**: Core ERP functionality
- **Dependencies**: PostgreSQL database
- **Health Check**: `/health` endpoint

### 4. OCR Microservice
- **Type**: ClusterIP (internal service discovery)
- **Replicas**: 2 (high availability)
- **Port**: 5000
- **Role**: AI-based document processing
- **GPU Support**: Optional (uncomment resource limits)
- **Health Check**: `/health` endpoint

### 5. PostgreSQL Database
- **Type**: ClusterIP (internal service discovery)
- **Replicas**: 1 (consider StatefulSet for production)
- **Port**: 5432
- **Role**: Primary database backend for Odoo
- **Health Check**: `pg_isready` command

## Pre-Deployment Checklist

### 1. Prerequisites
- [ ] Kubernetes cluster running (v1.24+)
- [ ] kubectl CLI configured
- [ ] Docker images built and pushed to registry:
  - [ ] `fastapi-gateway:latest`
  - [ ] `ocr-service:latest`
  - [ ] `nginx:1.25-alpine` (or your custom nginx image)
  - [ ] `odoo:16.0` (or your custom Odoo image)
  - [ ] `postgres:15-alpine`

### 2. Registry Configuration
- [ ] Docker registry credentials configured as ImagePullSecret (if using private registry)
- [ ] Images tagged with version numbers (recommended: use SemVer)

### 3. Certificates & Secrets
- [ ] Generate SSL/TLS certificates:
  ```bash
  # Self-signed (development only)
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout key.pem -out cert.pem
  ```
- [ ] Update `secret.yaml` with:
  - [ ] Strong JWT secret key (min 32 characters)
  - [ ] Secure database credentials
  - [ ] SSL certificates (base64 encoded)

### 4. Network Policies
- [ ] Configure network policies if cluster has them enabled
- [ ] Ensure DNS resolution is working (`CoreDNS` or equivalent)

## Deployment Instructions

### Step 1: Create Namespace (Optional)
```bash
kubectl create namespace edu-erp
kubectl set-context --current --namespace edu-erp
```

### Step 2: Deploy Configuration & Secrets
```bash
# Apply ConfigMaps and Secrets first
kubectl apply -f k8s/config/configmap.yaml
kubectl apply -f k8s/config/secret.yaml
kubectl apply -f k8s/config/postgres-initdb-configmap.yaml
```

### Step 3: Deploy PostgreSQL Database
```bash
# PostgreSQL must be deployed first (Odoo depends on it)
kubectl apply -f k8s/config/postgres-serviceaccount.yaml
kubectl apply -f k8s/config/postgres-service.yaml
kubectl apply -f k8s/config/postgres-deployment.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l component=postgres-db --timeout=300s
```

### Step 4: Deploy Core Microservices
```bash
# Deploy FastAPI Gateway
kubectl apply -f k8s/fastapi/

# Deploy Odoo ERP
kubectl apply -f k8s/odoo/

# Deploy OCR Service
kubectl apply -f k8s/ocr/

# Wait for all services to be ready
kubectl wait --for=condition=ready pod -l app=edu-erp --timeout=600s
```

### Step 5: Deploy NGINX API Gateway (Last)
```bash
# NGINX reverse proxy routes to other services
kubectl apply -f k8s/nginx/

# Verify all pods are running
kubectl get pods -l app=edu-erp
```

### Step 6: Verify Deployment
```bash
# Check all services
kubectl get svc -l app=edu-erp

# Check all deployments
kubectl get deployments -l app=edu-erp

# View NGINX service external IP (LoadBalancer)
kubectl get svc nginx-service
```

## Health Probes Configuration

Each deployment includes both **livenessProbe** and **readinessProbe**:

### Liveness Probe
- **Purpose**: Detects if container has crashed or hung
- **Action**: Kubernetes restarts the pod if it fails
- **Endpoint**: `/health`

### Readiness Probe
- **Purpose**: Detects if service is ready to receive traffic
- **Action**: Removes pod from load balancer if it fails
- **Endpoint**: `/health`

### Probe Configuration by Service
| Service   | Live Delay | Live Period | Ready Delay | Ready Period | Failures |
|-----------|-----------|------------|------------|-------------|----------|
| FastAPI   | 30s       | 10s        | 10s        | 5s          | 2-3      |
| Odoo      | 60s       | 30s        | 30s        | 10s         | 2-3      |
| NGINX     | 15s       | 10s        | 5s         | 5s          | 2-3      |
| OCR       | 45s       | 15s        | 30s        | 10s         | 2-3      |
| PostgreSQL| 30s       | 10s        | 10s        | 5s          | 2-3      |

## Configuration Management

### ConfigMap (Global)
Non-sensitive configuration shared across all services:
- Service URLs (via Kubernetes DNS)
- Feature flags
- Logging levels
- Timezone settings
- Active profiles

**Update**: Edit `k8s/config/configmap.yaml` and:
```bash
kubectl apply -f k8s/config/configmap.yaml
# Pods will need to be restarted to pick up changes:
kubectl rollout restart deployment/fastapi-deployment
```

### Secrets
Sensitive data stored in `edu-erp-secrets`:
- Database credentials
- JWT secret key
- SSL/TLS certificates
- API keys

**Update**: Edit `k8s/config/secret.yaml` and:
```bash
kubectl apply -f k8s/config/secret.yaml
# Pods will need to be restarted:
kubectl rollout restart deployment/fastapi-deployment
```

**Security Note**: Consider using external secret management (e.g., Sealed Secrets, ExternalSecrets, Vault)

## Service Discovery via Kubernetes DNS

Services communicate internally using Kubernetes DNS naming:

```
Service Format: <service-name>.<namespace>.svc.cluster.local
Short Format:  <service-name> (same namespace)

Examples:
- FastAPI → Odoo: http://odoo-service:8069
- FastAPI → OCR:  http://ocr-service:5000
- Odoo → PostgreSQL: host=postgres-service port=5432
```

Update environment variables in `k8s/config/configmap.yaml`:
```yaml
OCR_SERVICE_URL: "http://ocr-service:5000"
ODOO_URL: "http://odoo-service:8069"
```

## Scaling Deployments

### Horizontal Pod Autoscaling (HPA)

Optional: Enable automatic scaling based on CPU/memory:

```bash
# Create HPA for FastAPI (scales between 2 and 5 replicas)
kubectl autoscale deployment fastapi-deployment \
  --min=2 --max=5 --cpu-percent=80

# View HPA status
kubectl get hpa
```

### Manual Scaling

```bash
# Scale FastAPI to 3 replicas
kubectl scale deployment fastapi-deployment --replicas=3

# View current replicas
kubectl get deployment fastapi-deployment
```

## Rolling Updates & Deployments

### Update an Image

```bash
# Update FastAPI image
kubectl set image deployment/fastapi-deployment \
  fastapi=fastapi-gateway:v1.1.0

# Check rollout status
kubectl rollout status deployment/fastapi-deployment
```

### Rollback a Deployment

```bash
# View rollout history
kubectl rollout history deployment/fastapi-deployment

# Rollback to previous version
kubectl rollout undo deployment/fastapi-deployment
```

## Resource Management

Each deployment specifies resource requests and limits:

```yaml
resources:
  requests:
    memory: "256Mi"  # Guaranteed allocation
    cpu: "250m"      # 0.25 CPU core
  limits:
    memory: "512Mi"  # Maximum allowed
    cpu: "500m"      # Maximum allowed
```

### Adjust Resource Limits

Edit the deployment and update resource spec:
```bash
kubectl set resources deployment fastapi-deployment \
  --requests=cpu=300m,memory=256Mi \
  --limits=cpu=600m,memory=512Mi
```

## Persistence & Storage

### Current Setup (Development)
- All deployments use `emptyDir: {}` for volumes
- Data is lost when pods restart
- Suitable for development/testing

### Production Setup (Recommended)
Replace `emptyDir` with `PersistentVolumeClaim`:

```yaml
volumes:
- name: odoo-data
  persistentVolumeClaim:
    claimName: odoo-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: odoo-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd  # Match your storage class
  resources:
    requests:
      storage: 50Gi
```

## Monitoring & Logging

### View Logs

```bash
# View FastAPI logs
kubectl logs -l component=fastapi-gateway

# Tail logs (follow mode)
kubectl logs -f deployment/fastapi-deployment

# View previous pod logs (if crashed)
kubectl logs deployment/fastapi-deployment --previous
```

### Pod Events

```bash
# Describe pod to see events
kubectl describe pod <pod-name>
```

### Metrics

Prometheus metrics available at:
- FastAPI: `:8000/metrics`
- NGINX: `:80/metrics` (if configured)

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app=edu-erp

# Describe failing pod
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
```

### Service Discovery Issues

```bash
# Test DNS resolution inside a pod
kubectl exec -it <pod-name> -- nslookup odoo-service

# Verify service endpoints
kubectl get endpoints
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
kubectl get pod -l component=postgres-db

# Test database connection
kubectl exec -it <fastapi-pod> -- \
  psql postgresql://odoo:password@postgres-service:5432/odoo_db
```

### NGINX Gateway Issues

```bash
# Check NGINX configuration
kubectl exec -it <nginx-pod> -- nginx -T

# Test backend connectivity
kubectl exec -it <nginx-pod> -- \
  curl -v http://fastapi-service:8000/health
```

## Security Best Practices

### 1. Network Policies
Implement network policies to restrict traffic:
```bash
# Example: Only allow FastAPI → PostgreSQL
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: odoo-db-access
spec:
  podSelector:
    matchLabels:
      component: postgres-db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          component: odoo-erp
EOF
```

### 2. RBAC (Role-Based Access Control)
Each service has a dedicated ServiceAccount. Define Roles/RoleBindings as needed.

### 3. Pod Security Standards
- Non-root containers (where possible)
- Read-only root filesystems (for stateless services)
- Drop unnecessary capabilities

### 4. Secrets Management
- Use external secret managers (Sealed Secrets, Vault) in production
- Rotate credentials regularly
- Never commit secrets to version control

### 5. Image Security
- Use specific image versions (not `latest`)
- Scan images for vulnerabilities
- Use private registries for custom images

## Environment Variables Reference

### FastAPI
```
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
OCR_SERVICE_URL=http://ocr-service:5000
ODOO_URL=http://odoo-service:8069
ODOO_DB=edu_demo_new
ODOO_USERNAME=admin
JWT_SECRET_KEY=<your-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Odoo
```
ODOO_DB=edu_demo_new
ODOO_USERNAME=admin
ODOO_PASSWORD=<your-password>
PGHOST=postgres-service
PGPORT=5432
PGUSER=odoo
PGPASSWORD=<db-password>
```

### PostgreSQL
```
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<db-password>
POSTGRES_DB=odoo_db
PGDATA=/var/lib/postgresql/data/pgdata
```

## Next Steps

1. **Build & Push Images**
   ```bash
   docker build -t fastapi-gateway:v1.0.0 ./fastapi_app
   docker build -t ocr-service:v1.0.0 ./services/ocr
   ```

2. **Update Image References**
   - Edit deployment manifests with your registry and image versions
   - Update `imagePullPolicy` based on your needs

3. **Customize Configurations**
   - Update `k8s/config/configmap.yaml` with your specific values
   - Generate and secure credentials in `secret.yaml`

4. **Deploy**
   ```bash
   kubectl apply -f k8s/
   ```

5. **Verify & Test**
   ```bash
   kubectl get pods,svc,deployment -l app=edu-erp
   ```

## Support & Documentation

- Kubernetes Official Docs: https://kubernetes.io/docs/
- Odoo Docker Guide: https://hub.docker.com/_/odoo
- NGINX Kubernetes Guide: https://kubernetes.io/docs/concepts/services-networking/ingress/
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

## License

These manifests are provided as-is for your educational ERP system migration.
