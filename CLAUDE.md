# Bookmark Academic ERP Suite - Project Context

## Project Overview
"Bookmark Academic ERP" is a modern, decoupled educational management system. It replaces a monolithic Odoo frontend with a decoupled microservices architecture, featuring a React frontend, a FastAPI API gateway, and an Odoo backend.

## Tech Stack
- **Frontend**: React, Vite, React Router, Tailwind CSS, CSS Modules. (Located in `bookmark-frontend/`)
- **API Gateway**: FastAPI, NGINX proxy. (Located in `api_gateway/fastapi_app/`)
- **Backend ERP**: Odoo 19.0 (Custom addons in `addons/edu_mangment/` and `addons/open_edu_cat/`)
- **Database**: PostgreSQL (Containerized via Docker)
- **Infrastructure**: Docker Compose (Redis, Prometheus, Grafana, OCR Microservice)

## Coding Conventions & Style Guide
- **React Frontend**: 
  - Use Functional Components and Hooks.
  - Apply Tailwind CSS for utility layouts and CSS Modules (`*.module.css`) for strict component scoping. 
  - Reusable primitive components belong in `src/components/`. 
  - Follow the visual language defined in `src/styles/global.css` and `src/styles/brand.js`.
- **FastAPI Gateway**: 
  - Use asynchronous functions (`async def`) for all endpoints.
  - Proxy requests to Odoo using `httpx.AsyncClient`.
- **Odoo Backend**:
  - Follow standard Odoo ORM conventions.
  - Do not use XML views or controllers for student-facing features; everything is headless and exposed via JSON-RPC.

## Commonly Used Commands
- **Run the full stack**: `make run`
- **Rebuild Gateway Containers**: `cd api_gateway && docker-compose up -d --build`
- **Frontend Dev Server**: `cd bookmark-frontend && npm run dev`
- **Frontend Build**: `cd bookmark-frontend && npm run build`
- **Restart Odoo**: `venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf\odoo.conf`

## Architecture & Ports
- **Odoo Backend**: Runs directly on the Windows host. 
  - **Port**: `8081` (Configured in `odoo.conf\odoo.conf` as `http_port = 8081`).
  - *Note*: Port 8069 is explicitly avoided due to a conflict with a global Windows Odoo service installation.
- **FastAPI Gateway**: `http://localhost:8000` (Proxied via NGINX in docker, configured to talk to Odoo via `http://host.docker.internal:8081`).
- **React Frontend**: `http://localhost:5173` (Proxies `/api` to the FastAPI gateway).
- **PostgreSQL**: `localhost:5432` (Dockerized, used by Odoo on the host).

## Test Credentials
The Odoo database is named `edu_demo_new`. You can log in to the frontend or Odoo backend using:
- **Super Admin**: `admin` / `admin`
- **Test Admin**: `admin@test.com` / `admin123`
- **Test Student**: `student@test.com` / `student123`
- **Test Officer**: `officer@test.com` / `officer123`

## Important Gotchas & Configuration Notes
1. **Odoo Timeouts on Windows**: Odoo's internal thread monitor frequently crashes on Windows during local development. The `odoo.conf\odoo.conf` file has `limit_time_real = 99999` and `limit_time_cpu = 99999` set to prevent random disconnects.
2. **API Gateway Odoo URL**: The FastAPI gateway runs inside Docker but needs to communicate with the Odoo server running on the Windows host. Therefore, `ODOO_URL` in `api_gateway/docker-compose.yml` is set to `http://host.docker.internal:8081`.
3. **Frontend API Proxy**: The React frontend uses Vite's `server.proxy` to forward all `/api` requests to `http://localhost:8000`.
4. **Odoo Virtual Environment**: Odoo is run using the local Python virtual environment (`venv\Scripts\python.exe`).

## Frontend Data-Integration (now wired to live endpoints)
The screens below now fetch **live data** through new FastAPI gateway routers (`api_gateway/fastapi_app/routers/`), using the shared `src/hooks/useAsync.js` hook for loading/error states. New gateway routers: `account.py`, `registrar.py`, `notifications.py`, `registration.py`, `faculty.py`, `admin.py` (all registered in `main.py`).

- **Change Password** → `POST /api/v1/auth/change-password` (verifies current password, writes new). `ChangePasswordPage.jsx`.
- **Registrar Dashboard** → `GET /api/v1/registrar/dashboard` (enrolled/open-seats/open-courses/waitlist, capacity utilization, real per-course registration windows, recent-activity feed). Derived entirely from `education.registration` / `education.course`.
- **Notifications Hub** → new Odoo module `addons/edu_mangment/edu_mang_notification/` (`edu.notification` model + workflow hooks on petition/registration/admission events). Routes: `GET /api/v1/notifications`, `PATCH /:id/read`, `POST /read-all`. The frontend fallback feed was removed.
- **Registration catalog** → `GET /api/v1/registration/courses`. **Student dashboard** → `GET /api/v1/student/dashboard`.
- **Faculty** → `GET /api/v1/faculty/dashboard`, `/faculty/courses`, `/faculty/courses/{id}/roster` (+ existing `/faculty/petitions`).
- **Admissions pipeline** → `GET /api/v1/admin/admissions/pipeline`, `PATCH /admin/admissions/{id}/stage`. **Admin users** → `GET/POST /api/v1/admin/users`. **Registration rules** → `GET/PUT /api/v1/admin/settings/registration-rules` (stored as `ir.config_parameter`). **Admin petitions** → `GET /api/v1/admin/petitions[/{id}]`.

### Deploy note
The notifications module must be installed/updated once:
`venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf\odoo.conf -u edu_mang_notification -d edu_demo_new --stop-after-init`
then rebuild the gateway: `cd api_gateway && docker-compose up -d --build`.

### Remaining genuine gaps (no Odoo model — intentionally not faked)
- **Student GPA**: no GPA model → `student/dashboard` returns `gpa: null` (UI shows "—").
- **Registrar "tiers" / "active concurrent users"**: no model → replaced with real per-course windows and an "Open Courses" metric; concurrent-users card removed.
- **Waitlist auto-promotion**: `education.registration` has a `waitlist` state but no auto-promote logic.
- **User role granularity**: `admin/users` returns a coarse Student/Staff role (portal `share` flag), not the full 9-role mapping.
- **Ruleset windows / prerequisite list** (`InstitutionalRulesetPage`): scalar rules persist via `ir.config_parameter`; the registration-windows table and prerequisite checklist remain UI-local (no model).
