# Bookmark Academic ERP — Missing React Views (To-Do Checklist)

This document tracks every frontend view that must be built to satisfy the role-specific routing defined in [`Roles.md`](./Roles.md) and the access matrix in [`RBAC.md`](./RBAC.md).

**Current frontend reality** (verified against source):
- [`App.jsx`](../../bookmark-frontend/src/App.jsx) defines only `/login` and `/dashboard`.
- [`ProtectedRoute.jsx`](../../bookmark-frontend/src/components/ProtectedRoute/ProtectedRoute.jsx) only checks *authenticated vs. not* — it has no role awareness.
- [`DashboardPage.jsx`](../../bookmark-frontend/src/pages/DashboardPage/DashboardPage.jsx) is the only landing screen (the App Launcher).

Everything below is unbuilt unless explicitly noted.

---

## Post-Login Landing Routes (per this implementation)

| Role | Landing Route | Lands on App Launcher? |
|---|---|---|
| System Administrator | `/apps` | ✅ Yes |
| Registrar | `/apps` | ✅ Yes |
| Admission Officer | `/apps` | ✅ Yes |
| Student | `/student/dashboard` | ❌ Bypassed |
| Instructor | `/faculty/dashboard` | ❌ Bypassed |
| Academic Advisor | `/faculty/dashboard` | ❌ Bypassed |
| Department Chair | `/faculty/dashboard` | ❌ Bypassed |
| Support Technician | `/support/chat-queue` | ❌ Bypassed |
| Prospective Student | `/admissions/status` | ❌ Bypassed |

> **Note on the shared `/faculty/dashboard`:** Instructor, Advisor, and Chair share one landing route. The dashboard renders role-specific widgets based on `user.role`, but each still navigates to its own sub-views (below).

---

## 0. Routing Infrastructure (Build First — Blocks Everything Else)

- [ ] `RoleRouter` component — reads `user.role`, redirects to the correct landing route after login.
- [ ] `RoleProtectedRoute` component — extends `ProtectedRoute` with an `allowedRoles` prop; redirects to `/unauthorized` on scope violation.
- [ ] `UnauthorizedPage` (`/unauthorized`) — shown when a user hits a route outside their role.
- [ ] `NotFoundPage` (`*`) — replaces the current catch-all redirect to `/login`.
- [ ] **Gateway fix:** login endpoint must derive the real role from Odoo groups and return it in the JWT + response body (currently hardcoded to `admin`).

---

## 1. Prospective Student (Guest / Candidate)

- [ ] `AdmissionsPortalPage` (`/admissions`) — public list of active programs.
- [ ] `ApplicationFormPage` (`/admissions/apply`) — multi-step application form with OCR document upload.
- [ ] `ApplicationStatusPage` (`/admissions/status`) — **landing view.** Reference-number status tracker.

## 2. Admission Officer

- [ ] `OfficerPipelinePage` (`/admissions/officer`) — Kanban pipeline of all applications.
- [ ] `ApplicationReviewPage` (`/admissions/officer/application/:id`) — detail view with OCR data, documents, and Accept/Reject/Review actions.
- [ ] App Launcher tile linking to the officer pipeline (officer lands on `/apps`).

## 3. Student

- [ ] `StudentDashboardPage` (`/student/dashboard`) — **landing view.** Schedule, GPA, active petition status.
- [ ] `CourseCatalogPage` (`/student/courses`) — browse catalog, add to cart/wishlist.
- [ ] `RegistrationPage` (`/student/registration`) — enroll/drop with real-time seat validation and time-slot enforcement.
- [ ] `GradesPage` (`/student/grades`) — read-only transcript and grades.
- [ ] `PetitionListPage` (`/student/petitions`) — list of submitted petitions with live status.
- [ ] `PetitionFormPage` (`/student/petitions/new`) — submit an enrollment-override or grade-dispute petition.

## 4. Instructor (Teacher / Professor)

