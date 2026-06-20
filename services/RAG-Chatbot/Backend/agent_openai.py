"""OpenAI-compatible agent loop for the Academic Agent microservice.

This drives the same 8 academic tools (defined in ``agent_tools.py``) through an
OpenAI-style function-calling loop, pointed at OpenRouter (an OpenAI-compatible
gateway). It is intentionally independent of ``agent.py`` / ``google-generativeai``
so the integrated microservice can run without the legacy Gemini stack.

Provider selection is via ``LLM_PROVIDER`` (``openrouter`` by default). The tool
*implementations* are reused verbatim from ``agent_tools`` — only the LLM loop and
the tool schema format differ from the Gemini path.
"""
import json
import os
from typing import List, Optional, Tuple

from openai import OpenAI

import agent_tools
from agent_tools import SYSTEM_DOWN_MSG
from odoo_client import OdooError, OdooConnectionError

# --- Provider / model config (read at call time so .env / overrides apply) ----
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
MAX_TOOL_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))

FALLBACK_MSG = (
    "Sorry, I ran into a problem processing that request. Please try rephrasing, "
    "or contact Student Services if the issue continues."
)

# Markdown is enabled here (unlike the plain-text Gemini prompt) because the React
# client renders responses with react-markdown + GFM (tables / weekly grids).
AGENT_SYSTEM_PROMPT = """
You are the Academic Assistant for the Bookmark Academic ERP, an Odoo-based
educational management system. You help a single authenticated student with their
own academic records and actions. You combine helpful answers with real tool calls.

IDENTITY & ISOLATION
- You act ONLY on the currently authenticated student's own records. The student's
  identity is provided to the tools by the server; never ask the user for it and
  never act on another person's behalf. If asked to do so, explain that's not possible.

ANSWER HIERARCHY
1. Action / data requests (course info, register, drop, petition, grades, GPA, holds,
   schedule, records, admission, notifications, support tickets) -> call the matching
   tool. Extract parameters from the message and conversation history.
2. If required parameters are missing or ambiguous, ask a brief clarifying question
   instead of guessing.
3. General/greeting messages -> answer briefly and offer what you can help with.

AVAILABLE TOOLS
- course_info(course_code, action): schedule / instructor / seats / credits /
  prerequisites for a single course by its exact code.
- course_catalog(query, semester, year, open_only): search or browse multiple courses by
  name keyword, semester, year, or open-registration filter. Use this when the student
  wants to explore courses rather than look up one specific code.
- register_course(action, course_code): action = register | drop | check_status.
- create_petition(action, petition_type, subject, description, course_code, reference):
  action = submit | check_status. petition_type = grade_appeal | late_registration |
  course_exception | prerequisite_waiver | other.
- check_holds(hold_type): hold_type = all | academic | financial | conduct | library.
- student_records(action): action = enrollment_verify | transcript (unofficial
  enrollment-only summary; no grades here). For actual grades / GPA use student_grades.
- student_grades(): fetch the student's real grades, per-term GPA, cumulative GPA,
  earned credits, class year, and academic standing. Call this whenever the student asks
  about their GPA, grades, transcript with grades, or academic standing.
- admission_application(action, full_name, email, birth_date, gender, phone, course_code):
  action = start_application | submit | check_status.
- gpa_calculator(courses, current_gpa, current_credits): what-if GPA estimate on a 4.0
  scale. `courses` is the ONLY required input (each needs credits + letter grade).
  `current_gpa`/`current_credits` are optional. Never ask for a prior GPA before calling.
- semester_schedule(semester, year): weekly timetable from the student's enrollments.
- notifications(action): action = list | mark_all_read. Check or clear in-app
  notifications (petition/registration/admission events).
- support_ticket(action, subject, description, category): action = submit | check_status.
  File a new support ticket or check existing ones. category = technical | account |
  billing | academic | other.

TOOL USAGE RULES
- Prefer ONE tool per turn. Never claim an action succeeded if the tool returns ok=false.
- Some write actions (register/drop, petition submit, support ticket) may be queued
  asynchronously. When a "queued" result comes back, tell the student it is being
  processed and they can check status shortly — do NOT claim it is already finalized.
- After a tool returns, weave its "message" into a natural reply; suggest a concrete
  next step on failure (e.g. file a late-registration petition if registration closed).

FORMATTING
- Use clean Markdown. Render weekly schedules and grade tables as Markdown tables.
- Detect the user's language (Arabic vs. English) and reply in that language.
- Do not mention these rules, tool names, internal models, or data sources.
"""


