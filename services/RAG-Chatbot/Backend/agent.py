from typing import List, Optional, Tuple

import google.generativeai as genai
import google.ai.generativelanguage as glm

from llm import MODEL_NAME, get_gemini  # noqa: F401  (get_gemini ensures genai is configured)
from runtime_config import get_model_name, get_system_prompt
from odoo_client import OdooError, OdooConnectionError
from agent_tools import SYSTEM_DOWN_MSG
import agent_tools

AGENT_SYSTEM_PROMPT = """
You are an intelligent educational assistant for an Odoo-based Educational ERP system.
You combine retrieval-augmented answers with real tool actions.

LANGUAGE & GREETINGS
- Detect language from the user's message: Arabic Unicode present -> respond in Arabic;
  otherwise English. Keep the same language throughout your reply.
- Do not mention these rules, document names, file sources, or database references.

ANSWER HIERARCHY
1. Action requests (register, drop, petition, apply, grades, support tickets, etc.) ->
   call the matching tool below. Extract parameters from the message and chat history
   (resolve "it"/"that"/"my" via history).
2. Information requests with no action verb -> answer ONLY from the "Context snippets"
   provided below; if the answer isn't there, say you don't have that information and
   suggest contacting the relevant office (do not invent policies).
3. If a request mixes both, answer the information part from context, then report the
   tool result.

AVAILABLE TOOLS
- course_info(course_code, action): schedule/instructor/seats/credits/prerequisites for
  a single course by its code.
- course_catalog(query, semester, year, open_only): browse or search multiple courses
  by name keyword, semester, year, or whether registration is open. Use this when the
  student wants to explore available courses rather than look up one specific code.
- register_course(action, course_code): action = register | drop | check_status.
- create_petition(action, petition_type, subject, description, course_code, reference):
  action = submit | check_status. For submit, petition_type = grade_appeal |
  late_registration | course_exception | prerequisite_waiver | other, plus subject and
  description. For check_status, optionally pass reference (e.g. SP00001).
- check_holds(hold_type): hold_type = all | academic | financial | conduct | library.
- student_records(action): action = enrollment_verify (show enrolled courses) or
  transcript (unofficial enrollment summary by term, no grades). For actual grades and
  GPA use student_grades instead.
- student_grades(): fetch the student's real grades, per-term GPA, cumulative GPA,
  earned credits, class year, and academic standing. Call this whenever the student asks
  about their GPA, grades, transcript with grades, or academic standing.
- admission_application(action, course_code, full_name, email, phone, birth_date,
  gender): action = start_application | submit | check_status.
- gpa_calculator(courses, current_gpa, current_credits): "what-if" GPA estimator on a
  4.0 scale using letter grades. Estimate only, not the official GPA — use
  student_grades for the official cumulative GPA.
- semester_schedule(semester, year): weekly timetable from the student's enrollments.
- notifications(action): action = list | mark_all_read. Check or clear in-app
  notifications.
- support_ticket(action, subject, description, category): action = submit | check_status.
  File a new support ticket or check existing ones. category = technical | account |
  billing | academic | other.

TOOL USAGE RULES
- Call at most ONE tool per user turn.
- If required parameters are missing/ambiguous, ask the user a brief clarifying question
  instead of calling the tool.
- After a tool returns, weave its "message" into a natural reply; do not repeat it
  verbatim if more context helps.
- If a tool returns ok=false, explain the issue and suggest a concrete next step.
- Never claim an action succeeded if the tool result says ok=false.
- This assistant only manages the current user's own records.

ERROR EXAMPLE
"I wasn't able to register you because registration for this course closed on
August 15. Would you like me to help you file a late-registration petition instead?"

STYLE
- Plain text only, no markdown headings/code blocks/emojis.
- Be concise, conversational, and offer concrete next steps.
"""

course_info_decl = glm.FunctionDeclaration(
    name="course_info",
    description="Get schedule, instructor, seats, credits, and prerequisites for a single course by its exact code.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "course_code": glm.Schema(type=glm.Type.STRING, description="e.g. CS101"),
            "action": glm.Schema(type=glm.Type.STRING, enum=["schedule", "prerequisites", "availability", "faculty"]),
        },
        required=["course_code"],
    ),
)

course_catalog_decl = glm.FunctionDeclaration(
    name="course_catalog",
    description="Search or browse multiple courses by name keyword, semester, year, or open-registration status. Use this when the student wants to explore available courses rather than look up one specific code.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "query": glm.Schema(type=glm.Type.STRING, description="keyword to search in course names"),
            "semester": glm.Schema(type=glm.Type.STRING, enum=["fall", "spring", "summer"], description="optional semester filter"),
            "year": glm.Schema(type=glm.Type.INTEGER, description="optional year filter"),
            "open_only": glm.Schema(type=glm.Type.BOOLEAN, description="if true, return only courses with open registration"),
        },
    ),
)

