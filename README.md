# Bookmark Academic ERP Suite

A modern, highly scalable, and decoupled microservices architecture designed to modernize traditional educational management systems. By transitioning away from native Odoo XML dashboards to a headless model, the platform delivers a fast, responsive Single-Page Application (SPA) experience powered by React, orchestrated by a FastAPI Gateway, and backed by the robust core of Odoo 19.0.

---

## 🌟 Core Architecture & Technology Stack

The Bookmark Academic ERP Suite is logically divided into distinct, loosely coupled layers to ensure modularity, scalability, and security.

### 1. Presentation Layer (Frontend)
- **Tech Stack:** React, Vite, React Router, Tailwind CSS, CSS Modules.
- **Role:** Completely replaces the native Odoo XML/UI. It independently handles state, JWT storage, and asynchronous data fetching. 

### 2. API Gateway Layer (Orchestration & Security)
- **Tech Stack:** FastAPI (Python), NGINX.
- **Role:** The single entry point for all client requests. NGINX handles rate limiting and SSL termination. FastAPI provides Role-Based Access Control (RBAC), validates JWTs, orchestrates calls across microservices, and tracks active concurrent users using Redis.

### 3. Core ERP Layer (Backend)
- **Tech Stack:** Headless Odoo 19.0 (Python).
- **Role:** Handles core business logic (Admissions, Petitions, Enrollments, Grades, Waitlists). It exposes custom REST controllers instead of traditional XML views.

### 4. Asynchronous & AI Services Layer
- **Tech Stack:** RabbitMQ, Python Workers, OCR Microservice (Flask).
- **Role:** Handles heavy background tasks without blocking the main event loop. Tasks like processing document OCR, sending bulk notifications, and orchestrating RAG-Chatbot queries are managed securely in the background.

---

## 🎨 System Wireframes & UI

The platform prioritizes a modern, responsive user experience. Below are the primary wireframes representing the current decoupled frontend views:

### Authentication & Login
A secure, JWT-backed authentication flow tailored for various academic roles (Student, Faculty, Advisor, Registrar, Admin).

![Login Screen](docs/Wire_frame/V02/Bookmark_Academic_ERP_Login.jpeg)

### Registrar & Administrative Dashboard
Provides real-time aggregates of concurrent active sessions, enrollment metrics, and waitlist tracking.

![Registrar Dashboard](docs/Wire_frame/V02/Bookmark_Academic_ERP_Dashboard.jpeg)

### Program & Course Catalog
Students and faculty can browse real-time course offerings, prerequisites, and track capacity utilization dynamically.

![Course Catalog](docs/Wire_frame/V02/Bookmark_ERP_Program_Catalog6.jpeg)

### Student Petition Submission
Students can easily submit multi-tiered academic petitions, uploading necessary documents securely to the backend.

![Student Petition Form](docs/Wire_frame/V02/Bookmark_ERP_Student_Petition_Form.jpeg)

### Petition Review & Tracking Queue
Faculty, Chairs, and Registrars manage their specific queues for approving or rejecting academic petitions.

![Petition Tracking](docs/Wire_frame/V02/Bookmark_ERP_Petition_Tracking.jpeg)

### User Management & Institutional Ruleset
Super Administrators can define canonical RBAC roles, edit institutional registration windows, and enforce prerequisites globally.

![User Management](docs/Wire_frame/V02/Bookmark_ERP_User_Management.jpeg)

---

## 🚀 Key System Features

- **Headless Odoo:** Complete removal of standard Odoo XML views in favor of high-performance JSON-RPC endpoints.
- **RabbitMQ Integration:** Background processing for waitlist promotions, registration attempts, and notification dispatching.
- **Dynamic Registration Windows:** Automated enrollment periods based on student seniority (academic tiers) calculated directly from real GPA.
- **Concurrent User Tracking:** Redis tracks active sessions (`uid` and `jti`) for real-time traffic monitoring by the Registrar.
- **Advanced OCR Document Processing:** Automatic extraction of metadata from student ID and transcript uploads via a dedicated microservice.
- **AI-Powered Assistance:** Integration of an Academic Agent (RAG-Chatbot) to support student inquiries natively within the ERP.

---

## 🛠 Deployment & Setup

The entire architecture is containerized using Docker and Docker Compose. 

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local Odoo development)
- Node.js 18+ (for frontend development)

### Quick Start (Full Stack)

1. **Clone the repository.**
2. **Start the API Gateway & Infrastructure:**
   ```bash
   cd api_gateway
   docker-compose up -d --build
   ```
   *(This starts FastAPI, NGINX, RabbitMQ, Redis, Prometheus, Grafana, and the OCR Microservice).*

3. **Start the Headless Odoo Backend (Windows Host):**
   ```bash
   venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf\odoo.conf
   ```

4. **Start the React Frontend:**
   ```bash
   cd bookmark-frontend
   npm install
   npm run dev
   ```

### Access Points
- **React Frontend:** `http://localhost:5173`
- **FastAPI Gateway:** `http://localhost:8000` (Swagger UI: `http://localhost:8000/docs`)
- **Prometheus Metrics:** `http://localhost:9090`
- **Grafana Dashboards:** `http://localhost:3000`

---

## 🧪 Testing

The repository includes extensive automated test coverage, particularly for the API Gateway and core Odoo models:

- `make run` — Runs the full stack.
- `cd api_gateway && ./test_gateway.ps1` — Runs health checks and rate limit testing on the Gateway.
- The `bookmark-frontend` uses Vite's built-in testing suite for unit-testing custom hooks (like `useAsync`).
