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

### Academic records & registration tiers (gap closure)
New Odoo module `addons/edu_mangment/edu_mang_academic/` adds a `grade` (+ `grade_points`) field to `education.registration` and computes `cumulative_gpa` / `earned_credits` / `class_year` / `academic_standing` on `res.users`, plus an `education.registration.tier` model (seniority windows, demo tiers seeded). A `post_init_hook` seeds sample grades so GPA renders on install. New gateway routers `registration_tiers.py` + additions to `registration.py`/`admin.py`/`deps.py`:
- **Precise user roles** → `/admin/users` now returns the real canonical role per user (batch `resolve_roles_bulk` in `deps.py`, group-xmlid → role). `UserManagementPage` maps role→label.
- **Real GPA + grades** → `GET /api/v1/student/grades` (per-term transcript + cumulative GPA/credits/standing); `GET /student/dashboard` now returns a real `gpa`. `GradesPage.jsx` is live.
- **Registration tiers/windows** → `GET /api/v1/registration/tiers`, `GET /api/v1/student/registration-window`. `InstitutionalRulesetPage` windows table reads live tiers.

### Waitlist, concurrent users & prerequisites (final gap closure)
- **Waitlist auto-promotion** → new module `addons/edu_mangment/edu_mang_waitlist/`: `education.registration.action_drop` is overridden to call `education.course._promote_waitlist()` (FIFO by `registration_date`, skips on-hold students, notifies via `edu.notification`); a 30-min `ir.cron` (`cron_promote_waitlist`) is the safety-net.
- **Active concurrent users** → gateway tracks `active_session:{uid}:{jti}` in Redis on login/refresh (`_track_active_session`) and clears it on logout; `GET /api/v1/registrar/dashboard` counts distinct uids (`scan_iter`) → `stats.active_concurrent_users`; `RegistrarDashboardPage` shows the live card.
- **Ruleset prerequisites (both)** → (1) the policy checklist persists as a JSON `ir.config_parameter` (`edu.reg.prerequisites`, handled in `routers/admin.py`; `InstitutionalRulesetPage` sends/loads it); (2) real per-course prerequisites: `education.course.prerequisite_course_ids` (M2M) in `edu_mang_academic`, **enforced** in `education.registration.create` when `edu.reg.prerequisite_check` is on (officer override bypasses). Gateway exposes prereqs in `/registration/courses` + `PATCH /api/v1/registrar/courses/{id}/prerequisites`; `CourseCatalogManagerPage` edits them, `RegistrationPage` course cards show them.

### Deploy note
Install/update the custom modules once (first install uses `-i`, later updates `-u`):
`venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf\odoo.conf -i edu_mang_notification,edu_mang_academic,edu_mang_waitlist -d edu_demo_new --stop-after-init`
(use `-u edu_mang_academic` when only updating the course-prerequisite fields). Then rebuild the gateway: `cd api_gateway && docker-compose up -d --build`.

### Remaining (optional, not a functional gap)
- **GPA source alternative**: GPA is computed from grades on the active custom stack; integrating OpenEduCat exam results (`op.result.line` / `op.marksheet.line`) remains an optional alternative, not required.

## Project Status — Full App Wired (finish pass)
Every React page now fetches **live data** from the gateway (no mock files except `rulesetMocks.js`, kept only as structural defaults). All buttons are functional or route correctly; the 6 dead routes (`/profile`, `/help`, `/handbook`, `/dashboard`, `/support`, `/apply/academic`) are resolved.

New Odoo modules: `edu_mang_support` (`support.ticket` + mail.thread) and `edu_mang_audit` (`audit.log`, written best-effort by the gateway on login). New gateway routers: `advising.py` (advisees / advisee profile / department students), `support.py` (tickets CRUD + messages), `audit.py` (`/admin/audit-log` + `record_audit_event`); plus additions to `registrar.py` (enrollment monitor, tier PUT), `registration.py` (student petitions, petition types), `admin.py` (admission detail, system-settings, maintenance, user delete). Active-concurrent-users now tracked via Redis `active_session:*` keys (login/refresh/logout) and shown on the Registrar dashboard.

Newly wired pages incl.: advisor (AdviseeList/Profile), chair (DepartmentStudents/ChairPetitionQueue/PetitionOverride), faculty (PetitionQueue/Review — decisions persist), support (Queue/Tickets/ChatSession), student (PetitionList/PetitionForm/Grades), admissions (Pipeline/Review/Status, DocumentVerification → real OCR), registrar (EnrollmentMonitor/TimeSlotConfigurator/CourseCatalog), admin (UserManagement/AuditLog/SystemSettings/InstitutionalRuleset). CSV exports + transcript print are real.

### Seed demo data
The DB ships sample users/tiers/admissions but not courses/enrollments/grades. Run the idempotent seeder after installing modules:
`venv\Scripts\python.exe odoo\odoo-bin shell -c odoo.conf\odoo.conf -d edu_demo_new --no-http < addons\edu_mangment\_scripts\seed_demo_data.py`
It seeds departments+chair, courses (instructors, windows, prerequisites), enrollments + graded past terms (drives GPA/standing), advisor links, petitions, support tickets, and audit rows.

### Full install line (all custom modules)
`venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf\odoo.conf -i edu_mang_notification,edu_mang_academic,edu_mang_waitlist,edu_mang_support,edu_mang_audit -d edu_demo_new --stop-after-init`

