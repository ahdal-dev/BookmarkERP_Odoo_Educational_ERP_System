# AI Prediction Tools — QA Testing Protocol

This document instructs the QA team to validate the two **AI prediction tools** added to
the Academic Agent: **`predict_grade`** and **`predict_performance`**. Unlike the other 12
tools (which read/write Odoo over XML-RPC), these two call **separate FastAPI ML
microservices** over HTTP:

| Tool | Microservice | Endpoint | Default URL |
|------|--------------|----------|-------------|
| `predict_grade` | Grade Predictor (`services/grade_predictor_service`) | `POST /predict` | `GRADE_PREDICTOR_URL` (`http://localhost:8000`) |
| `predict_performance` | Student Performance (`services/student_performance_service`) | `POST /predict` | `STUDENT_PERFORMANCE_URL` (`http://localhost:5002`) |

It verifies five things per query group:
1. **Tool selection accuracy** — the agent picks `predict_grade` vs `predict_performance` correctly.
2. **Automated parameter extraction** — it pulls course code, GPA, grades, semesters from natural language.
3. **HTTP service interaction** — the request reaches the right ML service and a prediction returns.
4. **Graceful degradation** — when a service is down or data is insufficient, the agent stays helpful.
5. **Response formatting** — the prediction is woven into a natural, clearly-advisory reply.

> **Advisory only:** both tools return AI predictions, never an official grade or academic
> standing. The reply must make that clear and must not claim a guaranteed outcome.

---

## 0. Environment bring-up

| Component | How to start | Port |
|-----------|--------------|------|
| Odoo (host) | `venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf\odoo.conf` | 8081 |
| Gateway + Agent + **both predictors** + RabbitMQ | `cd api_gateway && docker-compose up -d --build grade_predictor student_performance academic-agent fastapi_gateway rabbitmq` | 8000 / 8001 / 8000* / 5002 |
| React frontend | `cd bookmark-frontend && npm install && npm run dev` | 5173 |

\* The grade predictor listens on **8000 inside its own container** (reached by the agent as
`http://grade_predictor:8000`); it is *not* published to the host by default (it uses `expose`,
not `ports`). To curl it directly from the host (§4), either add a `ports: ["8000:8000"]`
mapping or run it standalone (below).

**Host-run fallback (no Docker), one shell each:**
```bash
cd services/grade_predictor_service && uvicorn main:app --host 0.0.0.0 --port 8000
cd services/student_performance_service && uvicorn app.main:app --host 0.0.0.0 --port 5002
```
With both running on the host, set `GRADE_PREDICTOR_URL=http://localhost:8000` and
`STUDENT_PERFORMANCE_URL=http://localhost:5002` in the agent's `.env`.

### Login
Open <http://localhost:5173>, sign in as the **student** (`student@test.com / student123`),
and navigate to **Assistant** (`/student/assistant`).

> **Isolation note:** the student identity used as `student_id` is taken from the verified JWT
> by the gateway and forwarded to the agent — never from the chat input.

---

## 1. Pre-flight health checks

```bash
# Grade Predictor — expect {"status":"healthy","model_loaded":true}
curl http://localhost:8000/health

# Grade Predictor catalog — expect {"courses":["CSAI 101","MATH 101", ...]}
curl http://localhost:8000/courses

# Student Performance — expect {"status":"ok","model_loaded":true}
curl http://localhost:5002/health
```

**Pass criteria:** both services return HTTP 200 and `model_loaded: true`. If `model_loaded`
is `false`, the model bundle is missing — train/restore it before continuing (predictions will
be off-catalog estimates or 422s).

---

## 2. Grade Prediction → tool `predict_grade`

Type each prompt in the Assistant chat:
- "What grade am I likely to get in MATH 201?"
- "If I take CSAI 351 next semester, what should I expect? My GPA is 3.2 and I got a B in CSAI 201."
- "Can you predict my grade for PHYS 102? I have a 2.8 GPA."
- "Predict my grade in ENGL 201 — I got an A in ENGL 101 last fall."

**Pass criteria:**
- The agent selects **`predict_grade`** (not `gpa_calculator`, not `student_grades`).
- `target_course` is extracted exactly (e.g. `MATH 201`, `CSAI 351`); `cumulative_gpa` and any
  mentioned past grades are passed in `transcript_history` (`{course, grade, semester}`).
