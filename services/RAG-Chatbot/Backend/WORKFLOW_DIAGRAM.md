# Chatbot Workflow Diagrams

Companion diagrams for [ARCHITECTURE.md](ARCHITECTURE.md). Rendered with
Mermaid (supported natively in GitHub/VS Code markdown preview).

---

## 1. Overall `/ask` request flow

```mermaid
flowchart TD
    A[POST /ask] --> B[Validate user, org, chat]
    B --> C[classify_message_llm]
    C -->|greeting_only| D[Reply with greeting<br/>no retrieval, no sources]
    D --> Z1[Persist user + assistant message]
    Z1 --> R1[Return answer]

    C -->|needs_answer| E[Load last 8 chat messages]
    E --> F[rewrite_query_with_history<br/>resolve pronouns -> standalone query]
    F --> G[embed_query + pgvector search<br/>document_chunks, top RAG_TOP_K]
    G --> H[Keep top RAG_LLM_SNIPPETS as context]
    H --> I[run_agent question, snippets, history, student_email]

    I --> J{tool_used?}
    J -->|No - informational| K[judge_answer_llm]
    K -->|answerable| L[Append Sources: filenames]
    K -->|unknown| M[No sources attached]
    L --> Z2[Persist user + assistant message]
    M --> Z2
    Z2 --> R2[Return answer + sources]

    J -->|Yes - action| N[Agentic tool flow<br/>see diagram 3]
    N --> Z3[Persist user + assistant message<br/>no sources]
    Z3 --> R3[Return answer]
```

---

## 2. RAG path (informational questions)

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI /ask
    participant LLM as Gemini (llm.py)
    participant DB as Postgres + pgvector
    participant AG as run_agent (agent.py)

    U->>API: "What's the late-drop policy?"
    API->>LLM: classify_message_llm()
    LLM-->>API: intent = needs_answer
    API->>API: load last 8 messages
    API->>LLM: rewrite_query_with_history()
    LLM-->>API: standalone query
    API->>LLM: embed_query(standalone query)
    LLM-->>API: query vector
    API->>DB: similarity search (top RAG_TOP_K)
    DB-->>API: ranked chunks + filenames
    API->>AG: run_agent(question, top-8 snippets, history, email)
    AG->>LLM: send_message (with tools + system prompt)
    LLM-->>AG: plain text answer (no function_call)
    AG-->>API: {answer, tool_used: null}
    API->>LLM: judge_answer_llm(question, snippets, answer)
    LLM-->>API: status = answerable
    API->>API: append "Sources: <filenames>"
    API->>DB: persist user + assistant messages (with citations)
    API-->>U: answer + sources
```

---

## 3. Agentic path (real ERP actions)

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI /ask
    participant AG as run_agent (agent.py)
    participant GEM as Gemini (function-calling)
    participant TOOL as agent_tools.py
    participant ODOO as Odoo (XML-RPC)

    U->>API: "Register me for CS101"
    API->>AG: run_agent(question, snippets, history, email)
    AG->>GEM: send_message (TOOL_DECLARATIONS + AGENT_SYSTEM_PROMPT)
    GEM-->>AG: function_call: register_course(action=register, course_code=CS101)

    AG->>TOOL: TOOL_DISPATCH["register_course"](args, student_email)
    TOOL->>ODOO: find_student(email) via res.users
    ODOO-->>TOOL: student record (id, partner_id)
    TOOL->>ODOO: search_read education.course (code ilike CS101)
    ODOO-->>TOOL: course record
    TOOL->>ODOO: execute_kw education.registration.create(...)

    alt success
        ODOO-->>TOOL: new registration id
        TOOL-->>AG: {ok: true, message: "You're registered for ..."}
    else OdooError (e.g. course full / on hold)
        ODOO-->>TOOL: ValidationError (cleaned)
        TOOL-->>AG: {ok: false, message: "<reason>"}
    else OdooConnectionError
        ODOO-->>TOOL: connection failure
        TOOL-->>AG: {ok: false, message: SYSTEM_DOWN_MSG}
    end

    AG->>GEM: send_message (FunctionResponse with tool result)
    GEM-->>AG: final natural-language reply
    AG-->>API: {answer, tool_used: "register_course", tool_ok}
    API->>API: persist messages (no sources/citations)
    API-->>U: final reply
```

---

## 4. Tool decision matrix (inside `run_agent`)

```mermaid
flowchart LR
    Q[User message + context snippets] --> M[Gemini w/ TOOL_DECLARATIONS]
    M --> D{Response type}
    D -->|plain text| T1[Return as RAG answer<br/>tool_used = null]
    D -->|function_call| D2{tool name}

    D2 -->|course_info| T2[education.course lookup]
    D2 -->|register_course| T3[education.registration<br/>register / drop / status]
    D2 -->|create_petition| T4[student.petition<br/>submit / check_status]
    D2 -->|check_holds| T5[res.users hold flags]
    D2 -->|student_records| T6[education.registration<br/>enrollment_verify / transcript]
    D2 -->|admission_application| T7[op.admission<br/>start / submit / check_status]
    D2 -->|gpa_calculator| T8[pure computation<br/>no Odoo call]

    T2 --> F[Tool result -> FunctionResponse -> Gemini]
    T3 --> F
    T4 --> F
    T5 --> F
    T6 --> F
    T7 --> F
    T8 --> F
    F --> O[Final natural-language answer]
```
