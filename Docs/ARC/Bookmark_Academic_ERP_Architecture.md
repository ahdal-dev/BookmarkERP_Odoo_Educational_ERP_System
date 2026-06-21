# Bookmark Academic ERP Architecture Documentation

## 1. Summary

Bookmark ERP keeps Odoo as the backend engine but replaces everything students and staff see and interact with. Instead of Odoo's XML-rendered views, we built a React frontend that talks to a FastAPI gateway, which routes requests to Odoo or one of the AI microservices. All heavy background work — OCR processing, prerequisite checks, bulk notifications — goes through RabbitMQ so the main request path stays fast. The whole system runs in Docker containers and can scale horizontally with Kubernetes.

## 2. Architecture Overview

The system is split into four main layers, each independently deployable.

![Platform Architecture Diagram](platform_architecture.drawio.png)


### Presentation Layer
*   **Technology Stack:** React, Tailwind CSS, CSS Modules.
*   **What it does:** Replaces Odoo's native XML views entirely. The React app is a single-page application that fetches data from the API gateway over REST. State management is handled client-side, so the UI stays responsive without round-tripping to the server for every interaction.
*   **Authentication:** Uses JWT tokens stored client-side and sent as Authorization headers. Session management lives in the gateway layer — Odoo's own session handling is bypassed.

### API Gateway
*   **Technology Stack:** FastAPI (Python).
*   **What it does:** Single entry point for all requests from the frontend.
*   **Routing and security:** Validates JWT tokens, applies rate limiting (DDoS mitigation), and routes requests to the right backend service. No request reaches Odoo or any microservice without passing through this layer first.

### Core ERP Layer
*   **Technology Stack:** Odoo 19.0 (Python), running without its frontend.
*   **What it does:** Handles all business logic and data storage. Custom modules (`edu_mang_admission`, `edu_mang_petition`, `custom_registration`) expose REST controllers that return JSON instead of rendering Odoo views. This is what lets the React frontend work independently of Odoo's UI.

### Message Broker (RabbitMQ)
*   **Technology Stack:** RabbitMQ.
*   **What it does:** Takes heavy background tasks off the main request path.
*   **Why we added it:** Operations like academic prerequisite calculations, OCR processing for uploaded documents, and bulk notification emails would make the API slow if run synchronously. Instead, the gateway publishes a job to a queue and immediately returns a response to the user. Background workers pick up the job and process it without blocking anything else.

### Data Layer
*   **Technology Stack:** PostgreSQL 15.
*   **What it does:** Stores all ERP data. ACID-compliant. Runs in its own container with a persistent volume so data survives restarts.

## 3. Asynchronous Workflows (RabbitMQ Use Cases)

Two examples of how the async queue is actually used in production.

### Use Case 1: Student Petition Submission
When a student submits an academic petition, multiple things need to happen: routing to the right faculty member, document processing, and email notifications. Running all of this inside a single HTTP request would be too slow.

1.  **UI:** Student submits the petition form in React.
2.  **Gateway:** Validates the JWT, applies rate limits, and forwards the payload.
3.  **Queue:** Instead of processing everything right away, the gateway (or a lightweight Odoo controller) publishes a `petition.submitted` message to RabbitMQ and returns `202 Accepted` to the client immediately.
4.  **Worker:** A background worker reads the message, writes the petition record to PostgreSQL through the `edu_mang_petition` module, evaluates routing rules, and triggers the Notification Service.
5.  **Done:** The student gets an email (or a WebSocket push) once the petition is logged and routed.

### Use Case 2: Registration Capacity Checks
During registration periods, many students hit "Register" at the same time. Without queuing, concurrent database writes can cause race conditions and over-enrollment.

1.  **Concurrent requests:** Many students register simultaneously via the API gateway.
2.  **Queue:** Each `registration.attempt` event goes into a dedicated high-priority RabbitMQ queue.
3.  **Controlled processing:** Background workers process the queue one at a time (or with controlled concurrency). Each worker checks prerequisites and available capacity against the database through the `custom_registration` module.
4.  **Protection:** Queuing the requests means the database sees a controlled write load instead of a spike. No over-enrollment, no locking out other users.
5.  **Result:** The registration outcome is pushed back to the client asynchronously.

## 4. Deployment & DevOps

### Docker
Every service runs in its own container:
*   **React frontend:** Nginx container serving the built static files.
*   **API Gateway:** FastAPI app running via Uvicorn/Gunicorn.
*   **Odoo:** Stateless application containers. Multiple Odoo containers can run in parallel because state lives in PostgreSQL, not in the container.
*   **Infrastructure:** RabbitMQ and PostgreSQL containers with persistent volume mounts to prevent data loss.

### Kubernetes
Kubernetes handles scaling and availability, especially during registration spikes:
*   **Pods:** Each service (Gateway, Odoo, React/Nginx, RabbitMQ workers) runs in isolated pods.
*   **Services:** Internal K8s services handle load balancing between the gateway, RabbitMQ, and Odoo pods.
*   **Ingress:** Routes external HTTPS traffic to the React frontend or the API gateway.
*   **Auto-scaling:** Horizontal Pod Autoscalers (HPA) add API Gateway and Odoo pods automatically when CPU/memory goes up during peak load.
