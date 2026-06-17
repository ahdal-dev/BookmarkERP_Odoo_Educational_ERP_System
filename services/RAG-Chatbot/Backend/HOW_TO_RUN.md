# How to Run the RAG Chatbot & Agentic Chatbot

This guide covers running the combined `/ask` service — the **RAG chatbot**
(answers from uploaded documents) and the **agentic chatbot** (real actions
against the Odoo Educational ERP). Both are served by the same FastAPI app
(`Backend/main.py`); see [ARCHITECTURE.md](ARCHITECTURE.md) and
[WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) for how they work internally.

---

## 1. Prerequisites

| Requirement | Needed for | Notes |
|---|---|---|
| Python 3.10+ | both | on PATH |
| PostgreSQL + `pgvector` extension | RAG (document storage/search) | `CREATE EXTENSION IF NOT EXISTS vector;` |
| Google Gemini API key | both | classification, rewriting, judging, embeddings, and agent function-calling — get one at [Google AI Studio](https://aistudio.google.com/) |
| Running Odoo instance with the Educational ERP addons | agentic only | `education.*`, `op.admission*`, `student.petition`, `petition.type`, `res.users` hold fields |
| (Optional) SMTP credentials | admin/user emails | if unset, emails are printed to console instead |

---

## 2. Configure environment variables

The app loads `services/RAG-Chatbot/.env` (one level above `Backend/`). Copy
the template and fill it in:

```bash
cd services/RAG-Chatbot
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
```

The current `.env.example` only ships the **Odoo** variables (added for the
agentic tools). Make sure your `.env` also includes the **RAG/core**
variables — add these manually if missing:

```env
# --- Core (RAG chatbot) ---
DATABASE_URL=postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/mydb
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash       # optional, this is the default

# --- Optional: tunes RAG retrieval ---
RAG_TOP_K=40            # how many chunks to retrieve from pgvector
RAG_LLM_SNIPPETS=8      # how many of those are sent to the LLM as context

# --- Optional: SMTP for admin/user invite emails ---
SMTP_HOST=...
SMTP_PORT=...
SMTP_USER=...
SMTP_PASSWORD=...

# --- Whisper STT ---
WHISPER_MODEL=small     # tiny|base|small|medium|large
WHISPER_DEVICE=cpu      # or cuda

# --- Agentic chatbot: Odoo connection ---
ODOO_URL=http://localhost:8081
ODOO_DB=edu_demo_new
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

> Without `DATABASE_URL` / `GEMINI_API_KEY`, the app won't start or every
> `/ask` call will fail. Without a reachable `ODOO_*` instance, the RAG
> chatbot still works fine — agentic tool calls will just return a
> "having trouble accessing the student records system" message
> (`SYSTEM_DOWN_MSG`), handled gracefully.

---

## 3. Install dependencies

### Option A — Makefile (from `services/RAG-Chatbot/`)
```bash
make install
```

### Option B — manual
```bash
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Unix/macOS:
source venv/bin/activate

pip install --upgrade pip
pip install -r Backend/requirements.txt
```

---

## 4. Initialize the database & create a super-admin

```bash
make db-init
make superadmin USERNAME=admin PASSWORD=password123
```

or manually:
```bash
cd Backend
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
python setup_super_admin.py admin password123
```

---

## 5. Run the server

```bash
make run
```

or manually:
```bash
cd Backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The first run also loads the Whisper STT model (`WHISPER_MODEL`), which can
take a moment.

---

## 6. Set up Odoo for the agentic chatbot (one-time)

The agentic tools talk to Odoo over XML-RPC using the credentials in
`ODOO_*`. To exercise them end-to-end:

1. Start your Odoo instance (`ODOO_URL`, default `http://localhost:8081`)
   with database `ODOO_DB` (default `edu_demo_new`) and the Educational ERP
   addons installed (`edu_mangment`, `open_edu_cat/*`).
2. Ensure `petition.type` demo data is loaded (module `edu_mang_petition` —
   upgrade the module if it was installed before the seed data was added).
3. **Link a chatbot user to an Odoo student**: the agentic tools match the
   logged-in chatbot user's `User.email` to an Odoo `res.users.login`. Create
   (or pick) an Odoo user whose login email matches a chatbot user's email,
   and make sure that Odoo user has a linked `op.student`/`res.partner`
   record with course registrations, etc., for realistic testing.

---

## 7. Using the chatbots

### 7.1 First-time platform setup (one-time, via UI)

1. Open [http://localhost:8000/login](http://localhost:8000/login) and log
   in as **Super-Admin** (created in step 4).
2. Create an **Organization** and an **Org Admin** user for it.
3. Log in as the Org Admin, set a permanent password, then:
   - Create regular **Users** (their `email` must match an Odoo
     `res.users.login` to use agentic features).
   - Go to **Documents** and upload reference files (PDF/DOCX/TXT/CSV) — these
     get chunked and embedded for the RAG chatbot.
4. Log in as a regular **User** to start chatting.

### 7.2 RAG chatbot — informational questions

Ask anything covered by the uploaded documents, e.g.:
- "What is the late-drop policy?"
- "What documents do I need for admission?"

The bot answers strictly from the org's documents and appends a
`Sources:` list of the source filenames. If nothing relevant was uploaded, it
replies that it doesn't have that information.

### 7.3 Agentic chatbot — real ERP actions

Ask for an action and the bot will call the matching tool against Odoo:

| Try asking | Tool called |
|---|---|
| "What's the schedule for CS101?" | `course_info` |
| "Register me for CS101" / "Drop CS101" / "What am I registered for?" | `register_course` |
| "I want to file a grade appeal for CS101 because..." | `create_petition` (submit) |
| "What's the status of SP00001?" | `create_petition` (check_status) |
| "Do I have any holds on my account?" | `check_holds` |
| "Show my enrolled courses" / "Can I see my transcript?" | `student_records` |
| "I want to apply for admission to ..." | `admission_application` |
| "If I get an A in CS201 (3 credits)... what's my GPA?" | `gpa_calculator` |

If the chatbot user's email isn't linked to an Odoo `res.users` record, these
tools reply with a "no student profile linked to your account" message
instead of failing silently.

---

## 8. Verifying everything works

```bash
make test          # DB connectivity + model registration checks
```

Then via the UI or `POST /ask` (see Swagger UI at
[http://localhost:8000/docs](http://localhost:8000/docs)):

- "hi" → greeting only, no retrieval/tools.
- A document-backed question → RAG answer + `Sources:`.
- "Show my enrolled courses" → agentic `student_records` call (requires Odoo
  reachable and the user's email linked to a student).

---

## 9. Troubleshooting

| Symptom | Likely cause |
|---|---|
| `/ask` always returns "ran into a problem" | `GEMINI_API_KEY` missing/invalid, or Gemini quota exceeded |
| RAG answers always "I don't have that information" | no documents uploaded for the org, or `RAG_TOP_K`/embeddings mismatch |
| Agentic replies always say the records system is unreachable | Odoo not running, wrong `ODOO_URL`/`ODOO_DB`, or bad `ODOO_USERNAME`/`ODOO_PASSWORD` |
| Agentic replies say "no student profile linked to your account" | chatbot user's `email` doesn't match any Odoo `res.users.login` |
| Petition submission fails with "Petition types are not configured yet" | `edu_mang_petition`'s `petition_type_data.xml` seed data not loaded — upgrade the module |
| STT (`/stt`) errors on startup | Whisper model failed to download/load — check `WHISPER_MODEL`/`WHISPER_DEVICE` and network access |
