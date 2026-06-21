"""
LLM-powered recommendation refinement via OpenRouter.
Falls back to rule-based recommendations if the API key is missing or the call fails.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b:free"


def _build_prompt(pred: dict) -> str:
    r    = pred
    reas = r.get("reasoning", {})
    pa   = r.get("plan_analysis", {})

    flags     = r.get("flags", [])
    flags_str = ", ".join(flags) if flags else "none"

    courses = r.get("_study_plan_courses", [])
    courses_str = ", ".join(
        c["course_id"] + (f" ({c['title']})" if c.get("title") else "")
        for c in courses
    ) if courses else "not specified"

    return f"""You are a friendly academic advisor. A student is planning their next semester. Give them 3 short, specific tips to help them succeed.

Student's plan:
- Registered courses: {courses_str}
- Total credits: {reas.get('plan_credit_load')} — {pa.get('load_assessment')}
- Course difficulty: {pa.get('difficulty_note')}
- Plan fits past strengths: {pa.get('strength_alignment')}
- Credits in subjects they historically struggle with: {pa.get('credits_in_weak_subjects')}
- Courses they previously got a low grade in (retaking): {pa.get('repeated_difficult_courses')}
- Courses in brand-new subject areas: {pa.get('new_subject_courses')}

Student background:
- Cumulative GPA: {reas.get('cumulative_gpa')} | Last term GPA: {reas.get('last_term_gpa')} | Trend: {r.get('trajectory')}
- Predicted next GPA: {r.get('predicted_gpa')} | Risk level: {r.get('risk_level')}
- Warning signals: {flags_str}

Rules:
- Write exactly 3 tips, each starting with "•"
- Mention specific course IDs where relevant (e.g. "For CSAI 351, start the assignments early")
- Use plain, friendly language — no jargon
- Each tip is one sentence, max 25 words
- No intro, no conclusion, no headers — just the 3 bullets
"""


def refine_recommendations(pred: dict) -> Optional[list[str]]:
    """
    Call OpenRouter to refine recommendations with course-specific advice.
    Returns a list of strings, or None if unavailable (fallback to rule-based).
    """
    if not OPENROUTER_API_KEY:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "user", "content": _build_prompt(pred)},
            ],
            max_tokens=400,
            temperature=0.4,
            extra_headers={
                "HTTP-Referer": "https://github.com/ZiadMAlsawy/Odoo_Educational_ERP_System",
                "X-Title": "Student Performance Advisor",
            },
        )

        text = response.choices[0].message.content.strip()
        bullets = [
            line.lstrip("•- ").strip()
            for line in text.splitlines()
            if line.strip().startswith("•") or line.strip().startswith("-")
        ]
        return bullets if bullets else [text]

    except Exception as exc:
        logger.warning("LLM advisor failed, using rule-based fallback: %s", exc)
        return None
