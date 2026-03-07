# Educational ERP API Gateway

## 🏗️ Architecture Overview

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

## 📦 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- Git
- 4GB+ RAM for all services

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd api_gateway
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

3. **Generate SSL certificates** (for development)
```bash
mkdir -p nginx/ssl
cd nginx/ssl

# Generate self-signed certificate (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/C=EG/ST=Cairo/L=Cairo/O=EduERP/CN=localhost"
```

4. **Start all services**
```bash
docker-compose up -d
```

5. **Check service status**
```bash
docker-compose ps
```

6. **View logs**
```bash
docker-compose logs -f fastapi_gateway
```

### Service URLs

- **API Gateway (NGINX)**: https://localhost
- **FastAPI Documentation**: http://localhost/docs
- **Odoo ERP**: http://localhost:8069 (internal)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

## 🔐 Authentication & Authorization

### Generate Test JWT Token

```bash
curl -X POST "http://localhost/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "role": "prospective_student"
  }'
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

## 📊 Rate Limiting

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

## 🔧 Configuration

### Scaling FastAPI Gateway

Scale horizontally for high traffic:

```bash
docker-compose up -d --scale fastapi_gateway=3
```

NGINX will automatically load balance across all instances.

### Environment Variables

Key configuration in `.env`:

```env
# Service URLs
OCR_SERVICE_URL=http://ocr_microservice:5000
ODOO_URL=http://odoo:8069

# JWT Security
JWT_SECRET_KEY=your-very-secure-secret-key
JWT_EXPIRATION_HOURS=24

# Database
POSTGRES_PASSWORD=secure-password
ODOO_PASSWORD=secure-password
```

## 🧪 Testing

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

## 📈 Monitoring

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

## 🛡️ Security Best Practices

### Production Deployment Checklist

- [ ] Replace self-signed certificates with valid SSL certificates (Let's Encrypt)
- [ ] Update `JWT_SECRET_KEY` with cryptographically secure random string
- [ ] Change all default passwords
- [ ] Configure firewall rules
- [ ] Enable HTTPS redirect in NGINX
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Enable monitoring alerts
- [ ] Review and restrict CORS origins
- [ ] Implement API key management
- [ ] Set up intrusion detection
- [ ] Configure DDoS protection

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

## 📝 API Documentation

Interactive API documentation available at:
- **Swagger UI**: https://localhost/docs
- **ReDoc**: https://localhost/redoc

## 🐛 Troubleshooting

### Service not starting

Check logs:
```bash
docker-compose logs <service_name>
```

### Connection refused errors

Verify network connectivity:
```bash
docker network ls
docker network inspect api_gateway_backend
```

### Rate limit issues

Adjust limits in `nginx/nginx.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### OCR service timeout

Increase timeout in FastAPI (`main.py`):
```python
async with httpx.AsyncClient(timeout=120.0) as client:
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [NGINX Documentation](https://nginx.org/en/docs/)
- [Odoo Documentation](https://www.odoo.com/documentation/)
- [Docker Compose Guide](https://docs.docker.com/compose/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Support

For support and questions:
- Email: support@edu-erp.local
- Issues: GitHub Issues
- Documentation: `/docs` endpoint

---

**Built with ❤️ for Educational Excellence**
