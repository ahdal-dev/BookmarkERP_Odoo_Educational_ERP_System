# Bookmark Academic ERP — User Roles & Scenarios

> **Architecture Note (Current State):** The React router in [`bookmark-frontend/src/App.jsx`](../../bookmark-frontend/src/App.jsx) currently defines only `/login` and `/dashboard`. The `AuthContext` in [`bookmark-frontend/src/context/AuthContext.jsx`](../../bookmark-frontend/src/context/AuthContext.jsx) already stores `user.role` from the API response. All role-specific routes listed below are the **target architecture** and must be built. See `## Upcoming React Views (To-Do List)` at the bottom of this file.

This document outlines the primary user roles within the Bookmark Academic ERP system and details the main scenarios each role interacts with inside the custom React frontend. Upon successful login, the React router reads `user.role` from `AuthContext` and **immediately redirects** the user to their dedicated landing view — no generic app launcher, no Odoo XML dashboard.

---

## 1. Prospective Student (Guest / Candidate)

* **Description:** An individual seeking admission who has not yet been granted an official student account. Interacts entirely with **public, unauthenticated** React screens.
* **Default React Route / Landing View:** `/admissions` — Public Admission Portal Home
* **Main Scenario (Application & Tracking):**
  The prospective student navigates to `/admissions` on the React frontend to browse all active admission programs. From there, they click through to `/admissions/apply`, which renders a multi-step React form where they fill in personal information and upload eligibility documents (transcripts, diplomas). Files are sent to the OCR microservice via the FastAPI gateway (`POST /api/admissions/apply`) to reduce manual data entry. Upon submission, the React form displays a unique reference number. The applicant then visits `/admissions/track` and enters their reference number to see a live status card — no account or login required.

---

## 2. Admission Officer

* **Description:** Administrative staff responsible for reviewing, evaluating, and processing incoming student applications.
* **Default React Route / Landing View:** `/admissions/officer` — Application Pipeline Dashboard
* **Main Scenario (Application Processing):**
  Upon login, the Admission Officer is redirected to `/admissions/officer`, a Kanban-style React dashboard that displays all submitted applications fetched from the API (`GET /api/admissions/applications`). The officer clicks an application card to navigate to `/admissions/officer/application/:id`, a detail view showing the applicant's form data, OCR-extracted fields, and attached documents. Status-change buttons (e.g., "Move to Review", "Accept", "Reject") issue `PATCH /api/admissions/applications/:id/status` calls through the gateway. There is no access to the Odoo backend UI.

---

## 3. Student

* **Description:** A fully enrolled individual with an active, secure student account.
* **Default React Route / Landing View:** `/student` — Student Portal Home
* **Main Scenarios (Registration & Petitions):**
  * **Portal Home:** After login, the student lands on `/student`, a personalized dashboard showing their current schedule, GPA summary, and any active petition statuses. All data is fetched via `GET /api/student/profile`.
  * **Registration:** The student navigates to `/student/courses` to browse the course catalog and add courses to a persistent wishlist/cart (`POST /api/student/cart`). During their assigned time slot, they visit `/student/registration` to finalize enrollment with real-time seat validation (`POST /api/student/registration`). Dropping a course during the add/drop period is handled by a `DELETE /api/student/registration/:courseId` call on the same screen.
  * **Petitions:** The student visits `/student/petitions` to see a list of all their submitted petitions with live status updates. They click "New Petition" to navigate to `/student/petitions/new`, a React form for submitting an enrollment override or grade dispute petition (`POST /api/student/petitions`).

---

## 4. Instructor (Teacher / Professor)

* **Description:** Academic faculty responsible for teaching courses and managing course-level student exceptions.
* **Default React Route / Landing View:** `/instructor` — Instructor Dashboard
* **Main Scenario (Course-Level Approvals):**
  The instructor lands on `/instructor`, showing a summary of their assigned courses and a count of pending petitions. They click a course card to open `/instructor/courses/:courseId`, a class roster view showing all enrolled students (`GET /api/instructor/courses/:courseId/students`). A "Petitions" badge in the navigation notifies them of pending items; clicking it opens `/instructor/petitions`, a queue listing all petitions scoped to their courses (`GET /api/instructor/petitions`). They click a petition to open `/instructor/petitions/:id`, where they review the student's academic context and issue an Approve or Reject action (`PATCH /api/petitions/:id/decision`).

---

## 5. Academic Advisor

