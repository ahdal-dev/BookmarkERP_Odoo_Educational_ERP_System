# Bookmark Academic ERP — Role-Based Access Control (RBAC) Matrix

> **Architecture Note:** This document reflects the **decoupled React + FastAPI + Odoo** architecture. "Access" is enforced at two independent layers:
> 1. **React Router Layer** — `RoleProtectedRoute` (to be built, see `Roles.md`) reads `user.role` from `AuthContext` and blocks navigation to any route not in a role's allowed list, redirecting to `/unauthorized`.
> 2. **API Gateway Layer** — The FastAPI gateway validates the JWT on every request and checks the role claim against an endpoint permission map. If a request arrives for a disallowed endpoint — even from a modified frontend — the gateway returns `HTTP 403 Forbidden`. The Odoo backend itself is **never directly reachable** from the browser.
>
> **Security guarantee:** Both layers must be independently satisfied. Bypassing the React router (e.g., typing `/admin/users` directly into the browser as a Student) is caught at the gateway. Bypassing the gateway is not possible from the browser because Odoo's port `8081` is not exposed externally.

This document establishes the RBAC framework that protects student data and ensures every user sees only what they are authorized to view.

---

## 1. Prospective Student (Guest / Candidate)

* **Frontend View Access:**
  * `/admissions` — Public Admission Portal (read-only program listing)
  * `/admissions/apply` — Online Application Form (submit only)
  * `/admissions/track` — Application Status Tracker (reference-number lookup only)
  * ❌ All routes under `/student/*`, `/admin/*`, `/admissions/officer/*`, and any authenticated path are **blocked at the router** (unauthenticated user) and **rejected at the gateway** (no valid JWT).

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET` | `/api/admissions/programs` | ✅ Public |
  | `POST` | `/api/admissions/apply` | ✅ Public (rate-limited) |
  | `GET` | `/api/admissions/track/:reference` | ✅ Public (read own status only) |

* **What they can manipulate:** Can create a new application and read their own application status by reference number only.
* **Security boundary:** No JWT is issued. Any attempt to call an authenticated endpoint returns `HTTP 401 Unauthorized`.

---

## 2. Student

* **Frontend View Access:**
  * `/student` — Student Portal Home
  * `/student/courses` — Course Catalog & Cart
  * `/student/registration` — Course Registration
  * `/student/grades` — Grades & Transcript (read-only)
  * `/student/petitions` — Petition Status List
  * `/student/petitions/new` — Petition Submission Form
  * ❌ Routes under `/admissions/officer/*`, `/instructor/*`, `/advisor/*`, `/chair/*`, `/registrar/*`, `/support/*`, `/admin/*` are **blocked at the router** and **rejected at the gateway** with `HTTP 403 Forbidden`.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET` | `/api/student/profile` | ✅ Own record only |
  | `GET` | `/api/student/grades` | ✅ Own grades only |
  | `GET` | `/api/student/courses` | ✅ Read full catalog |
  | `POST` | `/api/student/cart` | ✅ Own cart only |
  | `DELETE` | `/api/student/cart/:courseId` | ✅ Own cart only |
  | `POST` | `/api/student/registration` | ✅ Own registration, time-slot enforced |
  | `DELETE` | `/api/student/registration/:courseId` | ✅ Own drop, within add/drop window only |
  | `GET` | `/api/student/petitions` | ✅ Own petitions only |
  | `POST` | `/api/student/petitions` | ✅ Create own petition only |
  | `GET` | `/api/student/petitions/:id` | ✅ Own petition only (gateway validates ownership) |

* **What they can manipulate:** Strictly limited to their own personal academic data. The gateway enforces record-level ownership — a student cannot read or modify another student's record even if they construct a valid API call with a different student ID.
* **Security boundary:** `user_id` is extracted from the JWT server-side; client-supplied user IDs in request bodies are ignored and overridden by the gateway.

---

## 3. Admission Officer

* **Frontend View Access:**
  * `/admissions/officer` — Application Pipeline Dashboard
  * `/admissions/officer/application/:id` — Application Detail & Review View
  * ❌ Routes under `/student/*`, `/registrar/*`, `/admin/*`, and all other staff portals are **blocked at the router** and **rejected at the gateway** with `HTTP 403 Forbidden`.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET` | `/api/admissions/applications` | ✅ All applications |
  | `GET` | `/api/admissions/applications/:id` | ✅ Any application |
  | `GET` | `/api/admissions/applications/:id/documents` | ✅ Download documents |
  | `PATCH` | `/api/admissions/applications/:id/status` | ✅ Update status (Accept/Reject/Review) |
  | `GET` | `/api/admissions/ocr/:id` | ✅ Read OCR-extracted data |

* **What they can manipulate:** Can read all applications and move them through the admission pipeline. Cannot modify academic transcripts, registration configurations, or student grade records.
* **Security boundary:** Admission Officer's JWT role claim (`admission_officer`) grants no access to `/api/student/*`, `/api/registrar/*`, or `/api/admin/*` endpoints.

---

## 4. Instructor (Teacher / Professor)

* **Frontend View Access:**
  * `/instructor` — Instructor Dashboard
  * `/instructor/courses/:courseId` — Class Roster (scoped to own courses)
  * `/instructor/petitions` — Petition Review Queue (scoped to own courses)
  * `/instructor/petitions/:id` — Petition Detail & Decision View
  * ❌ Routes under `/student/*`, `/admissions/officer/*`, `/registrar/*`, `/admin/*` are **blocked at the router** and **rejected at the gateway** with `HTTP 403 Forbidden`.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET` | `/api/instructor/courses` | ✅ Own assigned courses only |
  | `GET` | `/api/instructor/courses/:courseId/students` | ✅ Roster for own courses only |
  | `GET` | `/api/instructor/petitions` | ✅ Petitions for own courses only |
  | `GET` | `/api/petitions/:id` | ✅ If petition is for an own course (gateway validates) |
  | `PATCH` | `/api/petitions/:id/decision` | ✅ If petition is for an own course (gateway validates) |

* **What they can manipulate:** Can approve or reject petitions only for courses they are the instructor of record for. The gateway checks course ownership server-side on every petition `PATCH`.
* **Security boundary:** Instructors cannot access petitions for courses they do not teach, cannot alter enrollment figures globally, and cannot view student records outside their roster.

---

## 5. Academic Advisor

* **Frontend View Access:**
  * `/advisor` — Advisor Dashboard
  * `/advisor/advisees` — Advisee List
  * `/advisor/advisees/:studentId` — Advisee Academic Profile (read-only)
  * `/advisor/petitions` — Advisor Petition Queue
  * `/instructor/petitions/:id` — Petition Detail & Decision View (shared component, advisor scope)
  * ❌ Routes under `/student/*`, `/admissions/officer/*`, `/registrar/*`, `/admin/*` are **blocked at the router** and **rejected at the gateway** with `HTTP 403 Forbidden`.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET` | `/api/advisor/advisees` | ✅ Own advisee cohort only |
  | `GET` | `/api/advisor/advisees/:studentId` | ✅ Own advisees only (gateway validates cohort membership) |
  | `GET` | `/api/advisor/petitions` | ✅ Petitions routed to this advisor only |
  | `GET` | `/api/petitions/:id` | ✅ If petition is routed to this advisor |
  | `PATCH` | `/api/petitions/:id/decision` | ✅ If petition is routed to this advisor |

* **What they can manipulate:** Read-only access to advisee academic records. Can approve or reject petitions routed to them. Cannot view records for students outside their assigned cohort.
* **Security boundary:** Cannot override a Department Chair's decision. The gateway rejects `PATCH /api/petitions/:id/override` for the `academic_advisor` role claim.

---

## 6. Department Chair

* **Frontend View Access:**
  * `/chair` — Department Chair Dashboard
  * `/chair/petitions` — Department Petition Escalation View (includes all prior decisions)
  * `/chair/students` — Department-wide Student Records (read-only)
  * ❌ Routes under `/student/*`, `/admissions/officer/*`, `/registrar/*`, `/admin/*` are **blocked at the router** and **rejected at the gateway** with `HTTP 403 Forbidden`.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET` | `/api/chair/petitions` | ✅ All petitions within own department |
  | `GET` | `/api/petitions/:id` | ✅ Any petition in own department |
  | `PATCH` | `/api/petitions/:id/decision` | ✅ Any petition in own department |
  | `PATCH` | `/api/petitions/:id/override` | ✅ **Exclusive to this role and above** — overrides prior instructor/advisor ruling |
  | `GET` | `/api/chair/students` | ✅ All students enrolled in department courses (read-only) |

* **What they can manipulate:** Full petition authority within their department, including final override. Can read (but not modify) any student record in their department.
* **Security boundary:** Cannot configure global IT security, manage admission pipelines, or access records for students or petitions outside their department. The gateway scopes all queries to `department_id` extracted from the chair's JWT claims.

---

## 7. Registrar

* **Frontend View Access:**
  * `/registrar` — Registrar Dashboard
  * `/registrar/timeslots` — Registration Time Slot Configurator
  * `/registrar/courses` — Course Catalog Manager (full CRUD)
  * `/registrar/enrollment` — Enrollment Status Monitor
  * ❌ Routes under `/student/*`, `/admissions/officer/*`, `/instructor/*`, `/advisor/*`, `/chair/*`, `/admin/*` are **blocked at the router** and **rejected at the gateway** with `HTTP 403 Forbidden`.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET/POST/PATCH/DELETE` | `/api/registrar/courses` | ✅ Full CRUD on course catalog |
  | `GET/POST/PATCH/DELETE` | `/api/registrar/timeslots` | ✅ Full CRUD on registration windows |
  | `GET` | `/api/registrar/enrollment/status` | ✅ Read global enrollment state |
  | `PATCH` | `/api/registrar/enrollment/:studentId` | ✅ Update student enrollment status |

* **What they can manipulate:** Full structural control over the course catalog and registration configuration. Can update any student's enrollment status (active, withdrawn, on-hold).
* **Security boundary:** Does not hold backend IT security rights. Cannot assign user roles or change passwords (`/api/admin/*` endpoints return `HTTP 403`). Cannot approve or reject academic petitions.

---

## 8. Support Technician (Student Affairs)

* **Frontend View Access:**
  * `/support` — Support Chat Dashboard
  * `StudentQuickLookupDrawer` (side drawer within the support dashboard, no dedicated URL)
  * ❌ Routes under `/student/*`, `/admissions/officer/*`, `/instructor/*`, `/advisor/*`, `/chair/*`, `/registrar/*`, `/admin/*` are **blocked at the router** and **rejected at the gateway** with `HTTP 403 Forbidden`.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `GET` | `/api/support/students/:studentId` | ✅ Read basic profile & registration status (no grades, no transcripts) |
  | `POST` | `/api/support/tickets` | ✅ Create support tickets |
  | `PATCH` | `/api/support/tickets/:id` | ✅ Update own support tickets |
  | `GET` | `/api/support/tickets` | ✅ Read own ticket queue |

* **What they can manipulate:** Can read a student's basic profile and current registration status to provide live support. Can create and update support tickets.
* **Security boundary:** Strictly read-only on all academic data. The gateway explicitly denies `GET /api/student/grades` and all petition/enrollment-mutation endpoints for the `support_technician` role. Cannot approve petitions, change grades, accept applications, or alter registration rules.

---

## 9. System Administrator (Super Admin)

* **Frontend View Access:**
  * `/admin/apps` — App Launcher (the only role that lands here)
  * `/admin/users` — User Role Manager
  * `/admin/admissions/rules` — Admission Rules Configurator
  * `/admin/audit-log` — Security Audit Log Viewer
  * `/admin/settings` — Global System Settings
  * ✅ The Super Admin role is the only role whose `RoleProtectedRoute` grants access to **all routes** across the application for inspection/debugging purposes.

* **API Permissions (FastAPI Gateway):**

  | Method | Endpoint | Permission |
  |---|---|---|
  | `*` | `/api/admin/*` | ✅ Full access |
  | `GET/PATCH` | `/api/admin/users` | ✅ Create, read, update, delete user accounts and role assignments |
  | `GET/POST/PATCH/DELETE` | `/api/admin/admissions/rules` | ✅ Configure per-program admission rules (GPA floors, document types) |
  | `GET` | `/api/admin/audit-log` | ✅ Read all authentication and system events |
  | `GET/PATCH` | `/api/admin/settings` | ✅ Read and update global system configuration |

* **What they can manipulate:** Full CRUD across all modules and all users. The only role that can assign or revoke another user's role claim.
* **Security boundary:** All admin actions are written to an immutable audit log (`/api/admin/audit-log`). The audit log endpoint itself is **read-only even for the Super Admin** — entries cannot be deleted or altered. This ensures compliance and forensic integrity.

---

## Cross-Cutting Security Rules

These rules apply globally across all roles and are enforced independently at both the React router layer and the FastAPI gateway layer.

1. **Route Scope Violation:** If a user navigates to any route not in their allowed list (via URL bar manipulation), `RoleProtectedRoute` redirects them to `/unauthorized`. The gateway simultaneously rejects the API call with `HTTP 403 Forbidden`.

2. **JWT Expiry:** All protected endpoints require a valid, non-expired JWT. Expired tokens return `HTTP 401 Unauthorized`, and the React `AuthContext` intercepts this response globally, clears `localStorage`, dispatches `LOGOUT`, and redirects the user to `/login`.

3. **Odoo Isolation:** The Odoo backend (port `8081`) is never exposed to the browser. All traffic flows through the FastAPI gateway (`localhost:8000`). A user cannot bypass the gateway permission model by hitting Odoo's JSON-RPC directly from the browser.

4. **Record-Level Ownership:** For student-scoped endpoints, the gateway extracts `user_id` from the JWT and ignores any `user_id` provided in the request payload. This prevents horizontal privilege escalation (a student reading another student's data by changing an ID in the URL or request body).

5. **Department Scoping:** For chair, instructor, and advisor endpoints, the gateway similarly enforces `department_id` and `course_id` scoping from JWT claims. Staff cannot widen their own scope by crafting API calls with different department or course identifiers.
