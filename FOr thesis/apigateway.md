# Bookmark Academic ERP - API Gateway

## 1. Overview
This API Gateway is the central routing, authentication, and orchestration layer for the Bookmark Academic ERP microservices architecture. It safely proxies requests from the React frontend to the headless Odoo backend and other internal services (such as OCR and AI models). 

The gateway is built using **FastAPI** (Python) for high-performance asynchronous request handling and uses **NGINX** as a reverse proxy for SSL termination, load balancing, and rate limiting.

---

## 2. Architecture & Tech Stack

- **FastAPI:** High-performance ASGI framework used for routing and business logic orchestration.
- **NGINX:** Reverse proxy handling rate limiting (leaky bucket), SSL/TLS, and load balancing.
- **PostgreSQL:** Primary database (via Odoo JSON-RPC proxying).
- **Redis:** Used for caching (e.g., Odoo role resolutions, active session tracking) and token blocklisting.
- **RabbitMQ:** Message broker for asynchronous tasks (e.g., email dispatch, waitlist promotion, notifications).
- **Prometheus & Grafana:** Provides system observability and custom metric tracking.

---

## 3. Core Features

### 🔐 Security & RBAC
- **Token Validation:** Secure JWT validation using `HS256`. Checks for expiration and blocklisting (stored in Redis).
- **Role-Based Access Control (RBAC):** Automatically resolves Odoo user groups into 9 canonical API roles (`prospective_student`, `admission_officer`, `student`, `instructor`, `academic_advisor`, `department_chair`, `registrar`, `support_technician`, `super_admin`).
- **Circuit Breakers:** Built-in circuit breakers prevent cascading failures when the Odoo backend or OCR microservice are down.

### 🚦 Rate Limiting (SlowAPI)
Rate limiting is strictly enforced per IP address:
- **General APIs:** 10 req/s
- **OCR Extractor:** 5 req/min
- **Authentication/Login:** 5 req/min
- Responses return a `429 Too Many Requests` when limits are exceeded.

### 📊 Observability & Auditing
- **Prometheus Metrics:** Tracks `http_requests_total`, `http_request_duration_seconds`, Odoo proxy errors, and auth login attempts.
- **Structured JSON Logging:** Consistent log format including `X-Request-ID` tracing across middlewares.
- **Audit Logger:** Tracks sensitive security events (`/api/v1/auth/`, `/api/v1/admin/`, and all `401/403` errors).

---

## 4. API Modules & Routing

The gateway heavily uses FastAPI routers to organize features logically:

| Router | Purpose |
| :--- | :--- |
| `auth.py` | Login, JWT generation, session tracking, token blocklisting. |
| `account.py` | Self-service account features (e.g., change password). |
| `admin.py` | User management, admissions pipeline, system settings. |
| `advising.py` | Academic advising, advisee profiles, department students. |
| `audit.py` | System-wide audit log retrieval and tracking. |
| `chatbot.py` | Proxies queries to the Academic Agent (RAG-Chatbot). |
| `faculty.py` | Faculty dashboard, course rosters. |
| `notifications.py`| Centralized in-app notifications hub. |
| `petitions.py` | Multi-tier petition workflow routing. |
| `registrar.py` | Registrar dashboard aggregates (capacity, concurrent users). |
| `registration.py` | Course catalog, student enrollment. |
| `registration_tiers.py` | Advanced academic standing and registration tier logic. |
| `support.py` | Support ticket CRUD and messaging. |

---

## 5. Configuration (Environment Variables)

Ensure your `.env` file in the `api_gateway/` folder is configured properly. Critical variables include:

```dotenv
# Odoo Connection
ODOO_URL=http://host.docker.internal:8081
ODOO_DB=edu_demo_new
ODOO_USERNAME=admin
ODOO_PASSWORD=your_secure_password

# JWT Security
JWT_SECRET_KEY=your_secure_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1
JWT_REFRESH_EXPIRATION_DAYS=7

# Infrastructure
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
OCR_SERVICE_URL=http://ocr_microservice:5000
ENABLE_MQ=true
AMQP_URL=amqp://guest:guest@rabbitmq:5672/

# CORS Settings
CORS_ORIGINS=http://localhost:5173
```

*(Note: The Gateway will crash on startup if `JWT_SECRET_KEY` or `ODOO_PASSWORD` are missing).*

---

## 6. Running the API Gateway

### Using Docker Compose (Recommended)
The standard way to run the API Gateway along with its dependencies (Redis, NGINX, RabbitMQ, Prometheus, Grafana) is via Docker Compose:

```bash
# Navigate to the API Gateway directory
cd api_gateway

# Build and start all services in detached mode
docker-compose up -d --build

# View logs for the FastAPI application
docker-compose logs -f fastapi
```

### Local Development (Python Virtual Environment)
If you need to debug the gateway locally without Docker:
```bash
cd api_gateway/fastapi_app
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 7. Testing & API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, navigate to:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Testing the Health Check
You can verify the gateway is up and running via the `/health` endpoint:
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "api_gateway",
  "timestamp": "2026-06-19T00:00:00.000Z",
  "version": "1.0.0"
}
```

---

## 8. Asynchronous Workflows & RabbitMQ
The Gateway initiates background processing to decouple heavy logic from HTTP requests:
1. When endpoints trigger heavy actions (e.g., `petition.submitted`), the Gateway uses `mq.try_publish()` to push an event to RabbitMQ.
2. Background workers (like the Academic Agent or Odoo Listeners) consume the queue, performing data persistence or email generation.
3. If RabbitMQ is unavailable (`ENABLE_MQ=false`), the gateway gracefully falls back to synchronous Odoo XML-RPC calls.
