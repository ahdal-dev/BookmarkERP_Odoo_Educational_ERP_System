# Bookmark Academic ERP — Test Checklist

## System Prerequisites

Before running any tests, confirm the stack is up:

| Service | URL | Expected |
|---------|-----|----------|
| Odoo backend | http://localhost:8081/web | Login page loads |
| FastAPI gateway | http://localhost:8000/docs | Swagger UI loads |
| React frontend | http://localhost:5173 | App loads, redirects to `/login` |

---

## Test Credentials

| Role | Login | Password | Post-login landing |
|------|-------|----------|--------------------|
| Super Admin | `admin` | `admin` | `/admin` |
| Test Admin | `admin@test.com` | `admin123` | `/admin` |
| Test Student | `student@test.com` | `student123` | `/student/dashboard` |
| Test Officer | `officer@test.com` | `officer123` | `/admissions/officer` |
| Registrar | *(create in Odoo backend)* | — | `/registrar/dashboard` |
| Instructor | *(create in Odoo backend)* | — | `/faculty/dashboard` |
| Academic Advisor | *(create in Odoo backend)* | — | `/faculty/dashboard` |
| Department Chair | *(create in Odoo backend)* | — | `/faculty/dashboard` |
| Support Tech | *(create in Odoo backend)* | — | `/support/chat-queue` |

---

## 1. Role Login & Landing Page Tests

For each role, log in and verify:

- [ ] **Super Admin** → lands on `/admin` (Command Center dashboard)
- [ ] **Admission Officer** (`officer@test.com`) → lands on `/admissions/officer` (Kanban pipeline)
- [ ] **Student** (`student@test.com`) → lands on `/student/dashboard`
- [ ] **Registrar** → lands on `/registrar/dashboard`
- [ ] **Instructor** → lands on `/faculty/dashboard`
- [ ] **Academic Advisor** → lands on `/faculty/dashboard`
- [ ] **Department Chair** → lands on `/faculty/dashboard`
- [ ] **Support Tech** → lands on `/support/chat-queue`
- [ ] **Prospective Student** → lands on `/admissions/status`

Cross-role guard test:
- [ ] While logged in as Student, manually navigate to `/admin` → should redirect to `/student/dashboard`
- [ ] While logged in as Officer, navigate to `/apps` → should redirect to `/admissions/officer`

---

## 2. Candidate Application Workflow

*Role: unauthenticated / prospective student*

- [ ] Visit http://localhost:5173/admissions — public portal loads with program info
- [ ] Click "Apply" — application form renders with all required fields
- [ ] Submit incomplete form — validation errors appear, form does not submit
- [ ] Fill all fields and upload a document (PDF/image) — OCR endpoint called (`POST /api/v1/extract-document`)
- [ ] Successful submission → confirmation message with reference number displayed
- [ ] Visit `/admissions/status`, enter reference number → status shown (Submitted / Under Review / Accepted / Rejected)
- [ ] Status page shows correct stage badge for the submitted application

---

## 3. Admission Officer Workflow

*Role: admission_officer (officer@test.com / officer123)*

- [ ] Login → lands directly on `/admissions/officer` (Kanban pipeline)
- [ ] Sidebar shows: Dashboard, Documents — no broken links
- [ ] Pipeline loads columns: Submitted, Under Review, Accepted, Rejected with real application cards
- [ ] Click a Kanban card → navigates to `/admissions/officer/application/:id`
- [ ] Application detail page loads: applicant info, OCR-extracted fields, stepper progress
- [ ] Click **Accept** → stage updates to Accepted, stepper reflects change
- [ ] Click **Reject** → stage updates to Rejected
- [ ] Drag a card between columns on pipeline → stage persists after page refresh
- [ ] Navigate to `/apply/documents` → Document Verification page loads

---

## 4. Student Registration Workflow

*Role: student (student@test.com / student123)*

- [ ] Dashboard loads with GPA, credits, upcoming schedule
- [ ] Click "Enrollment" in sidebar → `/registration` opens with live course catalog
- [ ] Courses load from Odoo (not empty); filter by department/level works
- [ ] Click "Enroll" on an open course → enrollment request sent to API
- [ ] Course with 0 seats shows "Waitlist" status
- [ ] Attempt to enroll in a course with unmet prerequisites → error/restriction shown

---

## 5. Petition Submission & Review Workflow

*Full chain: Student → Instructor → Advisor → Chair*

**Student submits:**
- [ ] Login as student → navigate to `/petitions/new`
- [ ] Select petition type (Prerequisite Override / Course Overload / Other)
- [ ] Fill in reason and submit → success confirmation shown
- [ ] Navigate to `/student/petitions` → petition appears with "Pending" status

