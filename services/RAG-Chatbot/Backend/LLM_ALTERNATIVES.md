# Switching Away from Gemini — Free LLM Alternatives & Config Steps

This service currently depends on Gemini in two places:

- **`llm.py`** — `google.generativeai` (`genai.configure`, `genai.GenerativeModel`)
  for classification, query rewriting, judging, and embeddings (`embed_query`
  in `ingestion.py`).
- **`agent.py`** — `google.ai.generativelanguage` (`glm.Tool`,
  `glm.FunctionDeclaration`, `glm.Schema`, `glm.FunctionResponse`) for
  Gemini-specific function-calling.

Any replacement needs to cover **both** the plain-text LLM calls and the
**function-calling (tool use)** format used by the agentic flow, plus
**embeddings** for the RAG vector search. This doc lists config steps per
provider and what would need to change in code (at a high level — no code has
been changed yet).

---

## 0. Common groundwork (applies to every option below)

Most non-Gemini providers expose an **OpenAI-compatible** API, so the
simplest migration path is:

```bash
pip install openai
```

And centralize provider config via env vars (add to `.env`):

```
LLM_PROVIDER=groq            # groq | ollama | openrouter | mistral
LLM_API_KEY=...
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_PROVIDER=...        # see §5
EMBEDDING_MODEL=...
```

Code-level changes common to all OpenAI-compatible providers:

- `llm.py`: replace `genai.configure()` / `genai.GenerativeModel(...).generate_content(prompt)`
  with `OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY).chat.completions.create(model=LLM_MODEL, messages=[...])`.
- `agent.py`: replace `glm.Tool`/`glm.FunctionDeclaration`/`glm.Schema` with
  plain JSON-schema `tools=[{"type": "function", "function": {"name": ..., "parameters": {...}}}]`,
  and read `response.choices[0].message.tool_calls` instead of
  `response.candidates[0].content.parts[0].function_call`.
- `run_agent()`'s follow-up step changes from `glm.Content(parts=[glm.Part(function_response=...)])`
  to appending a `{"role": "tool", "tool_call_id": ..., "content": json.dumps(result)}`
  message to the `messages` list.

---

## 1. Groq (Recommended)

Free tier, very fast inference, OpenAI-compatible, supports tool calling on
Llama 3.1/3.3 and Qwen models.

### Config steps

