# Academic Agent Chatbot — QA Testing Protocol

This document instructs the QA team to validate the integrated AI Chatbot Agent
across the full stack: **React UI → FastAPI Gateway → Academic Agent microservice
→ headless Odoo**, with **RabbitMQ** offloading the two write-heavy tools.

It verifies five things per query group:
1. **Tool selection accuracy** — the agent picks the right tool.
2. **Automated parameter extraction** — it pulls params (course code, grades, dates…) from natural language.
3. **Headless Odoo DB interaction** — reads/writes hit the real Odoo models.
4. **RabbitMQ queuing** — `register_course` (enroll/drop) and `create_petition` (submit) publish events; a worker performs the write.
5. **Response formatting** — Markdown renders cleanly (tables/grids for schedules & records).

---

## 0. Environment bring-up

| Component | How to start | Port |
|-----------|--------------|------|
| Odoo (host) | `venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf\odoo.conf` | 8081 |
| RabbitMQ + Gateway + Academic Agent + Worker | `cd api_gateway && docker-compose up -d rabbitmq academic-agent academic-agent-worker fastapi_gateway` | 5672 / 15672 / 8000 |
| React frontend | `cd bookmark-frontend && npm install && npm run dev` | 5173 |

**Host-run fallback for the agent** (no Docker): in `services/RAG-Chatbot/`
`make install-agent`, then `make agent` (`:8001`) and `make worker` in separate
shells, with a local RabbitMQ reachable at `AMQP_URL`.

### Pre-flight checks
- `GET http://localhost:8001/health` → `{"status":"ok","dependencies":{"odoo":true,"rabbitmq":true}}`.
- `GET http://localhost:8000/health` → gateway healthy.
- RabbitMQ management UI: <http://localhost:15672> (guest/guest) → queues
  `registration.attempt` and `petition.submitted` exist (created on first publish/worker start).
- Confirm `OPENROUTER_API_KEY` is set (agent `.env`) and `CHATBOT_SHARED_SECRET`
  (gateway) matches `CHATBOT_ADMIN_TOKEN` (agent).

### Login
Open <http://localhost:5173>, sign in as the **student**:
`student@test.com / student123`. Navigate to **Assistant** (`/student/assistant`).

> **Isolation note:** the student identity is taken from the verified JWT by the
> gateway and forwarded to the agent — never from the chat input. See §10.

---

## 1. Course Info  → tool `course_info`
Run each; expect the right course pulled from `education.course`.
- "What is the schedule and instructor for course CS101?"
- "How many available seats are left in MATH200?"
- "Are registrations currently open for BIO102?"

**Pass criteria:** correct `course_code` extracted; reply states schedule, instructor,
seats (available/total), and open/closed status. Unknown code → graceful "couldn't find" message.

## 2. GPA Calculator  → tool `gpa_calculator` (pure logic, no Odoo)
- "I got an A in Calculus (4 credits) and a B+ in Physics (3 credits). Can you estimate my GPA?"
  → expect **(4×4.0 + 3×3.3)/7 = 3.70**.
- "My current GPA is 3.5 over 60 credits. If I get an A- in a 3-credit course, what will my new GPA be?"
  → expect **(3.5×60 + 3.7×3)/63 ≈ 3.51**.

**Pass criteria:** correct 4.0-scale math; clearly labeled as an estimate; no Odoo call needed.

## 3. Course Registration  → tool `register_course`  *(RabbitMQ)*
- "What courses am I currently registered for?" → `action=check_status` (**synchronous read** from `education.registration`).
- "Please register me for course CS101." → `action=register` → **queued** to `registration.attempt`.
- "I need to drop course CS101 from my schedule." → `action=drop` → **queued**.

**Pass criteria:**
- check_status returns the live enrolled list (no queue).
- register/drop reply is a "received / being processed" (202-style) message — it must **NOT** claim the action is finalized.
- In RabbitMQ UI, a message passes through `registration.attempt`.
- Worker log (`docker logs edu_erp_academic_agent_worker`) shows `registration.attempt ok: ...`.
- Re-ask "What courses am I registered for?" → the change is reflected in Odoo.