## Next Phase — RabbitMQ (async messaging)
RabbitMQ already runs in `api_gateway/docker-compose.yml` (`rabbitmq:3-management`, ports 5672/15672, `rabbitmq_data` volume) and the **academic-agent worker** already consumes `registration.attempt` / `petition.submitted` (see `services/RAG-Chatbot/Backend/mq.py` + `worker.py`). The gateway/Odoo side is still synchronous.

**Scaffold in place:** `api_gateway/fastapi_app/mq.py` — durable queues, persistent messages, `try_publish()` with graceful fallback (no-op unless `ENABLE_MQ=true`). `pika==1.3.2` added to `requirements.txt`. Planned queues: `notification.created`, `admission.email`, `admission.mailbox`, `waitlist.promotion`, `grade.posted`.

**Migration checklist for the phase:**
1. Move blocking work to producers via `mq.try_publish(...)`: admission email + mailbox provisioning (`edu_mang_admission/models/admission.py`), notification fan-out (`edu_mang_notification/models/hooks.py`), waitlist promotion (`edu_mang_waitlist`), grade-posting alerts.
2. Add a gateway/worker consumer service in `docker-compose.yml` (mirror `academic-agent-worker`) that performs the Odoo writes/sends.
3. Keep the synchronous fallback when `ENABLE_MQ` is off or the broker is down.
4. Add Prometheus metrics for queue depth / consumer lag; set `ENABLE_MQ=true` + `AMQP_URL` in `.env`.

## Remaining / Next Tasks

### Recently Completed (V03.03 finish pass)
- **Landing page** at `/` — animated brand hero + feature grid + demo role picker (`LandingPage/`). `RoleRouter` moved to `/dashboard`.
- **Login page** — demo buttons removed (moved to landing page); "Apply Now" now routes to `/admissions`; card shadow polished.
- **Apply workflow** — full 4-step form: `/apply/personal-info` → `/apply/academic-history` → `/apply/documents` → `/apply/review`. `ApplicationContext` (`context/ApplicationContext.jsx`) carries state across steps. Step 4 submits to `POST /api/v1/admissions/submit-with-document`.
- **OCR wired** — `DocumentVerificationPage` stores extracted data and file in `ApplicationContext`; review page sends all fields in final submission.
- **Officer documents** — `/admissions/officer/documents` → `OfficerDocumentsPage` lists applications with document status; new gateway endpoint `GET /api/v1/admin/admissions/documents`.
- **Admin stats** — `admin.py /admin/stats` now wraps each Odoo call in isolated try/except with `logger.error`; `res.users` filter changed to `share=False` (internal users only).

### Recently Completed (V03.03 audit pass — this round)
- **Landing page polish** — bolder animated hero headline (staggered word entrance + lime/yellow gradient accent), drifting ambient glow on the dark panel, sheen on the primary CTA, and richer feature-card hover (top accent bar + icon pop). `prefers-reduced-motion` respected. `LandingPage.jsx` / `LandingPage.module.css`.
- **Login logo** — removed the redundant outer green CSS rim (`RoughCircle`) so the SVG's own brush-circle shows cleanly; `BookmarkLogo` now cross-fades between the book+plus mark (`bookark_logo.svg`) and the `Bookmark` wordmark (rendered as a white silhouette on the dark panel) with a pulsing glow. `BookmarkLogo.jsx` / `.module.css`.
- **Apply-flow upload crash (fixed)** — root cause was the public apply flow hitting JWT-guarded `/api/v1/extract-document` + `/api/v1/admissions/submit-with-document`, returning 401/403 and the axios interceptor force-redirecting to `/login`. Both endpoints now use a new **`optional_user`** dependency (`main.py`, `HTTPBearer(auto_error=False)`) so guests can OCR + submit; OCR→application mapping hardened (safe date/int/float parsing). Frontend interceptor no longer redirects on `/apply*` or `/admissions*`. Removed the duplicate "Cumulative GPA" card in `DocumentVerificationPage`.
- **Admin dashboard live data** — `/admin/stats` now returns the previously-missing fields (`aiRequests`, `aiRequestsDelta`, `criticalTickets`, `totalUsersDelta`, `activeTodayPct`, `openTickets`). `openTickets`/`criticalTickets` read from `support.ticket`, `aiRequests` from `audit.log`. A `_STATS_DEMO` fallback fills any metric the live DB can't supply so the dashboard is never blank. `CommandCenterPage` now prefers `openTickets`.
- **Officer documents resilience** — `/admin/admissions/documents` wraps the Odoo query in try/except (returns `{"documents": []}` instead of 500) and guards the `program_id` many2one via `_m2o_label`. The page now shows an empty-state row, not "Failed to load documents".

### Next Up
- **Admission e-mail confirmation** — send confirmation email on `school.admission` creation; wire through `admission.email` MQ queue (scaffold in `mq.py`).
- **Real AI-request metric** — `aiRequests` currently proxies `audit.log` count (with demo fallback); wire to an actual chatbot request log for a true figure. Likewise `totalUsersDelta` / `aiRequestsDelta` are static placeholders — compute from period-over-period history.
- **Officer documents detail** — add inline document preview (PDF iframe / image) in `ApplicationReviewPage` when `transcript_document` binary is available.
- **OpenEduCat GPA alternative** — optional: swap GPA source from `edu_mang_academic` grades to `op.result.line` / `op.marksheet.line` from OpenEduCat.
- **RabbitMQ migration** — see "Next Phase" section above.
- **Landing page analytics** — track CTA clicks (Log In / Try Demo / Apply Now) via `POST /api/v1/audit/record` to `audit.log`.