**Instructor reviews:**
- [ ] Login as instructor → navigate to `/faculty/petitions`
- [ ] Submitted petition appears in queue
- [ ] Click petition → `/faculty/petitions/:id` opens with student details
- [ ] Click **Approve** → status updates; student petition page shows "Instructor Approved"
- [ ] Click **Escalate** → petition moves to advisor/chair queue

**Academic Advisor reviews:**
- [ ] Login as advisor → `/faculty/petitions` shows escalated petition
- [ ] Navigate to `/faculty/advisees` → advisee list loads
- [ ] Click advisee → `/faculty/advisees/:studentId` shows academic record
- [ ] Approve or reject petition with guidance note

**Department Chair overrides:**
- [ ] Login as chair → `/faculty/chair/petitions` shows escalated petitions (Kanban)
- [ ] Click petition → `/faculty/chair/petitions/:id` opens full audit trail
- [ ] Override approval → status updates across all parties

---

## 6. Registrar Configuration Workflow

*Role: registrar*

- [ ] Login → lands on `/registrar/dashboard` with live enrollment stats
- [ ] Sidebar shows: Dashboard, Time Slots, Course Catalog, Enrollment Monitor, Ruleset
- [ ] Navigate to `/registrar/timeslots` → registration tier windows load
- [ ] Edit a tier window → save persists to Odoo
- [ ] Navigate to `/registrar/courses` → course catalog loads with seat counts
- [ ] Edit prerequisites for a course → saves correctly
- [ ] Navigate to `/registrar/enrollment` → per-course seat fill % displayed
- [ ] Navigate to `/admin/settings/registration-rules` (Ruleset) → **must load without redirect** (previously blocked)
- [ ] Toggle "Auto-Enroll" setting → save persists; reload shows same value

---

## 7. Student Affairs Support Workflow

*Role: support_technician*

- [ ] Login → lands on `/support/chat-queue`
- [ ] Live queue loads with active sessions and tickets
- [ ] Click a chat session → `/support/chat/:sessionId` opens conversation
- [ ] Navigate to `/support/tickets` → ticket list loads with status pills
- [ ] Close a ticket → status updates in list

---

## 8. System Administrator Workflow

*Role: super_admin (admin / admin)*

- [ ] Login → lands on `/admin` (Command Center)
- [ ] Admin sidebar shows: Apps, Users, Audit Log, Settings
- [ ] Navigate to `/apps` → Module launcher grid shows 6 custom module tiles
- [ ] Click each tile and verify navigation:
  - Registration → `/registration`
  - Admission → `/admin/admissions`
  - Authentication → `/admin/users`
  - Petition → `/petitions/new`
  - Website → `/admin/settings/registration-rules`
  - Portal Gateway → `/apply/documents`
- [ ] Click FAB "Add Core Odoo Modules" → modal opens
- [ ] Modal loads **live data from Odoo** (not hardcoded list)
- [ ] "Standard Odoo Modules" section shows installable modules with Install buttons
- [ ] "OpenEduCat Platform" section shows openeducat_* modules with Active/Inactive badge
- [ ] Search filters both sections in real-time
- [ ] Click Install on an uninstalled standard module → spinner shows, then "✓ Installed"
- [ ] Navigate to `/admin/users` → user list loads
- [ ] Navigate to `/admin/roles` → roles and permissions page loads
- [ ] Navigate to `/admin/audit-log` → audit entries load

---

## 9. API Health Spot-Checks

Run these against the gateway directly (Swagger at http://localhost:8000/docs or curl):

```bash
# Auth
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin@test.com", "password": "admin123"}'
# Expected: { "access_token": "...", "user": { "role": "super_admin" } }

# Modules list (requires super_admin token)
curl http://localhost:8000/api/v1/admin/modules \
  -H "Authorization: Bearer <token>"
# Expected: array of { name, shortdesc, state, summary }

# Admissions pipeline (requires officer token)
curl http://localhost:8000/api/v1/admin/admissions/pipeline \
  -H "Authorization: Bearer <token>"
# Expected: { columns: [...] }

# Registrar rules (requires registrar or admin token)
curl http://localhost:8000/api/v1/admin/settings/registration-rules \
  -H "Authorization: Bearer <token>"
# Expected: { auto_enroll: bool, prerequisite_check: bool, ... }
```

---

## 10. Known Gaps / Edge Cases

| Gap | Notes |
|-----|-------|
| OCR doc upload | `POST /api/v1/extract-document` must be reachable (OCR microservice in Docker); test with a real PDF |
| Waitlist enqueue | `POST /api/v1/student/waitlist` — verify Odoo `edu_mang_waitlist` module is installed |
| Petition escalation email | Notifications go via Redis queue; confirm `edu_mang_notification` is active in Odoo |
| Prospective student login | No protected routes exist post-login; `/admissions/status` is public — reference-based lookup only |
| Module install time | Installing an Odoo module can take 30–120 s; gateway timeout is set to 120 s |
