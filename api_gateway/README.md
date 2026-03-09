# API Gateway

## Architecture Overview

This API Gateway implements a modern microservices architecture for an Educational ERP system, combining **NGINX** as a reverse proxy with **FastAPI** as an internal gateway and orchestration layer.

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  NGINX (Reverse Proxy & Load Balancer)             │
│  • Rate Limiting (Leaky Bucket)                     │
│  • JWT Token Validation                             │
│  • SSL/TLS Termination                              │
│  • Load Balancing (Round-Robin)                     │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  FastAPI Gateway (Orchestration Layer)              │
│  • Role-Based Access Control (RBAC)                 │
│  • Request Routing                                  │
│  • Service Orchestration                            │
│  • API Documentation                                │
└──────┬──────────────────────┬──────────────┬────────┘
       │                      │              │
       ▼                      ▼              ▼
┌──────────────┐    ┌──────────────┐  ┌──────────────┐
│ OCR Service  │    │    Odoo ERP  │  │    Redis     │
│ (Flask)      │    │ (PostgreSQL) │  │   (Cache)    │
└──────────────┘    └──────────────┘  └──────────────┘
```

## 🚀 Features

### NGINX Layer
- ✅ **Load Balancing**: Round-robin algorithm for distributing traffic
- ✅ **Rate Limiting**: Leaky bucket strategy (configurable per endpoint)
- ✅ **JWT Validation**: Basic token format checking
- ✅ **SSL/TLS**: HTTPS support with configurable certificates
- ✅ **Health Checks**: Service availability monitoring
- ✅ **Security Headers**: XSS, CORS, CSP protection

### FastAPI Gateway
- ✅ **RBAC**: Role-based access control (Prospective Student, Admission Staff, Admin)
- ✅ **Async Operations**: High-performance async/await patterns
- ✅ **Service Orchestration**: Combines multiple microservices in single workflow
- ✅ **OpenAPI Documentation**: Auto-generated API docs (`/docs`, `/redoc`)
- ✅ **Error Handling**: Comprehensive exception handling
- ✅ **Logging**: Structured logging for debugging and monitoring

### API Endpoints

#### 1. Document Extraction (OCR)
```http
POST /api/v1/extract-document
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

# Upload National ID, certificate, or other document
# Returns extracted structured data
```

#### 2. Admission Application
```http
POST /api/v1/admissions/apply
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "full_name": "Ahmed Mohamed",
  "national_id": "12345678901234",
  "email": "ahmed@example.com",
  "phone": "+201234567890",
  "date_of_birth": "2000-01-01",
  "address": "Cairo, Egypt",
  "city": "Cairo",
  "previous_qualification": "High School",
  "graduation_year": 2018,
  "gpa": 3.5,
  "desired_program": "Computer Science"
}
```

#### 3. Orchestrated Workflow (OCR + Application)
```http
POST /api/v1/admissions/submit-with-document
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

# Upload document + metadata
# Automatically extracts data and submits application
```
### User Roles

| Role | Access Level | Permissions |
|------|-------------|-------------|
| `prospective_student` | User | Submit applications, upload documents |
| `admission_staff` | Staff | Review applications, process documents |
| `admin` | Administrator | Full system access |
| `system` | System | Internal service communication |

### Using JWT Token

```bash
# Get token
TOKEN=$(curl -X POST "http://localhost/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "role": "prospective_student"}' \
  | jq -r '.access_token')

# Use token in requests
curl -X POST "https://localhost/api/v1/extract-document" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@national_id.jpg"
```

## Rate Limiting

NGINX implements leaky bucket rate limiting to prevent server overload:

| Endpoint | Rate Limit | Burst |
|----------|-----------|-------|
| `/api/v1/extract-document` | 2 req/s | 5 |
| `/api/v1/admissions/apply` | 5 req/s | 10 |
| `/api/v1/admissions/submit-with-document` | 2 req/s | 3 |
| `/api/*` (general) | 10 req/s | 20 |

### Rate Limit Response
```json
HTTP/1.1 429 Too Many Requests
{
  "error": "Rate limit exceeded. Please try again later.",
  "retry_after": "2"
}
```

## Testing

### Health Check
```bash
curl http://localhost/health
```

### OCR Endpoint
```bash
curl -X POST "https://localhost/api/v1/extract-document" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_document.jpg"
```

### Admission Application
```bash
curl -X POST "https://localhost/api/v1/admissions/apply" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @application_data.json
```

## Monitoring (Under dev..)

### Prometheus Metrics
Access metrics at: http://localhost:9090

Custom metrics available:
- Request count by endpoint
- Response time percentiles
- Error rates
- Service health status

### Grafana Dashboards
Access dashboards at: http://localhost:3000

Default credentials:
- Username: `admin`
- Password: Set in `.env` (GRAFANA_PASSWORD)


### SSL Certificate Setup (Production)

Using Let's Encrypt:

```bash
# Install certbot
apt-get install certbot

# Generate certificates
certbot certonly --standalone -d api.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/api.yourdomain.com/privkey.pem

# Update docker-compose.yml volume mount
```

##  API Documentation under dev..

Interactive API documentation available at:
- **Swagger UI**: https://localhost/docs
- **ReDoc**: https://localhost/redoc