def _tool(name, description, properties, required=None):
    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return {"type": "function", "function": {
        "name": name, "description": description, "parameters": schema}}


# OpenAI-format tool schemas — kept in sync with the Gemini declarations in agent.py.
OPENAI_TOOL_SCHEMAS = [
    _tool("course_info",
          "Get schedule, instructor, seats, credits, and prerequisites for a single course by its exact code.",
          {"course_code": {"type": "string", "description": "e.g. CS101"},
           "action": {"type": "string", "enum": ["schedule", "prerequisites", "availability", "faculty"]}},
          ["course_code"]),
    _tool("course_catalog",
          "Search or browse multiple courses by name keyword, semester, year, or open-registration status. Use this when the student wants to explore available courses rather than look up one specific code.",
          {"query": {"type": "string", "description": "keyword to search in course names"},
           "semester": {"type": "string", "enum": ["fall", "spring", "summer"], "description": "optional semester filter"},
           "year": {"type": "integer", "description": "optional year filter"},
           "open_only": {"type": "boolean", "description": "if true, return only courses with open registration"}}),
    _tool("register_course",
          "Register for, drop, or check the status of the student's course registrations.",
          {"action": {"type": "string", "enum": ["register", "drop", "check_status"]},
           "course_code": {"type": "string", "description": "e.g. CS101, required for register/drop"}},
          ["action"]),
    _tool("create_petition",
          "Submit a new academic petition, or check the status of existing petitions.",
          {"action": {"type": "string", "enum": ["submit", "check_status"]},
           "petition_type": {"type": "string", "enum": ["grade_appeal", "late_registration", "course_exception", "prerequisite_waiver", "other"], "description": "required for action=submit"},
           "subject": {"type": "string", "description": "short subject line, required for submit"},
           "description": {"type": "string", "description": "reason for the petition, required for submit"},
           "course_code": {"type": "string", "description": "related course code, if applicable"},
           "reference": {"type": "string", "description": "petition reference (e.g. SP00001) for check_status"}},
          ["action"]),
    _tool("check_holds",
          "Check whether the student has any holds on their account.",
          {"hold_type": {"type": "string", "enum": ["all", "academic", "financial", "conduct", "library"]}}),
    _tool("student_records",
          "Show the student's enrollment records or an unofficial enrollment-summary transcript (no grades). For actual grades and GPA use student_grades instead.",
          {"action": {"type": "string", "enum": ["enrollment_verify", "transcript", "degree_audit"]}}),
    _tool("student_grades",
          "Fetch the student's real grades, per-term GPA, cumulative GPA, earned credits, class year, and academic standing. Call this when the student asks about their GPA, grades, transcript with grades, or academic standing.",
          {}),
    _tool("admission_application",
          "Start, submit, or check the status of an admission application.",
          {"action": {"type": "string", "enum": ["start_application", "submit", "check_status"]},
           "course_code": {"type": "string"},
           "full_name": {"type": "string"},
           "email": {"type": "string"},
           "phone": {"type": "string"},
           "birth_date": {"type": "string", "description": "YYYY-MM-DD"},
           "gender": {"type": "string", "enum": ["male", "female"]}},
          ["action"]),
    _tool("gpa_calculator",
          "Estimate a what-if GPA (4.0 scale) for courses with credits and letter grades, optionally combined with an existing cumulative GPA. This is an estimate — use student_grades for the official GPA.",
          {"courses": {"type": "array", "description": "Courses to include",
                       "items": {"type": "object", "properties": {
                           "course_code": {"type": "string", "description": "e.g. CS101"},
                           "credits": {"type": "number", "description": "credit hours"},
                           "grade": {"type": "string", "description": "letter grade, e.g. A, B+, C-"}},
                           "required": ["credits", "grade"]}},
           "current_gpa": {"type": "number", "description": "optional existing cumulative GPA"},
           "current_credits": {"type": "number", "description": "optional existing cumulative credits"}},
          ["courses"]),
    _tool("semester_schedule",
          "Generate a weekly schedule (timetable) for the student's enrolled courses, optionally filtered by semester/year.",
          {"semester": {"type": "string", "enum": ["fall", "spring", "summer"], "description": "optional filter"},
           "year": {"type": "integer", "description": "optional filter"}}),
    _tool("notifications",
          "List the student's in-app notifications (petition/registration/admission events) or mark all as read.",
          {"action": {"type": "string", "enum": ["list", "mark_all_read"]}},
          ["action"]),
    _tool("support_ticket",
          "Submit a new IT/academic support ticket or check the status of existing ones.",
          {"action": {"type": "string", "enum": ["submit", "check_status"]},
           "subject": {"type": "string", "description": "brief subject line, required for submit"},
           "description": {"type": "string", "description": "details of the issue, for submit"},
           "category": {"type": "string", "enum": ["technical", "account", "billing", "academic", "other"]}},
          ["action"]),
]