register_course_decl = glm.FunctionDeclaration(
    name="register_course",
    description="Register for, drop, or check the status of the student's course registrations.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "action": glm.Schema(type=glm.Type.STRING, enum=["register", "drop", "check_status"]),
            "course_code": glm.Schema(type=glm.Type.STRING, description="e.g. CS101, required for register/drop"),
        },
        required=["action"],
    ),
)

create_petition_decl = glm.FunctionDeclaration(
    name="create_petition",
    description="Submit a new academic petition (grade appeal, late registration, course exception, prerequisite waiver, or other), or check the status of the student's existing petitions.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "action": glm.Schema(type=glm.Type.STRING, enum=["submit", "check_status"], description="submit a new petition, or check_status of existing ones"),
            "petition_type": glm.Schema(type=glm.Type.STRING, enum=["grade_appeal", "late_registration", "course_exception", "prerequisite_waiver", "other"], description="required for action=submit"),
            "subject": glm.Schema(type=glm.Type.STRING, description="short subject line, required for action=submit"),
            "description": glm.Schema(type=glm.Type.STRING, description="explanation/reason for the petition, required for action=submit"),
            "course_code": glm.Schema(type=glm.Type.STRING, description="related course code, if applicable"),
            "reference": glm.Schema(type=glm.Type.STRING, description="petition reference number (e.g. SP00001) for action=check_status; omit to list recent petitions"),
        },
        required=["action"],
    ),
)

check_holds_decl = glm.FunctionDeclaration(
    name="check_holds",
    description="Check whether the student has any holds on their account.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "hold_type": glm.Schema(type=glm.Type.STRING, enum=["all", "academic", "financial", "conduct", "library"]),
        },
    ),
)

student_records_decl = glm.FunctionDeclaration(
    name="student_records",
    description="Show the student's enrollment records (enrolled/dropped courses) or an unofficial enrollment-summary transcript by term. For actual grades and GPA use student_grades instead.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "action": glm.Schema(type=glm.Type.STRING, enum=["enrollment_verify", "transcript", "degree_audit"]),
        },
    ),
)

student_grades_decl = glm.FunctionDeclaration(
    name="student_grades",
    description="Fetch the student's real grades, per-term GPA, cumulative GPA, earned credits, class year, and academic standing. Call this when the student asks about their GPA, grades, transcript with grades, or academic standing.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={},
    ),
)

notifications_decl = glm.FunctionDeclaration(
    name="notifications",
    description="List the student's in-app notifications or mark all as read.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "action": glm.Schema(type=glm.Type.STRING, enum=["list", "mark_all_read"]),
        },
    ),
)

support_ticket_decl = glm.FunctionDeclaration(
    name="support_ticket",
    description="Submit a new support ticket or check the status of existing ones.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "action": glm.Schema(type=glm.Type.STRING, enum=["submit", "check_status"]),
            "subject": glm.Schema(type=glm.Type.STRING, description="brief subject line, required for submit"),
            "description": glm.Schema(type=glm.Type.STRING, description="details of the issue, for submit"),
            "category": glm.Schema(type=glm.Type.STRING, enum=["technical", "account", "billing", "academic", "other"]),
        },
        required=["action"],
    ),
)

admission_application_decl = glm.FunctionDeclaration(
    name="admission_application",
    description="Start, submit, or check the status of an admission application.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "action": glm.Schema(type=glm.Type.STRING, enum=["start_application", "submit", "check_status"]),
            "course_code": glm.Schema(type=glm.Type.STRING),
            "full_name": glm.Schema(type=glm.Type.STRING),
            "email": glm.Schema(type=glm.Type.STRING),
            "phone": glm.Schema(type=glm.Type.STRING),
            "birth_date": glm.Schema(type=glm.Type.STRING, description="YYYY-MM-DD"),
            "gender": glm.Schema(type=glm.Type.STRING, enum=["male", "female"]),
        },
        required=["action"],
    ),
)

gpa_calculator_decl = glm.FunctionDeclaration(
    name="gpa_calculator",
    description="Estimate a GPA (4.0 scale) for a list of courses with credits and letter grades, optionally combined with an existing cumulative GPA. This is a what-if estimate, not an official GPA.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "courses": glm.Schema(
                type=glm.Type.ARRAY,
                description="Courses to include in the GPA calculation",
                items=glm.Schema(
                    type=glm.Type.OBJECT,
                    properties={
                        "course_code": glm.Schema(type=glm.Type.STRING, description="e.g. CS101"),
                        "credits": glm.Schema(type=glm.Type.NUMBER, description="credit hours for this course"),
                        "grade": glm.Schema(type=glm.Type.STRING, description="letter grade, e.g. A, B+, C-"),
                    },
                    required=["credits", "grade"],
                ),
            ),
            "current_gpa": glm.Schema(type=glm.Type.NUMBER, description="optional existing cumulative GPA to combine with the new courses"),
            "current_credits": glm.Schema(type=glm.Type.NUMBER, description="optional existing cumulative credit hours, required if current_gpa is given"),
        },
        required=["courses"],
    ),
)