- Reply states a **predicted letter grade**, a **confidence %**, a **likely range**, and one or
  more **reasoning** lines, and explicitly frames it as an advisory AI estimate.
- If no course is named ("What grade will I get?"), the agent asks **"Which course…?"** instead
  of calling the tool.

---

## 3. Performance Assessment → tool `predict_performance`

- "Am I at risk of academic probation this semester?"
- "Based on my transcript, how is my academic performance trending?"
- "I'm planning to take CSAI 351, MATH 301, and PHYS 201 next semester. What does my performance
  outlook look like? My program is Computer Science in Engineering, I started in 2021. I completed
  Fall 2023 with CSAI 201 (B+, 3cr), MATH 201 (A-, 3cr) for a 3.5 term GPA, and Spring 2024 with
  CSAI 251 (B, 3cr), PHYS 101 (B+, 3cr) for a 3.15 term GPA."
- "Give me recommendations for improving my academic performance."

**Pass criteria:**
- The agent selects **`predict_performance`**.
- `semesters` is built as a chronological list of `{term_name, courses[], term_gpa, ...}`;
  `study_plan` carries the planned courses when mentioned.
- Reply includes a **projected GPA (with interval)**, a **risk level (High/Medium/Low)**, a
  **trajectory**, and **personalized recommendations** drawn from `student_message.summary` /
  `recommendations`.
- If fewer than **2 completed semesters** are provided, the agent asks for at least two terms of
  grades instead of calling the tool (or surfaces the service's validation message).

---

## 4. Direct API testing (bypass the agent)

### Grade Predictor
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test-student-001",
    "target_course": "MATH 201",
    "cumulative_gpa": 3.2,
    "current_semester_credit_load": 15,
    "transcript_history": [
      {"course": "MATH 101", "grade": "B+", "semester": "Fall 2023"},
      {"course": "MATH 102", "grade": "A-", "semester": "Spring 2024"},
      {"course": "CSAI 101", "grade": "A", "semester": "Fall 2023"}
    ]
  }'
```
**Expect:** JSON with `predicted_grade`, `predicted_numeric`, `confidence` (0–1),
`grade_interval` (list), `reasoning` (object), `off_catalog`, `advisory_only: true`.

### Student Performance
```bash
curl -X POST http://localhost:5002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test-student-001",
    "program": "Computer Science",
    "school": "Engineering",
    "entry_year": 2021,
    "semesters": [
      {
        "term_name": "2023 Fall",
        "courses": [
          {"course_id": "CSAI 101", "grade": "A", "credits": 3},
          {"course_id": "MATH 101", "grade": "B+", "credits": 3},
          {"course_id": "ENGL 101", "grade": "A-", "credits": 3},
          {"course_id": "PHYS 101", "grade": "B", "credits": 3},
          {"course_id": "CSAI 110", "grade": "A", "credits": 1}
        ],
        "term_gpa": 3.54, "earned_credits": 13, "attempted_credits": 13, "cumulative_gpa": 3.54
      },
      {
        "term_name": "2024 Spring",
        "courses": [
          {"course_id": "CSAI 201", "grade": "B+", "credits": 3},
          {"course_id": "MATH 201", "grade": "B", "credits": 3},
          {"course_id": "PHYS 102", "grade": "B-", "credits": 3},
          {"course_id": "ENGL 102", "grade": "A", "credits": 3}
        ],
        "term_gpa": 3.18, "earned_credits": 12, "attempted_credits": 12, "cumulative_gpa": 3.36
      }
    ],
    "study_plan": [
      {"course_id": "CSAI 351", "credits": 3, "title": "AI Fundamentals"},
      {"course_id": "MATH 301", "credits": 3, "title": "Linear Algebra"},
      {"course_id": "PHYS 201", "credits": 4, "title": "Modern Physics"}
    ]
  }'