- [ ] `FacultyDashboardPage` (`/faculty/dashboard`) — **shared landing view** (instructor variant): assigned courses + pending-petition badge.
- [ ] `ClassRosterPage` (`/faculty/courses/:courseId`) — enrolled students for a specific course.
- [ ] `FacultyPetitionQueuePage` (`/faculty/petitions`) — **key missing screen.** Petition review queue scoped to the instructor's courses.
- [ ] `PetitionReviewPage` (`/faculty/petitions/:id`) — petition detail with Approve/Reject. **Shared component** reused by Advisor and Chair.

## 5. Academic Advisor

- [ ] `FacultyDashboardPage` (`/faculty/dashboard`) — shared landing view (advisor variant): advisee count + petition queue.
- [ ] `AdviseeListPage` (`/faculty/advisees`) — searchable list of assigned advisees.
- [ ] `AdviseeProfilePage` (`/faculty/advisees/:studentId`) — read-only academic profile and transcript.
- [ ] `FacultyPetitionQueuePage` (`/faculty/petitions`) — advisor-scoped petition queue (reuses the instructor queue component, advisor data scope).
- [ ] Reuses `PetitionReviewPage` (`/faculty/petitions/:id`).

## 6. Department Chair

- [ ] `FacultyDashboardPage` (`/faculty/dashboard`) — shared landing view (chair variant): escalated petitions + department summary.
- [ ] `ChairPetitionQueuePage` (`/faculty/chair/petitions`) — **key missing screen.** All department petitions with full decision history.
- [ ] `PetitionOverridePage` (`/faculty/chair/petitions/:id`) — **Department Chair Override Screen.** Shows prior instructor/advisor rulings + a final Override action.
- [ ] `DepartmentStudentRecordsPage` (`/faculty/chair/students`) — read-only access to all department student records.

## 7. Registrar

- [ ] App Launcher tile set (registrar lands on `/apps`).
- [ ] `RegistrarDashboardPage` (`/registrar/dashboard`) — registration-window status + live enrollment monitor.
- [ ] `TimeSlotConfiguratorPage` (`/registrar/timeslots`) — **key missing screen.** Priority-based registration window builder ("Ruleset Configurator").
- [ ] `CourseCatalogManagerPage` (`/registrar/courses`) — full CRUD course catalog manager (distinct from the student read-only catalog).
- [ ] `EnrollmentMonitorPage` (`/registrar/enrollment`) — real-time seat counts and compliance dashboard.

## 8. Support Technician (Student Affairs)

- [ ] `SupportChatQueuePage` (`/support/chat-queue`) — **landing view.** Live chat queue + active sessions. **Support Technician Live Chat Interface.**
- [ ] `ChatSessionPage` (`/support/chat/:sessionId`) — single live-chat conversation view.
- [ ] `StudentQuickLookupDrawer` (side drawer, no route) — read-only student profile/registration lookup from within a chat.
- [ ] `TicketListPage` (`/support/tickets`) — support ticket queue.

## 9. System Administrator (Super Admin)

- [ ] `AppLauncherPage` (`/apps`) — **landing view.** Rename/relocate the existing [`DashboardPage`](../../bookmark-frontend/src/pages/DashboardPage/DashboardPage.jsx) here.
- [ ] `UserRoleManagerPage` (`/admin/users`) — create/edit users and assign roles.
- [ ] `AdmissionRulesConfiguratorPage` (`/admin/admissions/rules`) — per-program GPA floors, required documents, seat caps.
- [ ] `AuditLogPage` (`/admin/audit-log`) — read-only authentication & system-event log.
- [ ] `SystemSettingsPage` (`/admin/settings`) — global ERP configuration.

---

## Shared / Reusable Components

- [ ] `RoleLayout` — sidebar/topbar shell that renders nav items filtered by `user.role`.
- [ ] `PetitionReviewPage` — single petition detail; reused by Instructor, Advisor, and Chair (Chair variant adds the Override action).
- [ ] `PetitionStatusBadge` — consistent status pill used across student, faculty, and chair views.
- [ ] `StudentQuickLookupDrawer` — read-only student card; reused by Support and Advisor.
