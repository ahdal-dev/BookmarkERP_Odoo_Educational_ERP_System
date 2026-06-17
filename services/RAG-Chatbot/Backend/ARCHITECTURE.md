# Educational ERP Chatbot — Architecture

This service powers a single `/ask` endpoint that combines two cooperating
systems:

1. A **RAG (Retrieval-Augmented Generation) chatbot** that answers
   informational questions from organization-uploaded documents.
2. An **agentic chatbot** that performs real actions against the Odoo
   Educational ERP (course registration, petitions, holds, records,
   admissions, GPA estimation) via XML-RPC.

Both share the same Gemini model, the same chat history, and the same
`/ask` request/response cycle — the agent decides per-turn whether to answer
from documents or call a tool.

---

## 1. High-level component map

```
                       ┌─────────────────────────────────────────┐
                       │              Frontend (chat UI)          │
                       └───────────────────┬───────────────────────┘
                                            │ POST /ask
                                            ▼
┌───────────────────────────────────────────────────────────────────────┐
│                          FastAPI app (main.py)                         │
│                                                                         │
│  1. Auth/org checks, load/create Chat                                  │
│  2. classify_message_llm()  ── greeting-only fast path                 │
│  3. rewrite_query_with_history()  ── standalone query                  │
│  4. embed_query() + pgvector similarity search (document_chunks)       │
│  5. run_agent(question, snippets, history, student_email)              │
│         │                                                               │
│         ├── informational → RAG answer + judge_answer_llm() + sources  │
│         └── action request → Gemini function-call → agent_tools.* →    │
│                               Odoo XML-RPC → follow-up answer           │
│  6. Persist user+assistant ChatMessage rows                            │
└───────────────────────────────────┬───────────────────┬───────────────┘
                                     │                    │
                       ┌─────────────▼──────┐   ┌─────────▼────────────┐
                       │ Postgres + pgvector │   │   Odoo (XML-RPC)      │
                       │ documents,          │   │ education.*, op.*,    │
                       │ document_chunks,    │   │ student.petition,     │
                       │ chats, messages     │   │ res.users, ...        │
                       └─────────────────────┘   └───────────────────────┘
```

Key files:

| File | Role |
|---|---|
| `main.py` | FastAPI app, `/ask` orchestration, persistence, auth |
| `llm.py` | Gemini wrappers: classify, rewrite, judge, prompt building |
| `agent.py` | Agentic layer: system prompt, tool declarations, `run_agent()` |
| `agent_tools.py` | Tool implementations, talk to Odoo via `odoo_client` |
| `odoo_client.py` | Thin XML-RPC client to Odoo (`search_read`, `execute_kw`, `find_student`) |
| `ingestion.py` | Document chunking + embedding for the RAG knowledge base |

---

## 2. RAG chatbot flow (informational questions)

**Goal:** answer questions strictly from documents the org has uploaded
(policies, handbooks, course catalogs, etc.), in the user's language, with
source citations.

### Step-by-step (`/ask` in `main.py`)

1. **Validate** the user belongs to the org and the chat exists (or create one).
2. **Greeting check** — `classify_message_llm()` (in `llm.py`) asks Gemini to
   classify the message as `greeting_only` vs `needs_answer`.
   - If `greeting_only`: reply immediately with a short greeting in the
     detected language, **no retrieval, no sources, no agent call**.
3. **Load recent history** (last 8 messages) for context.
4. **Rewrite to a standalone query** — `rewrite_query_with_history()` resolves
   pronouns/follow-ups ("its schedule" → "CS101's schedule") using the last
   ~7 turns, preserving the user's language.
5. **Embed + retrieve** — `embed_query()` embeds the rewritten query;
   a pgvector `<=>` similarity search against `document_chunks` (scoped to
   the org) returns the top `RAG_TOP_K` (default 40) chunks, ordered by
   distance. The top `RAG_LLM_SNIPPETS` (default 8) are kept as context.
6. **Run the agent** — `run_agent()` is called with the question, the kept
   snippets, recent history, and the student's email. (See §3 — this is the
   single entry point shared with the agentic flow.)
7. **If no tool was used** (pure informational answer):
   - `judge_answer_llm()` checks whether the draft answer is actually
     grounded in the snippets or amounts to "I don't know."
   - If grounded: append a `Sources:` block listing the unique document
     filenames behind the top chunks, and return those filenames in the API
     response's `sources` field for citation in the UI.
   - If "unknown": no sources are attached/persisted.