* **Description:** Faculty or staff assigned to guide a specific cohort of students through their academic journey.
* **Default React Route / Landing View:** `/advisor` — Advisor Dashboard
* **Main Scenario (Academic Guidance):**
  The advisor lands on `/advisor`, a dashboard showing their advisee count and pending petition queue. They visit `/advisor/advisees` to see a searchable list of their assigned students (`GET /api/advisor/advisees`). Clicking a student opens `/advisor/advisees/:studentId`, a read-only academic profile view showing the student's full transcript and degree progress (`GET /api/advisor/advisees/:studentId`). Petitions routed to them appear at `/advisor/petitions`, and each petition detail view allows an Approve or Reject action (`PATCH /api/petitions/:id/decision`).

---

## 6. Department Chair

* **Description:** The executive academic head of a specific department.
* **Default React Route / Landing View:** `/chair` — Department Chair Dashboard
* **Main Scenario (Executive Override):**
  The chair lands on `/chair`, showing escalated petitions and a department-wide summary. They navigate to `/chair/petitions` to view all petitions within their department, including those already ruled on by instructors or advisors (`GET /api/chair/petitions`). Each petition's detail view exposes the full decision history and an "Override" action that supersedes prior rulings (`PATCH /api/petitions/:id/override`). They can also access `/chair/students` to read academic records for any student in their department (`GET /api/chair/students`).

---

## 7. Registrar

* **Description:** The administrative authority responsible for the structural management of courses, enrollment, and institutional records.
* **Default React Route / Landing View:** `/registrar` — Registrar Dashboard
* **Main Scenario (Registration Management):**
  The registrar lands on `/registrar`, a control center showing registration window status and a live enrollment monitor. Before each semester, they navigate to `/registrar/timeslots` — the Registration Time Slot Configurator — where they define priority-based windows (e.g., seniors register Day 1, freshmen Day 3) via a form that calls `POST /api/registrar/timeslots`. They manage the course catalog at `/registrar/courses` (full CRUD via `/api/registrar/courses`). During peak registration hours, they monitor `/registrar/enrollment` for real-time seat counts and institutional compliance (`GET /api/registrar/enrollment/status`).

---

## 8. Support Technician (Student Affairs)

* **Description:** Staff dedicated to assisting students with technical or administrative issues during their interaction with the ERP.
* **Default React Route / Landing View:** `/support` — Support Chat Dashboard
* **Main Scenario (Live Troubleshooting):**
  The technician lands on `/support`, a real-time chat dashboard showing active student sessions and a ticket queue. During critical periods like registration, they communicate directly with students through the embedded chat interface. They can open a read-only student quick-lookup panel (accessible as a side drawer from any conversation, calling `GET /api/support/students/:studentId`) to view the student's basic profile and registration status without altering any data. Resolved issues are logged as support tickets via `POST /api/support/tickets`.

---

## 9. System Administrator (Super Admin)

* **Description:** The IT or system lead responsible for global system configuration, security, and maintenance.
* **Default React Route / Landing View:** `/admin/apps` — App Launcher
* **Main Scenario (System & Security Configuration):**
  The Super Admin is the **only role** that lands on the App Launcher (`/admin/apps`), the current `DashboardPage` component — all other roles bypass this screen entirely. From the launcher, they navigate to `/admin/users` to manage user accounts and assign roles (`GET/PATCH /api/admin/users`), to `/admin/admissions/rules` to configure per-program admission requirements (minimum GPA enforcement, required documents), and to `/admin/audit-log` to review a chronological log of all authentication events and system-level changes (`GET /api/admin/audit-log`). Global system settings are managed at `/admin/settings`.

---

## Upcoming React Views (To-Do List)

The following screens are required by the role-routing architecture above but **do not yet exist** in the frontend. This list is ordered by functional area for sprint planning. The existing router in [`App.jsx`](../../bookmark-frontend/src/App.jsx) and `ProtectedRoute` in [`ProtectedRoute.jsx`](../../bookmark-frontend/src/components/ProtectedRoute/ProtectedRoute.jsx) must also be upgraded to support role-aware routing before any of these views can be wired up.

### Infrastructure (Build First)

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P0 | `RoleProtectedRoute` | — | Wraps `ProtectedRoute`; reads `user.role` from `AuthContext`, redirects to role's landing view or `/unauthorized` if scope is violated. Replaces the current single-role `ProtectedRoute`. |
| P0 | Role-based redirect in `App.jsx` | `/` (post-login) | After `AUTH_SUCCESS`, router inspects `user.role` and calls `<Navigate>` to the correct landing route. |
| P0 | `UnauthorizedPage` | `/unauthorized` | Shown when a user navigates to a route outside their role scope. |