```
**Expect:** JSON with `predicted_gpa`, `interval_lo`/`interval_hi`, `at_risk_probability`,
`at_risk`, `risk_level`, `trajectory`, `recommendations` (list), and a `student_message` object
(`summary`, `detail`, `suggested_action`, `tone`).

> **Note:** `study_plan` is a **required field** on this service. Send `"study_plan": []` if there
> is no plan — omitting the key entirely returns a 422.

---

## 5. Agent API testing (full chain: agent → tool → microservice)

Send the shared secret as `X-Chatbot-Secret` (matches `CHATBOT_SHARED_SECRET` /
`CHATBOT_ADMIN_TOKEN`). The agent runs on **8001**.

```bash
# predict_grade
curl -X POST http://localhost:8001/agent/query \
  -H "Content-Type: application/json" \
  -H "X-Chatbot-Secret: YOUR_TOKEN_HERE" \
  -d '{
    "question": "What grade will I likely get in MATH 201? My GPA is 3.2 and I got B+ in MATH 101.",
    "student_email": "student@test.com"
  }'

# predict_performance
curl -X POST http://localhost:8001/agent/query \
  -H "Content-Type: application/json" \
  -H "X-Chatbot-Secret: YOUR_TOKEN_HERE" \
  -d '{
    "question": "Am I at risk this semester? Fall 2023: CSAI 201 B+ 3cr, MATH 201 A- 3cr (term GPA 3.5). Spring 2024: CSAI 251 B 3cr, PHYS 101 B+ 3cr (term GPA 3.15). Program Computer Science, Engineering, started 2021. Planning CSAI 351, MATH 301.",
    "student_email": "student@test.com"
  }'
```

**Pass criteria:** response JSON has `tool_used` = `predict_grade` / `predict_performance`,
`tool_ok: true`, and an `answer` that weaves the prediction into a natural, advisory reply.
A request **without** the `X-Chatbot-Secret` header returns **401**.

---

## 6. Error handling

- **Service down:** `docker stop edu_erp_grade_predictor`, then ask "What grade will I get in
  MATH 201?" → the agent replies that the prediction service is temporarily unavailable
  (`tool_ok: false`), does **not** crash, and does not invent a grade. Restart afterward.
- **Off-catalog course:** ask for a grade in a made-up course (e.g. "ZZZZ 999") → the service
  returns `off_catalog: true`; the reply notes it's a rough estimate for an unknown course.
- **Insufficient data (perf):** "Am I at risk?" with only **one** term of grades → the agent asks
  for at least 2 completed semesters instead of calling the tool. (Direct API with `<2` semesters
  or missing `study_plan` → **422**, flattened into a helpful message.)
- **Missing course (grade):** "Predict my grade" with no course → agent asks "Which course…?".

---

## 7. Conversational checks

- **Ambiguity:** "Will I do well?" → agent asks which course (grade) or for recent terms (perf)
  rather than guessing.
- **Coreference:** "Tell me about CSAI 351." then "What grade would I get in it?" → "it" resolves
  to CSAI 351 and `predict_grade` is called with that course.
- **Tool disambiguation:** "What's my GPA?" → `student_grades` (official), **not** a prediction;
  "What GPA will I get next semester?" → `predict_performance`.
- **Language:** send an Arabic message → reply is in Arabic; the prediction content is preserved.

---

## 8. Regression sign-off checklist

- [ ] `GET /health` on both predictor services → 200 with `model_loaded: true`.
- [ ] `predict_grade` selected for course-grade prompts; `target_course` + transcript extracted.
- [ ] `predict_performance` selected for risk/outlook prompts; `semesters` + `study_plan` extracted.
- [ ] Direct `POST /predict` on both services returns the documented JSON shapes (§4).
- [ ] Agent `/agent/query` returns `tool_ok: true` and an advisory, natural reply (§5).
- [ ] `X-Chatbot-Secret` required on `/agent/query` (401 without it).
- [ ] Graceful degradation when a predictor service is down; no fabricated grades.
- [ ] `<2` semesters / missing course / off-catalog handled with helpful messages (§6).
- [ ] Predictions are always framed as advisory, never as official grades/standing.
- [ ] **Regression:** all original **12** tools still selected correctly for their canonical
      prompts (re-run a few from `CHATBOT_TESTING.md`, e.g. `course_info`, `gpa_calculator`,
      `student_grades`, `register_course`) — **14 tools total** now load without error.