8. **Persist** the user message and the final assistant message (with
   citations) to `chat_messages`. Auto-title new chats from the first
   question.

### Example user scenario — RAG path

> **Student:** "What's the late-drop policy for this semester?"

- Not a greeting → proceeds.
- Rewritten query: unchanged (no pronouns).
- Retrieval finds chunks from an uploaded "Academic Policies" PDF.
- `run_agent()` sees this is purely informational (no action verb) → answers
  directly from the snippets, in the user's language.
- `judge_answer_llm()` confirms it's grounded → response includes
  `Sources: Academic Policies.pdf`.

If the org hasn't uploaded anything relevant, snippets are empty/irrelevant,
the judge returns `unknown`, and the user gets a friendly "I don't have that
information" reply with no sources — and is implicitly free to instead ask
for an action (handled by the agentic side).

---

## 3. Agentic chatbot flow (real ERP actions)

**Goal:** let students perform real self-service actions — register/drop
courses, file petitions, check holds, view enrollment, estimate GPA, apply
for admission — by calling Odoo via XML-RPC, with Gemini function-calling
choosing and parameterizing the tool.

### `run_agent()` (`agent.py`)

1. Build a `genai.GenerativeModel` with `tools=TOOL_DECLARATIONS` and
   `system_instruction=AGENT_SYSTEM_PROMPT`.
2. Build a single prompt containing: recent conversation history, the RAG
   context snippets (so the model can still answer hybrid questions), and
   the user's message.
3. `chat.send_message(prompt)` — Gemini either:
   - returns plain text (informational answer — falls back to the RAG path
     in §2), **or**
   - returns a **function call** (`fc.name`, `fc.args`) naming one of the
     tools below.
4. If a function call is returned:
   - Look up the Python implementation in `TOOL_DISPATCH` (`agent_tools.py`).
   - Call it with `(tool_args, student_email)`.
   - The tool talks to Odoo via `odoo_client.execute_kw` /
     `search_read` / `find_student`, and returns
     `{"ok": bool, "data": ..., "message": "..."}`.
   - Errors are caught at every layer: `OdooConnectionError` → generic
     "system unavailable" message; `OdooError` (business/validation) → the
     cleaned Odoo message; any other exception → generic fallback message.
     All are logged server-side (`print(...)`) for diagnosis.
5. **Follow-up turn** — the tool result is sent back to Gemini as a
   `FunctionResponse`. Gemini produces the final natural-language reply,
   weaving the tool's `message` into the user's language/tone. If this
   second call fails, the tool's raw `message` is used directly.