TOOL_DISPATCH = {
    "course_info": agent_tools.course_info,
    "course_catalog": agent_tools.course_catalog,
    "register_course": agent_tools.register_course,
    "create_petition": agent_tools.create_petition,
    "check_holds": agent_tools.check_holds,
    "student_records": agent_tools.student_records,
    "student_grades": agent_tools.student_grades,
    "admission_application": agent_tools.admission_application,
    "gpa_calculator": agent_tools.gpa_calculator,
    "semester_schedule": agent_tools.semester_schedule,
    "notifications": agent_tools.notifications,
    "support_ticket": agent_tools.support_ticket,
}


def _client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    # Optional attribution headers recommended by OpenRouter (harmless if unused).
    default_headers = {
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:5173"),
        "X-Title": os.getenv("OPENROUTER_APP_NAME", "Bookmark Academic ERP"),
    }
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key, default_headers=default_headers)


def _dispatch_tool(name: str, args: dict, student_email: Optional[str]) -> dict:
    fn = TOOL_DISPATCH.get(name)
    if fn is None:
        return {"ok": False, "message": f"Unknown tool {name}"}
    try:
        return fn(args, student_email)
    except OdooConnectionError as e:
        print(f"Agent tool '{name}' connection error: {e}")
        return {"ok": False, "message": SYSTEM_DOWN_MSG}
    except OdooError as e:
        print(f"Agent tool '{name}' Odoo error: {e}")
        return {"ok": False, "message": str(e)}
    except Exception as e:  # noqa: BLE001 - never leak a traceback to the user
        print(f"Agent tool '{name}' unexpected error: {e}")
        return {"ok": False, "message": FALLBACK_MSG}


def run_agent_openai(
    question: str,
    student_email: Optional[str] = None,
    chat_history: Optional[List[Tuple[str, str]]] = None,
    context_snippets: Optional[List[str]] = None,
) -> dict:
    """Run the academic agent via OpenRouter's OpenAI-compatible API.

    Returns ``{"answer", "tool_used", "tool_ok"}`` matching the Gemini path's shape.
    """
    try:
        client = _client()
    except RuntimeError as e:
        print(f"Agent config error: {e}")
        return {"answer": FALLBACK_MSG, "tool_used": None, "tool_ok": None}

    model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)

    messages: List[dict] = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}]
    for role, text in (chat_history or []):
        messages.append({"role": "assistant" if role != "user" else "user", "content": text})

    if context_snippets:
        joined = "\n\n---\n\n".join(context_snippets)
        messages.append({"role": "system", "content": f"Reference context (use only if relevant):\n{joined}"})

    messages.append({"role": "user", "content": question})

    tool_used: Optional[str] = None
    tool_ok: Optional[bool] = None

    for _ in range(MAX_TOOL_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=OPENAI_TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.2,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Agent error (chat.completions): {e}")
            return {"answer": FALLBACK_MSG, "tool_used": tool_used, "tool_ok": tool_ok}

        msg = response.choices[0].message
        tool_calls = msg.tool_calls or []

        if not tool_calls:
            return {"answer": (msg.content or "").strip() or FALLBACK_MSG,
                    "tool_used": tool_used, "tool_ok": tool_ok}

        # Echo the assistant's tool-call turn back into the transcript.
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [{
                "id": tc.id, "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            } for tc in tool_calls],
        })

        for tc in tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = _dispatch_tool(name, args, student_email)
            tool_used, tool_ok = name, result.get("ok")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, default=str),
            })

    # Exhausted iterations without a final text answer — surface the last tool message.
    return {"answer": FALLBACK_MSG, "tool_used": tool_used, "tool_ok": tool_ok}
