# Bookmark Academic ERP Suite - Architecture & Design Decisions

## 1. Executive Summary
The Bookmark Academic ERP is a modern, decoupled educational management system designed to replace the traditional, monolithic Odoo frontend with a highly scalable microservices architecture. By transitioning to a headless ERP model, the platform leverages a React-based frontend for a responsive user experience, a FastAPI API Gateway for centralized routing and security, and an Odoo backend for robust core business logic. The architecture is containerized using Docker and orchestrated with Kubernetes, ensuring high availability and seamless scalability during peak academic cycles (e.g., course registration periods). Furthermore, asynchronous processing is handled via RabbitMQ to decouple heavy tasks from the synchronous request-response cycle.

## 2. High-Level Architecture Overview

The system is logically divided into several decoupled layers, ensuring modularity, independent scalability, and a distinct separation of concerns.

### 2.1. Presentation Layer (Frontend)
*   **Technology Stack:** React, Vite, React Router, Tailwind CSS, CSS Modules.
*   **Location:** `bookmark-frontend/`
*   **Design Decision:** A Single-Page Application (SPA) was chosen over native Odoo UI/XML views to provide a dynamic, responsive, and optimized user experience. 
*   **State & Authentication:** The frontend manages its own state independently of the backend. It implements token-based authentication (JWT), storing secure tokens client-side and passing them via authorization headers. This completely decouples session management from Odoo's monolithic session handling.
*   **API Integration:** The React frontend uses Vite's `server.proxy` during development to forward all `/api` requests to the FastAPI Gateway. All data fetches are performed asynchronously via a custom `useAsync` hook connected to live gateway endpoints.

### 2.2. API Gateway Layer
*   **Technology Stack:** FastAPI (Python), NGINX.
*   **Location:** `api_gateway/fastapi_app/`
*   **Design Decision:** FastAPI was selected due to its high performance (ASGI), native asynchronous capabilities, and automatic OpenAPI documentation generation. 
*   **Functionality:** 
    *   **Single Entry Point:** It acts as the central router for all client requests, exposing RESTful APIs under `/api/v1/`.
    *   **Security Perimeter:** Manages JWT validation, authentication, and rate limiting to mitigate DDoS attacks *before* requests reach the core ERP.
    *   **Proxy to Backend:** Uses asynchronous HTTP clients (`httpx.AsyncClient`) to proxy validated requests to the Odoo backend via JSON-RPC.
    *   **Session Tracking:** Tracks active concurrent users using Redis (`active_session:{uid}:{jti}`).

### 2.3. Core ERP Layer (Backend)
*   **Technology Stack:** Headless Odoo 19.0 (Python).
*   **Location:** `addons/edu_mangment/` and `addons/open_edu_cat/`
*   **Design Decision:** Odoo serves as the primary business logic engine and system of record due to its robust ORM and extensive enterprise features. However, traditional XML views are strictly avoided for student-facing features.
*   **Custom Modules:** Business logic for admissions (`edu_mang_admission`), petitions (`edu_mang_petition`), waitlists (`edu_mang_waitlist`), and registration (`custom_registration`, `edu_mang_academic`) are encapsulated in custom addons. These expose headless REST/JSON APIs via custom controllers to interface seamlessly with the API Gateway.

### 2.4. Message Broker (Asynchronous Layer)
*   **Technology Stack:** RabbitMQ.
*   **Location:** Configured via `api_gateway/docker-compose.yml` and utilized in workers (e.g., `services/RAG-Chatbot/Backend/mq.py`).
*   **Design Decision:** To prevent database locking and UI freezes during heavy operations (like peak course registration or complex petition routing), a message broker is introduced to decouple these tasks from the synchronous HTTP cycle.
*   **Use Cases:** 
    *   **Registration Capacity Checks:** "Register" attempts are published as `registration.attempt` events to a high-priority queue. Background workers consume these sequentially to perform prerequisite checks and capacity validations, ensuring transactional integrity without locking out other users.
    *   **Petitions & Notifications:** Submission of petitions (`petition.submitted`) and dispatching of bulk notifications/emails are offloaded to asynchronous workers.

### 2.5. AI & Chatbot Integration
*   **Technology Stack:** RAG-based Chatbot, Academic Agent Worker.
*   **Location:** `services/RAG-Chatbot/`
*   **Design Decision:** An Academic Agent worker integrates directly with the RabbitMQ message broker to consume and process specific asynchronous events. The chatbot is designed to provide intelligent assistance to students and faculty, drawing context from the core ERP via the API Gateway.

### 2.6. Data Layer
*   **Technology Stack:** PostgreSQL (Relational), Redis (Caching/Sessions).
*   **Design Decision:** PostgreSQL provides robust, ACID-compliant data storage for Odoo. Redis is utilized by the API Gateway for rapid session tracking and rate limiting.

## 3. Infrastructure & Deployment Strategy

The deployment infrastructure is designed for fault tolerance, dynamic scaling, and environmental consistency.

*   **Containerization (Docker):** The entire platform is containerized using Docker and Docker Compose. 
    *   The React frontend is served via an NGINX container optimized for static files.
    *   The API Gateway runs as a containerized FastAPI app via Uvicorn/Gunicorn.
    *   RabbitMQ, Redis, and an OCR Microservice run alongside in the Docker network.
*   **Orchestration (Kubernetes):** For production, Kubernetes (K8s) is utilized to ensure high availability.
    *   **Isolation:** Microservices run in isolated Pods.
    *   **Networking:** Internal K8s Services enable stable load balancing.
    *   **Auto-scaling:** Horizontal Pod Autoscalers (HPA) dynamically spin up additional Gateway and Odoo pods based on CPU/Memory metrics during traffic spikes (e.g., university registration periods).

## 4. Key Technical Decisions & Gotchas

1.  **Headless Odoo Paradigm:** The most significant architectural shift was the abandonment of Odoo's native templating engine in favor of a strictly headless approach. This forces a clean separation of concerns, where Odoo only handles data persistence and business rules, while the React frontend dictates user experience.
2.  **Odoo Timeouts on Windows (Local Dev):** During local development on Windows, Odoo's internal thread monitor frequently crashes. To mitigate this, `limit_time_real = 99999` and `limit_time_cpu = 99999` are set in `odoo.conf` to prevent random disconnects.
3.  **Port Management:** Odoo runs on port `8081` directly on the host (avoiding `8069` due to conflicts). The API Gateway in Docker communicates with it via `http://host.docker.internal:8081`. The frontend proxies to the Gateway at `http://localhost:8000`.
4.  **Waitlist Auto-Promotion:** A custom module (`edu_mang_waitlist`) overrides course drop actions to trigger a FIFO waitlist promotion, supported by a 30-minute fallback cron job (`ir.cron`), ensuring classes remain at optimal capacity without manual intervention.

## 5. Conclusion
The Bookmark Academic ERP architecture provides a robust, future-proof foundation. By decoupling the frontend from the monolithic backend and introducing a high-performance API Gateway and asynchronous message broker, the system achieves the scalability required for modern educational institutions, while allowing independent iterative development of the UI, API, and core ERP layers.