6. Returns `{"answer", "tool_used", "tool_ok"}` to `main.py`. When
   `tool_used` is set, the RAG citation/judge step is skipped entirely (an
   action result isn't "sourced" from documents).

**Identity resolution:** the student is identified by matching the
RAG-Chatbot `User.email` against Odoo's `res.users.login` via
`find_student()`. If no match, tools return a "no student profile linked to
your account" message — the assistant never acts on someone else's behalf
and never fabricates a successful action.

### Available tools (`agent_tools.py`)

| Tool | Actions | Odoo models | Notes |
|---|---|---|---|
| `course_info` | `schedule` / `prerequisites` / `availability` / `faculty` | `education.course` | Case-insensitive course code lookup (`=ilike`); prerequisites note limitation |
| `register_course` | `register` / `drop` / `check_status` | `education.registration`, `education.course` | `register`/`drop` rely on the model's own validation (seats, holds, windows, duplicates) surfaced as friendly errors |
| `create_petition` | `submit` / `check_status` | `student.petition`, `petition.type` | `submit` returns a human reference (e.g. `SP00001`) used later for `check_status` |
| `check_holds` | `all` / `academic` / `financial` / `conduct` / `library` | `res.users` | Only a single generic hold flag exists; category is informational only |
| `student_records` | `enrollment_verify` / `transcript` / `grades` / `gpa` / `degree_audit` | `education.registration`, `education.course` | `transcript` = unofficial enrollment summary grouped by term; `grades`/`gpa`/`degree_audit` are out of scope (point to Registrar; `gpa` also suggests `gpa_calculator`) |
| `admission_application` | `start_application` / `submit` / `check_status` | `op.admission`, `op.admission.register` | Validates required personal info before creating; gender mapped to Odoo's `m`/`f` codes |
| `gpa_calculator` | (pure computation) | — | "What-if" GPA estimator on a 4.0 scale from `{course_code, credits, grade}` + optional current GPA/credits; no Odoo dependency |
| `semester_schedule` | (optional `semester`/`year` filters) | `education.registration`, `education.course` | Weekly timetable template built from enrolled courses' `schedule`/`timing_start`/`timing_end`/`instructor`, grouped by day of week |

### Tool usage rules (enforced via `AGENT_SYSTEM_PROMPT`)

- At most **one tool call per user turn**.
- Missing/ambiguous parameters → the model asks a clarifying question instead
  of guessing or calling the tool.
- A tool result with `ok: false` is never reported as success; the model
  explains the issue and suggests a next step (e.g. "registration is closed —
  want me to file a late-registration petition?").
- The assistant only ever manages the **current** user's own records.

### Example user scenarios — agentic path

**A. Course registration**

> **Student:** "Register me for CS101"

- Agent recognizes an action request → calls `register_course(action="register", course_code="CS101")`.
- Tool finds the student via `find_student`, looks up `education.course` by
  code (case-insensitive), and `create`s an `education.registration`.
- If the course is full, the model's validation raises an `OdooError`
  ("course is full") → tool returns `ok: false` with that message → Gemini's
  follow-up turn explains this and offers to file a petition.
- On success: "You're registered for Introduction to Computer Science (CS101), 3 credits."

**B. Petition with status follow-up (multi-turn)**

> **Student:** "I want to appeal my grade in CS101, I think it was graded incorrectly."

- Agent calls `create_petition(action="submit", petition_type="grade_appeal", subject=..., description=..., course_code="CS101")`.
- A `student.petition` record is created and submitted; the reply includes
  a reference like `SP00001`.

> **Student (later):** "What's the status of SP00001?"

- Agent calls `create_petition(action="check_status", reference="SP00001")`,
  returning the current state (e.g. "under review").

**C. Hybrid information + action**

> **Student:** "Why can't I register for anything? Also what's the add/drop deadline?"

- The action part (`check_holds`) is handled by the tool call (one tool per
  turn — the model prioritizes the action).
- If the student is on hold, the reply explains the hold and reason; the
  add/drop-deadline question would need a separate follow-up turn, which
  would then be answered from RAG context (§2) since no further action is
  implied.

**D. GPA what-if (no Odoo data needed)**

> **Student:** "If I get an A in CS201 (3 credits) and a B+ in MA205 (4 credits), and my current GPA is 3.2 over 60 credits, what would my new GPA be?"

- Agent calls `gpa_calculator(courses=[...], current_gpa=3.2, current_credits=60)`.
- Pure computation, returns an estimated cumulative GPA — explicitly framed
  as an estimate, not an official record.

**E. Unofficial transcript**

> **Student:** "Can I see my transcript?"

- Agent calls `student_records(action="transcript")`.
- Tool fetches `education.registration` rows for the student, joins
  `education.course` for code/name/credits/semester/year, groups by term, and
  returns an "unofficial enrollment summary" (no grades) with a pointer to
  the Registrar's Office for an official transcript.

---

## 4. Error handling & resilience

- **`odoo_client.py`**: `OdooError` (business/validation, safe to show) vs
  `OdooConnectionError` (Odoo unreachable/auth failure — never show raw
  details). XML-RPC faults are cleaned via `_clean_fault()` to strip
  tracebacks down to the relevant message.
- **`agent_tools.py`**: every tool catches `OdooError` at its Odoo calls and
  returns `{"ok": False, "message": ...}` — connection errors get
  `SYSTEM_DOWN_MSG`, business errors get the cleaned message.
- **`agent.py`**: both Gemini round-trips (`send_message` for the initial
  prompt and for the function response) are wrapped in `try/except`; any
  tool exception is caught and converted to a fallback message. All
  exceptions are logged server-side via `print()`.
- **`main.py`**: the entire `run_agent()` call is wrapped in `try/except` so
  `/ask` never 500s due to an LLM or Odoo failure — the user gets a generic
  "try again shortly" message.

This layering means a down Odoo instance, a Gemini API error, or an
unexpected tool exception degrades gracefully to a polite message rather than
breaking the chat.