### Public (No Auth)

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P1 | `AdmissionsPortalPage` | `/admissions` | Lists active programs. Fully public. |
| P1 | `ApplicationFormPage` | `/admissions/apply` | Multi-step form with document upload. Integrates OCR microservice. |
| P1 | `ApplicationTrackerPage` | `/admissions/track` | Reference-number lookup. No login required. |

### Admission Officer Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P1 | `OfficerPipelinePage` | `/admissions/officer` | Kanban board of all applications. Officer's landing view. |
| P1 | `ApplicationDetailPage` | `/admissions/officer/application/:id` | Form data, OCR output, status change buttons. |

### Student Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P1 | `StudentPortalPage` | `/student` | Student's landing view. Schedule, GPA, petition status. |
| P1 | `CourseCatalogPage` | `/student/courses` | Browse courses, add to cart/wishlist. |
| P1 | `RegistrationPage` | `/student/registration` | Enroll/drop with real-time seat validation and time-slot enforcement. |
| P2 | `GradesPage` | `/student/grades` | Read-only transcript and grade viewer. |
| P1 | `PetitionListPage` | `/student/petitions` | List of student's submitted petitions with live status. |
| P1 | `PetitionFormPage` | `/student/petitions/new` | Form for submitting a new petition (override, grade dispute, etc.). |

### Instructor Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P1 | `InstructorDashboardPage` | `/instructor` | Instructor's landing view. Course summary + petition badge. |
| P1 | `ClassRosterPage` | `/instructor/courses/:courseId` | Enrolled student list for a specific course. |
| P1 | `InstructorPetitionQueuePage` | `/instructor/petitions` | All petitions scoped to instructor's courses. **This screen is the key missing piece for the petition workflow.** |
| P1 | `PetitionReviewPage` | `/instructor/petitions/:id` | Single petition detail with Approve/Reject actions. Shared layout with Advisor & Chair petition detail view. |

### Academic Advisor Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P2 | `AdvisorDashboardPage` | `/advisor` | Advisor's landing view. Advisee count, petition queue. |
| P2 | `AdviseeListPage` | `/advisor/advisees` | Searchable list of the advisor's assigned students. |
| P2 | `AdviseeProfilePage` | `/advisor/advisees/:studentId` | Read-only full academic profile and transcript. |
| P2 | `AdvisorPetitionQueuePage` | `/advisor/petitions` | Petitions routed to this advisor. Shares the `PetitionReviewPage` for the detail view. |

### Department Chair Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P2 | `ChairDashboardPage` | `/chair` | Chair's landing view. Escalated petitions, department summary. |
| P2 | `ChairPetitionQueuePage` | `/chair/petitions` | All department petitions with full decision history and Override action. |
| P2 | `DepartmentStudentRecordsPage` | `/chair/students` | Read-access to all student records within the chair's department. |

### Registrar Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P1 | `RegistrarDashboardPage` | `/registrar` | Registrar's landing view. Registration window status, live enrollment monitor. |
| P1 | `TimeSlotConfiguratorPage` | `/registrar/timeslots` | **Key missing piece.** Priority-based registration window builder. |
| P1 | `CourseCatalogManagerPage` | `/registrar/courses` | Full CRUD for the course catalog. Different from the student's read-only catalog view. |
| P2 | `EnrollmentMonitorPage` | `/registrar/enrollment` | Real-time seat counts and compliance dashboard for peak registration. |

### Support Technician Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P2 | `SupportDashboardPage` | `/support` | Support technician's landing view. Live chat sessions and ticket queue. |
| P2 | `StudentQuickLookupDrawer` | (side drawer, no dedicated route) | Read-only student profile panel opened from within a chat session. |

### System Administrator Views

| Priority | Component / File | Route | Notes |
|---|---|---|---|
| P1 | Rename `DashboardPage` → `AppLauncherPage` | `/admin/apps` | The current `DashboardPage` becomes the admin-only app launcher. Route must change. |
| P1 | `UserRoleManagerPage` | `/admin/users` | Create/edit users and assign roles. CRUD via `/api/admin/users`. |
| P2 | `AdmissionRulesConfiguratorPage` | `/admin/admissions/rules` | Per-program GPA floors, required document types, seat caps. |
| P2 | `AuditLogPage` | `/admin/audit-log` | Chronological log of auth events and system changes. Read-only. |
| P2 | `SystemSettingsPage` | `/admin/settings` | Global ERP configuration. |