## 4. Petitions  → tool `create_petition`  *(RabbitMQ on submit)*
- "I'd like to submit a petition for late registration for CS101. The reason is that I had a medical emergency last week."
  → `action=submit`, `petition_type=late_registration` → **queued** to `petition.submitted`.
- "What is the status of my recent petitions?" → `action=check_status`, no reference (**synchronous read**).
- "Can you check the status of petition reference PET-2024-001?" → `action=check_status` with `reference` (read; expect "couldn't find" if it doesn't exist — references in this system look like `SP00001`).

**Pass criteria:** submit returns a queued/202 message; a `petition.submitted` message appears in
RabbitMQ; worker log shows the write; a new `student.petition` record exists in Odoo; status lookups read correctly.

## 5. Holds  → tool `check_holds`
- "Do I have any administrative or financial holds on my account?"

**Pass criteria:** reads `res.users` hold flags; returns a clear boolean status and, if held,
the reason/date. (Category like "financial" is acknowledged as not separately tracked.)

## 6. Semester Schedule  → tool `semester_schedule`
- "What does my weekly schedule look like for the Fall 2024 semester?"
- "Show me my schedule."

**Pass criteria:** builds a weekly grid from enrolled `education.course` rows; **renders as a
Markdown table** (Day | Time | Course | Instructor) in the UI; semester/year filter respected.

## 7. Records  → tool `student_records`
- "Can you give me an unofficial summary of my transcript and my total credits?" → `action=transcript`.
- "How many total credits am I currently enrolled in?" → `action=enrollment_verify`.

**Pass criteria:** aggregates `education.registration` + course credits; clearly marked **unofficial**
(no grades/GPA — points to Registrar / suggests `gpa_calculator`); total credits correct.

## 8. Admissions  → tool `admission_application`
- "I want to start an admission application. My name is Jane Doe, my email is jane.doe@example.com, my birth date is 2002-05-15, and my gender is female."
  → `action=start_application`; creates an `op.admission` record.
- "What is the status of the admission application under jane.doe@example.com?"
  → `action=check_status` by email.

**Pass criteria:** all four params extracted; gender mapped to Odoo code (`f`); record created
when an active `op.admission.register` cycle exists; status lookup returns the most recent application.

---

## 9. Conversational / parameter-extraction checks
- Ambiguity: "Register me for the math course." → agent asks for the **course code** instead of guessing.
- Coreference: "What's the schedule for CS101?" then "Is it open for registration?" → "it" resolves to CS101.
- Language: send an Arabic message → reply is in Arabic.

## 10. Security / data-isolation checks
- Inspect the gateway→agent request (gateway logs / network): the body's `student_email`
  equals the **logged-in** student, regardless of any email typed in chat.
- "Show me John Smith's schedule" (another student) → the agent declines / only ever returns the
  authenticated student's data.
- Call `POST http://localhost:8001/agent/query` **without** the `X-Chatbot-Secret` header → `401`.

## 11. Resilience
- Stop RabbitMQ, then "register me for CS101" → the agent **falls back to a synchronous write**
  (still succeeds) and logs `MQ unavailable, falling back...`. Restart RabbitMQ afterward.
- Stop the Academic Agent container → the gateway returns `502` with a friendly "assistant unavailable" message; the UI shows the error bar.

---

## Regression sign-off checklist
- [ ] All 8 tools selected correctly for their canonical prompts (§1–§8).
- [ ] Parameters auto-extracted (codes, grades, dates, names, gender).
- [ ] Reads hit Odoo live; writes create/modify the correct Odoo records.
- [ ] `register`/`drop`/petition-`submit` enqueue to RabbitMQ; worker performs the write; 202-style replies.
- [ ] Markdown (tables/grids) renders correctly in the chat UI.
- [ ] JWT-derived identity enforced; shared-secret required on `/agent/query`.
- [ ] Graceful degradation when RabbitMQ / agent service is down.