1. Create a free account at Groq and generate an API key (console → API Keys).
2. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_...
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
3. Install the client (OpenAI SDK works against Groq's endpoint):
   ```bash
   pip install openai
   ```
4. Initialize the client pointed at Groq's base URL:
   ```python
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
   ```
5. Use `client.chat.completions.create(model=GROQ_MODEL, messages=[...], tools=[...])`
   for both the RAG prompts (`llm.py`) and the agentic tool-calling
   (`agent.py`).

### Tradeoffs
- Free tier has request-per-minute / token-per-day limits — fine for dev/demo,
  may need a paid tier for production load.
- No native embeddings endpoint — pair with a separate embedding provider
  (see §5).

---

## 2. Ollama (fully local, fully free)

Run open models (Llama 3.1, Qwen2.5, Mistral, Gemma2) on your own machine —
no API key, no rate limits, but requires local compute (GPU recommended).

### Config steps

1. Install Ollama: https://ollama.com/download (Windows installer).
2. Pull a model with tool-calling support:
   ```bash
   ollama pull llama3.1
   ```
3. Ollama exposes an OpenAI-compatible endpoint at `http://localhost:11434/v1`
   by default — no API key needed (use a placeholder string).
4. Add to `.env`:
   ```
   OLLAMA_BASE_URL=http://localhost:11434/v1
   OLLAMA_MODEL=llama3.1
   ```
5. Initialize the client:
   ```python
   from openai import OpenAI
   client = OpenAI(base_url=os.getenv("OLLAMA_BASE_URL"), api_key="ollama")
   ```
6. Same `chat.completions.create(..., tools=[...])` pattern as Groq.

### Tradeoffs
- Zero ongoing cost and no rate limits, but inference speed/quality depends
  entirely on local hardware — 70B-class models need a serious GPU; smaller
  models (8B) trade off tool-calling reliability.
- The machine running the backend must stay up and have the model loaded
  (extra RAM/VRAM alongside the existing Whisper model).

---

## 3. OpenRouter

Free-tier (`:free` suffixed) models from multiple providers behind one
OpenAI-compatible API.

### Config steps

1. Create an account at OpenRouter and generate an API key.
2. Add to `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-...
   OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct:free
   ```
3. Install/initialize same as Groq, pointed at `https://openrouter.ai/api/v1`:
   ```python
   client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
   ```
4. Same tool-calling JSON-schema format as §0/§1.

### Tradeoffs
- Free models are rate-limited and occasionally rotated/deprecated — pin a
  model and monitor OpenRouter's model list for availability changes.
- Tool-calling support varies by underlying model; verify the chosen
  `:free` model supports `tools` before relying on it for the agentic flow.

---

## 4. Mistral AI (La Plateforme free tier)

Free experimental-tier API key with rate limits, native tool calling on
`mistral-large`/`mistral-small`/`open-mixtral` models.

### Config steps

1. Create an account at Mistral's platform and generate an API key
   (free tier requires opting into data usage for training).
2. Add to `.env`:
   ```
   MISTRAL_API_KEY=...
   MISTRAL_MODEL=mistral-small-latest
   ```
3. Install the official SDK (or use OpenAI-compatible mode):
   ```bash
   pip install mistralai
   ```
   or, OpenAI-compatible:
   ```python
   client = OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1")
   ```
4. Same tool-calling JSON-schema format as §0.

### Tradeoffs
- Free tier rate limits are fairly low (requests/sec); fine for a single-user
  dev/demo, not for concurrent classroom traffic.

---

## 5. Embeddings (`embed_query` in `ingestion.py`)

Gemini's embedding model needs its own replacement regardless of which chat
LLM is chosen above:

| Option | Config | Notes |
|---|---|---|
| **`sentence-transformers`** (local) | `pip install sentence-transformers`; `model = SentenceTransformer("all-MiniLM-L6-v2")` | Free, no API key, runs on CPU; vector dimension (384) differs from Gemini's — requires re-embedding existing `document_chunks` and updating the pgvector column dimension |
| **Ollama `nomic-embed-text`** | `ollama pull nomic-embed-text`; call `POST /api/embeddings` on the same local Ollama server | Free, local, pairs naturally with Ollama chat models; also a different vector dimension than Gemini |
| **Cohere `embed-v3` (free trial)** | `COHERE_API_KEY=...`; `pip install cohere` | Generous free trial credits, strong multilingual embeddings (useful given Arabic/English support) |

**Important:** changing the embedding model/dimension requires
re-ingesting all existing documents (re-chunking + re-embedding) and updating
the `vector(N)` column definition for `document_chunks.embedding` to match
the new model's output dimension.

---

## 6. Suggested migration order (if you proceed)

1. Pick one chat provider (Groq is the easiest drop-in) and one embedding
   provider (sentence-transformers is the simplest, no extra API key).
2. Refactor `llm.py` to a provider-agnostic `chat_completion(messages)`
   helper using the OpenAI SDK against the chosen `base_url`.
3. Refactor `agent.py`'s `TOOL_DECLARATIONS`/`TOOL_DISPATCH` and `run_agent()`
   to OpenAI-style `tools=[...]` + `tool_calls` handling.
4. Update `ingestion.py`'s `embed_query` / chunk-embedding path, re-embed
   existing documents, and migrate the `vector(N)` column dimension.
5. Update `.env.example` with the new provider's env vars and remove
   `GEMINI_API_KEY`/`GEMINI_MODEL` once migration is verified.