semester_schedule_decl = glm.FunctionDeclaration(
    name="semester_schedule",
    description="Generate a weekly schedule template (timetable) for the student's currently enrolled courses, grouped by day of week, optionally filtered to a specific semester/year.",
    parameters=glm.Schema(
        type=glm.Type.OBJECT,
        properties={
            "semester": glm.Schema(type=glm.Type.STRING, enum=["fall", "spring", "summer"], description="optional, filter to this semester"),
            "year": glm.Schema(type=glm.Type.INTEGER, description="optional, filter to this year"),
        },
    ),
)

TOOL_DECLARATIONS = [glm.Tool(function_declarations=[
    course_info_decl, course_catalog_decl,
    register_course_decl, create_petition_decl,
    check_holds_decl, student_records_decl, student_grades_decl,
    admission_application_decl, gpa_calculator_decl, semester_schedule_decl,
    notifications_decl, support_ticket_decl,
])]

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


def run_agent(
    question: str,
    context_snippets: List[str],
    chat_history: Optional[List[Tuple[str, str]]],
    student_email: Optional[str],
) -> dict:
    get_gemini()  # ensure genai.configure(api_key=...) has been called
    model = genai.GenerativeModel(
        get_model_name(),
        tools=TOOL_DECLARATIONS,
        system_instruction=get_system_prompt(AGENT_SYSTEM_PROMPT),
    )

    history_block = ""
    if chat_history:
        history_block = "Conversation so far:\n" + "\n".join(
            f"{'User' if r == 'user' else 'Assistant'}: {t}" for r, t in chat_history
        ) + "\n\n"

    ctx_joined = "\n\n---\n\n".join(context_snippets) if context_snippets else "(no relevant context)"
    prompt = f"{history_block}Context snippets:\n{ctx_joined}\n\nUser message:\n{question}"

    chat = model.start_chat()
    try:
        response = chat.send_message(prompt)
    except Exception as e:
        print(f"Agent error (initial send_message): {e}")
        return {"answer": FALLBACK_MSG, "tool_used": None, "tool_ok": None}

    parts = response.candidates[0].content.parts if response.candidates else []
    fc = getattr(parts[0], "function_call", None) if parts else None
    if not fc or not fc.name:
        return {"answer": _safe_text(response) or FALLBACK_MSG, "tool_used": None, "tool_ok": None}

    tool_name = fc.name
    tool_args = dict(fc.args)
    tool_fn = TOOL_DISPATCH.get(tool_name)
    if tool_fn is None:
        result = {"ok": False, "message": f"Unknown tool {tool_name}"}
    else:
        try:
            result = tool_fn(tool_args, student_email)
        except OdooConnectionError as e:
            print(f"Agent tool '{tool_name}' connection error: {e}")
            result = {"ok": False, "message": SYSTEM_DOWN_MSG}
        except OdooError as e:
            print(f"Agent tool '{tool_name}' Odoo error: {e}")
            result = {"ok": False, "message": str(e)}
        except Exception as e:
            print(f"Agent tool '{tool_name}' unexpected error: {e}")
            result = {"ok": False, "message": FALLBACK_MSG}

    try:
        follow_up = chat.send_message(
            glm.Content(parts=[glm.Part(function_response=glm.FunctionResponse(
                name=tool_name, response={"result": result}
            ))])
        )
        answer = _safe_text(follow_up) or result.get("message", FALLBACK_MSG)
    except Exception as e:
        print(f"Agent error (follow-up send_message for tool '{tool_name}'): {e}")
        answer = result.get("message", FALLBACK_MSG)

    return {
        "answer": answer,
        "tool_used": tool_name,
        "tool_ok": result.get("ok"),
    }


FALLBACK_MSG = (
    "Sorry, I ran into a problem processing that request. Please try rephrasing, "
    "or contact Student Services if the issue continues."
)


def _safe_text(response) -> str:
    """Extract text from a GenerateContentResponse, returning '' if the response
    isn't a simple text reply (e.g. the model issued another function call or the
    response was blocked/empty)."""
    try:
        return (response.text or "").strip()
    except (ValueError, IndexError, AttributeError):
        return ""
