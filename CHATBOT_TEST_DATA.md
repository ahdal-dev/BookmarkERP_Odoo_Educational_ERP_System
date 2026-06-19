# Chatbot Test Data — Structure & Injection

This describes the data the Academic Agent's 8 tools read/write, and how to inject it.
Injection is done **through the Odoo ORM via XML-RPC** (script:
[seed_chatbot_test_data.py](services/RAG-Chatbot/Backend/seed_chatbot_test_data.py)), not
raw SQL — these models have computed/stored fields (`available_seats`, `display_name`),
sequences (petition `name`), and `create()` guards, so direct Postgres `INSERT`s would
corrupt state. The "table" column below is the underlying Postgres table for reference.

## Run it
```bash
cd services/RAG-Chatbot && make seed
# or: cd services/RAG-Chatbot/Backend && ../venv/Scripts/python.exe seed_chatbot_test_data.py
```
Connects with `ODOO_URL/ODOO_DB/ODOO_USERNAME/ODOO_PASSWORD` from
`services/RAG-Chatbot/.env` (defaults `http://localhost:8081 / edu_demo_new / admin / admin`).
Idempotent — safe to re-run.

---

## 1. Students — `res.users` (+ `res.partner`)  → tables `res_users`, `res_partner`

The chatbot identifies a student by **`res.users.login` == the email** the gateway forwards.
Holds live directly on `res.users`. Creating a user auto-creates its `res.partner`
(used as `student.petition.student_id`).

**User format (what each student record needs):**

| Field | Meaning | Example |
|-------|---------|---------|
| `login` | **must equal the student's email** (chatbot lookup key) | `student@test.com` |
| `email` | same as login | `student@test.com` |
| `name` | display name | `Test Student` |
| `password` | for React/gateway login | `student123` |
| `groups_id` | must include `edu_mang_auth.group_erp_student` | `[(4, <group id>)]` |
| `is_on_hold` | hold flag (read by `check_holds`) | `false` / `true` |
| `hold_reason` | text shown when on hold | `"Outstanding library fines…"` |
| `hold_date` | date the hold was placed | `2024-…` |

**Seeded users:**

| login / email | password | role | hold |
|---------------|----------|------|------|
| `student@test.com` | `student123` | student | none — for the happy-path tests |
| `held.student@test.com` | `student123` | student | **on hold** — to test a positive `check_holds` |

> The chatbot only ever acts on the **logged-in** student (identity from the verified JWT).
> To test a *positive* hold, log in as `held.student@test.com`.

## 2. Course catalog — `education.course`  → `education_course`

| Field | Notes |
|-------|-------|
| `code` | unique, e.g. `CS101` (chatbot looks courses up by this) |
| `name`, `description` | |
| `schedule` | e.g. `MWF 10:00-11:00` (parsed into the weekly grid) |
| `timing_start`, `timing_end` | Float hours, e.g. `10.0`, `11.0` |
| `instructor` | display string |
| `credits`, `total_seats` | ints; `available_seats` is **computed** |
| `registration_open` | bool (drives "are registrations open?") |
| `semester` | `fall` / `spring` / `summer` |
| `year` | int |

Seeded: **CS101, MATH200, BIO102** (closed, to test "registration closed"), **PHYS210, ENG105**.

## 3. Enrollments — `education.registration`  → `education_registration`

| Field | Notes |
|-------|-------|
| `student_id` | **→ `res.users`** (the user id, not partner) |
| `course_id` | → `education.course` |
| `state` | `enrolled` / `dropped` / `waitlist` |
| `is_officer_override` | set **true when seeding** to bypass open/seat/hold checks in `create()` |

Seeded: `student@test.com` enrolled in **CS101, MATH200, PHYS210** (gives "my courses",
records, and a multi-day weekly schedule).

## 4. Petition categories — `petition.type`  → `petition_type`

Required so `create_petition` can resolve a type. `code` is unique; the agent maps to:
`GRADE_APPEAL`, `LATE_REG`, `COURSE_EXCEPTION`, `PREREQ_WAIVER`, `OTHER`.

## 5. Sample petition — `student.petition`  → `student_petition`

| Field | Notes |
|-------|-------|
| `student_id` | **→ `res.partner`** (the user's `partner_id`) |
| `petition_type_id` | → `petition.type` |
| `subject`, `description`, `requested_date` | |
| `name` | auto from sequence (`SP00001`, …) — don't set |

Seeded: one submitted `LATE_REG` petition for `student@test.com` so "status of my recent
petitions" returns data.

## 6. Admissions — `op.course`, `op.admission.register`, `op.admission`

`admission_application` needs an **active `op.admission.register` with a `course_id`** to
file against, and reads `op.admission` by email for status.

| Model → table | Purpose | Key fields |
|---------------|---------|-----------|
| `op.course` → `op_course` | course the cycle admits to | `name`, `code` |
| `op.admission.register` → `op_admission_register` | active admission cycle | `name`, `course_id`, `admission_base='course'`, `state='application'`, `active=true` |
| `op.admission` → `op_admission` | an application | `name`, `first_name`, `last_name`, `email`, `birth_date`, `gender` (`m`/`f`), `course_id`, `register_id`, `application_date` |

Seeded (best-effort; reuses existing OpenEduCat demo course if present): one active cycle +
a sample application `existing.applicant@example.com` for status lookups. (The "start an
application for Jane Doe" test creates its own record.)

---

## Coverage vs. the 8 tools
| Tool | Data it needs (seeded) |
|------|------------------------|
| `course_info` | `education.course` (CS101/MATH200/BIO102…) |
| `register_course` | student user + `education.course` (+ enrollments for check_status) |
| `create_petition` | `petition.type` + student partner (+ sample for status) |
| `check_holds` | `res.users` hold fields (held.student@test.com) |
| `student_records` | `education.registration` + `education.course` |
| `semester_schedule` | enrollments with `schedule`/timings |
| `gpa_calculator` | none (pure logic) |
| `admission_application` | `op.admission.register` (+ `op.course`, sample `op.admission`) |
