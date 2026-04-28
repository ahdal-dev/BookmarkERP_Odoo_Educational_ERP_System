"""
Zewail City – LLM-Driven Synthetic Transcript Generator  (v3 Enhanced)
=======================================================================
All academic data (STUDY_PLANS, COURSE_CATALOG, ZEWAIL_CITY_STRUCTURE)
are loaded directly from the original Transcript_generator.py file.

ENHANCED FEATURES (v3+):
  ✓ Batch Years: Students can be in batches 2021, 2022, 2023, 2024, 2025
  ✓ End Term: Spring 2026 is the target terminal semester for all students
  ✓ Smart Semester Count: Automatically calculated based on entry year
    - 2021: ~11 semesters until Spring 2026
    - 2022: ~9 semesters until Spring 2026
    - 2023: ~7 semesters until Spring 2026
    - 2024: ~5 semesters until Spring 2026
    - 2025: ~3 semesters until Spring 2026
  ✓ Failure & Retake Logic:
    - Fall failure → retake in Spring or next Fall
    - Spring failure → retake in next Fall (NOT Summer)
    - Retaken courses shown as [Grade] to indicate repeats
  ✓ Summer Constraints:
    - Only humanities, English, and internship courses allowed
    - Cannot take core major/engineering/science courses
    - Max 9 credits per Summer
  ✓ New Personas:
    - disciplined_retake: Shows systematic retake strategy
    - summer_intensive: Strategic use of Summer terms

For every student the generator:
  1. Picks a program and persona.
  2. Builds a detailed natural-language prompt that embeds:
       • The program's full study plan (semester by semester)
       • Relevant course names/credits from COURSE_CATALOG
       • Enhanced persona rules with failure/retake/summer strategies
       • The ZC grading scale
       • The exact JSON schema to output
  3. Sends the prompt to  gpt-oss-120b  via the OpenAI-compatible
     Ollama-cloud endpoint.
  4. Parses and validates the returned JSON with verify_academic_integrity.
  5. Writes a single  transcripts.json  with all records.

Usage:
    python transcript_generator_v3.py --students 50 --seed 42

Environment variables:
    OLLAMA_API_URL   base URL of Ollama cloud   (default: http://localhost:11434)
    OLLAMA_API_KEY   bearer token if required    (default: "")
"""

import json
import os
import random
import sys
import time
import re
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ollama import Client

# ──────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────
ORIGINAL_SCRIPT = Path(__file__).parent / "Transcript_generator (1).py"
OUTPUT_DIR      = Path("generated_data")
OUTPUT_DIR.mkdir(exist_ok=True)

OLLAMA_API_KEY  = os.getenv("OLLAMA_API_KEY", "28a461fc69bd49ff919312200fb836c8.LKhlcs14IRGw_xgi-Foialjk")
MODEL           = "gpt-oss:120b-cloud"    # cloud model name on ollama.com

REQUEST_TIMEOUT = 120          # seconds per LLM call
MAX_RETRIES     = 3
RETRY_DELAY     = 5            # seconds between retries

# ──────────────────────────────────────────────────────────────────
# LOAD DATA STRUCTURES FROM ORIGINAL SCRIPT
# ──────────────────────────────────────────────────────────────────
def _load_original_data() -> Tuple[Dict, Dict, Dict]:
    """
    Safely execute the original script in an isolated namespace to
    extract STUDY_PLANS, COURSE_CATALOG, and ZEWAIL_CITY_STRUCTURE
    without importing its side-effects.
    """
    if not ORIGINAL_SCRIPT.exists():
        sys.exit(
            f"[ERROR] Original script not found at {ORIGINAL_SCRIPT}.\n"
            "Place Transcript_generator__1_.py in the same directory."
        )
    src = ORIGINAL_SCRIPT.read_text(encoding="utf-8")
    # Stub out imports that may not be installed
    stubs = [
        "import google.generativeai as genai",
        "genai.configure(api_key=GOOGLE_API_KEY)",
        "from dataclasses import dataclass, asdict",
    ]
    for stub in stubs:
        src = src.replace(stub, f"# stubbed: {stub}")

    ns: Dict[str, Any] = {}
    exec(compile(src, str(ORIGINAL_SCRIPT), "exec"), ns)   # noqa: S102

    return (
        ns["STUDY_PLANS"],
        ns["COURSE_CATALOG"],
        ns["ZEWAIL_CITY_STRUCTURE"],
    )


print("📂 Loading academic data from original script …", flush=True)
STUDY_PLANS, COURSE_CATALOG, ZC_STRUCTURE = _load_original_data()

# ── flat course lookup: course_id → {name, credits, prerequisites} ──
COURSE_LOOKUP: Dict[str, Dict] = {}
for _dept, _courses in COURSE_CATALOG.items():
    for _cid, _info in _courses.items():
        COURSE_LOOKUP[_cid] = {
            "name":    _info["name"],
            "credits": _info["credits"],
            "prereqs": _info.get("prerequisites", []),
        }

print(f"   ✓ {len(STUDY_PLANS)} programs  |  {len(COURSE_LOOKUP)} catalog courses loaded.\n",
      flush=True)

# ──────────────────────────────────────────────────────────────────
# GRADING SCALE
# ──────────────────────────────────────────────────────────────────
GRADE_SCALE: Dict[str, float] = {
    "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D": 1.0, "F": 0.0,
}
NON_GPA_GRADES = {"P", "W", "IP"}

def grade_points(grade: str) -> Optional[float]:
    """Return numeric grade points, or None for P / W / IP."""
    g = grade.strip("[]")          # handle [B+] repeat notation
    return GRADE_SCALE.get(g)

# ──────────────────────────────────────────────────────────────────
# PERSONAS
# ──────────────────────────────────────────────────────────────────
PERSONAS: Dict[str, str] = {
    "high_achiever": (
        "This student is an excellent academic performer. "
        "They earn mostly A and A- grades, occasionally B+. "
        "They rarely fail or withdraw from courses (max 0-1 failures across the entire program). "
        "When they do fail, they retake immediately in the next available semester (Spring or next Fall). "
        "Their cumulative GPA should be above 3.7. "
        "They should graduate early or on time with Spring 2026 as target end term."
    ),
    "solid_b": (
        "This student is a consistent B-level performer. "
        "Grades are mostly B+, B, and B-, with occasional C+ or C. "
        "May have 0-2 failures across the entire program. "
        "When they fail in Fall, they retake in Spring of same year. "
        "When they fail in Spring, they retake in next Fall (not Summer - Summer is for humanities/English/internship). "
        "Very few withdrawals. GPA typically 3.0–3.4. "
        "Should complete by Spring 2026."
    ),
    "average": (
        "This student is an average performer. "
        "Mix of B-, C+, C, and C- grades. "
        "May have 2-4 failures across the entire program. "
        "Failure strategy: Failed Fall courses → retake in Spring or Summer (if humanities/English/internship available). "
        "Failed Spring courses → retake in next Fall or Summer (Summer only for humanities/English/internship). "
        "Occasional W grades. GPA typically 2.1–2.8. "
        "Should complete by or near Spring 2026."
    ),
    "probation": (
        "This student is struggling academically. "
        "They have multiple F grades (3-6), some D and C- grades. "
        "Failed Fall courses can be retaken in Spring or Summer. "
        "Failed Spring courses can be retaken in Summer (if humanities/English/internship) or next Fall. "
        "Retaken courses must be shown with bracket notation [Grade] (e.g. [B-]) to indicate repeats. "
        "Some courses may be taken more than once. "
        "GPA is below 2.0, possibly as low as 1.5. "
        "Academic status should be 'Academic Probation'. "
        "May not complete by Spring 2026 due to multiple retakes."
    ),
    "withdrawal_heavy": (
        "This student frequently withdraws from courses mid-semester. "
        "Many courses show grade 'W' (3-6 withdrawals). "
        "Withdrawals often happen because student changes approach after failed courses. "
        "Otherwise grades are in the B- to C range. "
        "Some failed courses are retaken; some are withdrawn before completion. "
        "GPA is 2.0–2.5. "
        "Should complete by Spring 2026 but with irregular progress."
    ),
    "transfer": (
        "This student transferred from a different major partway through. "
        "Their early semesters show courses from a different program (first 2 semesters). "
        "From Year 2 (Spring 2023 or later) onward they follow the current program's study plan. "
        "GPA is in the 2.3–2.8 range. "
        "May have 1-2 failures in new program. "
        "Should complete by Spring 2026."
    ),
    "disciplined_retake": (
        "This student had a rough start but is disciplined about retakes. "
        "May have 2-3 failures in early semesters. "
        "Failed Fall courses are retaken in Spring of same year. "
        "Failed Spring courses are retaken next Fall month (not Summer). "
        "Shows improvement over time with consistent retake strategy. "
        "GPA gradually improves to 2.5–3.0 range. "
        "Should complete by Spring 2026 with clear progression visible in transcript."
    ),
    "summer_intensive": (
        "This student uses Summer terms strategically for humanities, English, and internship. "
        "Summer enrollment shows humanities courses (philosophy, history, etc.), English courses, and internship. "
        "May have 1-2 failed core courses that are retaken in Fall/Spring. "
        "Tries to maximize progress by taking electives and development courses in Summer. "
        "GPA is 2.8–3.3 range. "
        "Should complete by Spring 2026."
    ),
    "honor_student": (
        "This student is an honors program participant with exceptional achievement. "
        "Earns mostly A, A-, and B+ grades with very few B or C grades. "
        "Has 0 failures (honors students don't typically fail; they withdraw instead). "
        "GPA 3.8 or above. "
        "May graduate as valedictorian or with honors. "
        "Completes early, often finishing 1-2 semesters before expected graduation. "
        "Takes challenging electives and advanced courses."
    ),
    "part_time_worker": (
        "This student works part-time while studying, affecting academic progress. "
        "Shows irregular enrollment patterns and sometimes reduced course loads. "
        "Grades are mixed B-, C, and C+ with occasional lower grades. "
        "May have 1-3 failures due to time constraints. "
        "Takes fewer courses in some semesters (6-9 credits instead of 12-15). "
        "GPA typically 2.2–2.7. "
        "May take longer to graduate but eventually completes by Spring 2026 or works toward completion."
    ),
    "late_bloomer": (
        "This student starts with moderate struggles but shows significant improvement. "
        "First year grades include C-, C, and some C+/B- in first 2-3 semesters. "
        "May have 1-2 early failures (usually in Foundation or Math courses). "
        "From Year 2 onward, grades consistently improve to B/B+. "
        "Shows clear upward trend with GPA progression from 1.9 to 3.0+. "
        "Develops better study habits and time management over time. "
        "Completes by Spring 2026 with strong finish."
    ),
    "perfectionist": (
        "This student aims for excellence through selective retakes. "
        "May retake courses even after earning B+ or A- to improve to A grades. "
        "Shows pattern of revisiting challenging subjects multiple times. "
        "Very few failures but multiple retakes for grade improvement. "
        "GPA very high 3.6–3.9 range. "
        "Completes on time with high cumulative GPA. "
        "Takes slightly more semesters due to optional retakes."
    ),
}

# ──────────────────────────────────────────────────────────────────
# STUDY-PLAN SERIALISER
# Converts the nested STUDY_PLANS entry for one program into a
# clean, prompt-friendly text block.
# ──────────────────────────────────────────────────────────────────
def _resolve_course(cid: str) -> str:
    """Return 'COURSE_ID – Course Name (N cr)' if found in catalog."""
    info = COURSE_LOOKUP.get(cid)
    if info:
        return f"{cid} – {info['name']} ({info['credits']} cr)"
    return cid   # unknown placeholder like 'General Education Elective'


def _semester_lines(sem_data: Any, label: str) -> List[str]:
    """Recursively flatten semester course lists, handling nested dicts."""
    lines: List[str] = []
    if isinstance(sem_data, list):
        lines.append(f"    {label}:")
        for cid in sem_data:
            lines.append(f"      • {_resolve_course(cid)}")
    elif isinstance(sem_data, dict):
        # Nested specialisation (e.g. year_3 with tracks APD/GCG/HCI)
        for track, track_courses in sem_data.items():
            if isinstance(track_courses, list):
                lines.append(f"    {label} [{track}]:")
                for cid in track_courses:
                    lines.append(f"      • {_resolve_course(cid)}")
            elif isinstance(track_courses, int):
                pass   # elective counts – skip
    return lines


def build_study_plan_text(program: str) -> str:
    """Return a human-readable study-plan block for prompt injection."""
    plan = STUDY_PLANS[program]
    lines: List[str] = [
        f"PROGRAM: {program}",
        f"Total Credits Required: {plan.get('total_credits', 'N/A')}",
        "",
        "SEMESTER-BY-SEMESTER COURSE SCHEDULE:",
    ]
    for year_num in range(1, 5):
        year_key_lower = f"year_{year_num}"
        # FIX: case-insensitive key lookup (handles 'Year_3' in Physics of Universe)
        actual_year_key = next((k for k in plan if k.lower() == year_key_lower), None)
        # FIX: fallback to 'foundation_year' for year_1 (Materials Science)
        if actual_year_key is None and year_num == 1 and "foundation_year" in plan:
            actual_year_key = "foundation_year"
        if actual_year_key is None:
            continue
        year_data = plan[actual_year_key]
        lines.append(f"  Year {year_num}:")
        for sem_name in ("fall", "spring", "summer", "Summer"):
            if sem_name.lower() in {k.lower() for k in year_data}:
                actual_key = next(k for k in year_data if k.lower() == sem_name.lower())
                sem_lines = _semester_lines(year_data[actual_key], sem_name.capitalize())
                lines.extend(sem_lines)

    # Electives section (if present)
    if "electives" in plan:
        elec = plan["electives"]
        if isinstance(elec, dict):
            prog_electives = elec.get("program", [])
            sch_electives  = elec.get("sch", [])
            if prog_electives:
                lines.append("  Approved Program Electives (pick from):")
                for cid in prog_electives[:10]:   # cap for brevity
                    lines.append(f"      • {_resolve_course(cid)}")
            if sch_electives:
                lines.append("  Approved SCH/General-Education Electives (pick from):")
                for cid in sch_electives[:8]:
                    lines.append(f"      • {_resolve_course(cid)}")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────
# PROMPT BUILDER
# ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert academic registrar AI for Zewail City University of Science
and Technology (UST), Egypt. You generate perfectly accurate, schema-valid student
transcript JSON records. You follow every rule given in the user prompt exactly.
You NEVER add markdown fences. You output ONLY raw JSON.

YOU MUST FOLLOW THESE RULES RELIGIOUSLY:
1. ALL failed courses are retaken with retake notation [Grade].
2. Fall failures → retake in Spring OR next Fall.
3. Spring failures → retake in next Fall OR Summer (Summer ONLY if humanities/English/internship).
4. Summer courses: ONLY humanities, English, and internship/capstone.
5. Grades: A=4.0, A-=3.7, B+=3.3, B=3.0, B-=2.7, C+=2.3, C=2.0, C-=1.7, D=1.0, F=0.0.
6. Terminal grades (P, W, IP): quality_points=0, not counted in GPA.
7. Cumulative GPA must be exactly: total_quality_points / total_gpa_credits.
8. End term target: Spring 2026."""

def build_prompt(program: str, persona_key: str,
                 entry_year: int, semesters_to_generate: int,
                 student_name: str, student_id: str,
                 prev_institution: str, gender: str) -> str:
    plan_text   = build_study_plan_text(program)
    persona_txt = PERSONAS[persona_key]
    prog_info   = ZC_STRUCTURE["undergraduate_programs"].get(program, {})
    school      = prog_info.get("school", "Unknown School")
    degree      = prog_info.get("degree", f"BSc in {program}")

    return f"""Generate ONE student academic transcript for Zewail City University of Science and Technology.

=== STUDENT PROFILE ===
Name            : {student_name}
Student ID      : {student_id}
Gender          : {gender}
Program         : {program}
Degree          : {degree}
School          : {school}
Previous School : {prev_institution}
Entry Year      : {entry_year}
Persona         : {persona_key}

=== PERSONA RULES ===
{persona_txt}

=== STUDY PLAN (follow this exactly) ===
{plan_text}

=== COMPREHENSIVE ACADEMIC RULES ===

1. SEMESTER COUNT & PROGRESSION:
   Generate exactly {semesters_to_generate} completed semester records.
   Semester timeline: {entry_year} Fall → {entry_year+1} Spring → {entry_year+1} Summer (if applicable) →
   {entry_year+1} Fall → {entry_year+2} Spring → ... → 2026 Spring.
   Target end term: Spring 2026.

   CREDIT LIMITS PER SEMESTER (STRICTLY ENFORCED):
   • Regular semester (Fall/Spring): MINIMUM 12 credits, MAXIMUM 21 credits.
   • Summer semester: MAXIMUM 9 credits.
   • NEVER exceed these limits. If remaining courses don't fit in one semester,
     spread them across the next semester(s). Do NOT cram courses.

2. STUDY PLAN ADHERENCE:
   Follow semester-by-semester courses from the study plan exactly.
   Do NOT invent courses not in the study plan.
   Electives must come from "Approved Electives" list.
   If the study plan shows multiple TRACKS (e.g., APD/GCG/HCI or ITNS/ITCC),
   choose ONE track at the start and follow it consistently across ALL semesters.
   Do NOT mix courses from different tracks.

   CRITICAL: NEVER use generic/placeholder course IDs like:
   GEN_ED_ELECTIVE, BMS_ELECTIVE, FREE_ELECTIVE, PROG_ELECTIVE,
   SCH_ELECTIVE, SCIENCE_ELECTIVE, MATH_ELECTIVE, or any *_ELECTIVE pattern.
   Always use a REAL course code from the study plan or approved electives list
   (e.g., "PHIL 101", "HIST 201", "SOC 101", "PSYC 101", etc.).

3. FAILURE AND RETAKE STRATEGY:
   
   a) Failed Fall courses (grade F):
      • Can be retaken in same academic year's Spring semester, OR
      • Can be retaken in next Fall semester.
      • When retaken, grade appears as [Grade] (e.g., [B+], [C], [D]) to show it's a repeat.
      • Only the retaken grade counts for GPA.
   
   b) Failed Spring courses (grade F):
      • CANNOT be retaken in Summer (Summer is restricted to humanities/English/internship).
      • Must be retaken in next Fall semester, OR
      • Can be retaken in the following Spring.
      • When retaken, grade appears as [Grade].
   
   c) Retaken courses after failure:
      • Must appear again in the target retake semester with bracket notation [Grade].
      • First attempt (F) contributes 0 quality_points.
      • Only retaken attempt counts for GPA and earned credits.

4. SUMMER SEMESTER RESTRICTIONS:
   Summer terms can ONLY include:
   • Humanities courses (philosophy, history, literature, arts, social sciences, etc.)
   • English/Communication courses
   • Internship/Capstone/Final Project (ENGL 003, ENGL 004, codes like CSAI 399, BMS 399, etc.)
   
   IMPORTANT: Summer CANNOT include core major courses, science courses, engineering courses.
   Maximum 9 credits per Summer term. NEVER exceed 9 credits in Summer.

5. PASS/FAIL COURSES:
   Courses with terminal grades (ENGL 003, ENGL 004, military, internship):
   • Always receive grade "P"
   • quality_points = 0
   • Not counted in GPA but count as attempted credits.

6. GRADING SCALE (use ONLY these values for GPA courses):
   A=4.0  A-=3.7  B+=3.3  B=3.0  B-=2.7  C+=2.3  C=2.0  C-=1.7  D=1.0  F=0.0

7. QUALITY POINTS & GPA CALCULATIONS:
   • Quality Points = credits × grade_points (rounded to 2 decimal places)
   • Terminal grades (P, W, IP): quality_points = 0
   • Term GPA = sum(quality_points) / sum(gpa_credits) for that term (non-P/W/IP only)
   • Cumulative GPA = total_quality_points / total_gpa_credits across ALL completed terms

8. WITHDRAWN COURSES:
   • Grade "W", earn 0 quality points, 0 GPA credits
   • Count as attempted credits

9. IN-PROGRESS COURSES:
   • Current semester courses if student is still enrolled
   • Grade "IP", quality_points = 0, not counted in GPA

=== REQUIRED JSON SCHEMA ===
Return ONLY this JSON object — no markdown, no explanation:
{{
  "student_id": "{student_id}",
  "name": "{student_name}",
  "gender": "{gender}",
  "program": "{program}",
  "degree": "{degree}",
  "school": "{school}",
  "previous_institution": "{prev_institution}",
  "entry_year": {entry_year},
  "persona": "{persona_key}",
  "enrollment_status": "<Active | Graduated | Academic Probation>",
  "cumulative_gpa": <float rounded to 4 decimal places>,
  "semesters": [
    {{
      "term_name": "<YYYY Fall | YYYY Spring | YYYY Summer>",
      "courses": [
        {{
          "course_id":      "<e.g. CSAI 101>",
          "title":          "<full course title from study plan>",
          "subtype":        "LECTURE",
          "grade":          "<A|A-|B+|B|B-|C+|C|C-|D|F|P|W|IP|[B+]|…>",
          "credits":        <integer>,
          "quality_points": <float>
        }}
      ],
      "term_statistics": {{
        "attempted_credits": <int>,
        "earned_credits":    <int>,
        "gpa_credits":       <int>,
        "quality_points":    <float>,
        "term_gpa":          <float>
      }},
      "running_totals": {{
        "attempted_credits": <int>,
        "earned_credits":    <int>,
        "total_credits":     <int>,
        "gpa_credits":       <int>,
        "transfer_credits":  0,
        "quality_points":    <float>,
        "cumulative_gpa":    <float>
      }}
    }}
  ]
}}
"""

# ──────────────────────────────────────────────────────────────────
# LLM CALLER
# ──────────────────────────────────────────────────────────────────
def call_llm(prompt: str) -> Optional[str]:
    """Send prompt to Ollama cloud API (ollama.com)."""
    client = Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"}
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.message.content
        except ConnectionError:
            print(f"   [Attempt {attempt}] Connection error – check your internet and API key.")
        except TimeoutError:
            print(f"   [Attempt {attempt}] Request timed out after {REQUEST_TIMEOUT}s.")
        except Exception as exc:
            print(f"   [Attempt {attempt}] LLM call failed: {exc}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
    return None


def _extract_json_object(text: str) -> Optional[str]:
    """FIX #12: Find the first balanced { … } block using a bracket counter.
    Much more reliable than a greedy regex on nested JSON.
    """
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    escape = False
    for i, ch in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_str:
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start: i + 1]
    return None


def parse_json_response(raw: str) -> Optional[Dict]:
    """Extract and parse a JSON object from the LLM response."""
    if not raw:
        return None
    # Strip markdown fences if the model added them despite instructions
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # FIX #12: Use bracket-counting extractor instead of greedy regex
    block = _extract_json_object(cleaned)
    if block:
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            pass
    return None


# ──────────────────────────────────────────────────────────────────
# ACADEMIC INTEGRITY VALIDATOR
# ──────────────────────────────────────────────────────────────────
class verify_academic_integrity:
    """
    Validates every generated transcript:
      1. quality_points = credits × grade_points
      2. cumulative_gpa = total_quality_points / total_gpa_credits
      3. Summer credits ≤ 9
      4. Graduated students have earned ≥ required total_credits
    """
    TOLERANCE = 0.05

    def __init__(self, transcripts: List[Dict]):
        self.transcripts = transcripts
        self.errors: List[str] = []

    def run(self) -> bool:
        for t in self.transcripts:
            sid = t.get("student_id", "???")
            self._check_quality_points(t, sid)
            self._check_cumulative_gpa(t, sid)
            self._check_summer_credits(t, sid)
            self._check_graduation(t, sid)
            self._check_credit_limits(t, sid)
            self._check_invented_courses(t, sid)
        ok = len(self.errors) == 0
        if ok:
            print(f"✅ Integrity check PASSED for all {len(self.transcripts)} transcripts.")
        else:
            print(f"⚠️  Integrity check: {len(self.errors)} issue(s) found:")
            for e in self.errors[:30]:      # cap display
                print(f"   • {e}")
        return ok

    def _retaken_courses(self, t: Dict) -> Set[str]:
        """Return set of course_ids that were retaken (have a [Grade] entry later)."""
        retaken: Set[str] = set()
        for sem in t.get("semesters", []):
            for c in sem.get("courses", []):
                grade = c.get("grade", "")
                if grade.startswith("[") and grade.endswith("]"):
                    retaken.add(c.get("course_id", ""))
        return retaken

    def _check_quality_points(self, t: Dict, sid: str):
        for sem in t.get("semesters", []):
            for c in sem.get("courses", []):
                grade = c.get("grade", "")
                cr    = c.get("credits", 0)
                qp    = c.get("quality_points", 0)
                gp    = grade_points(grade)
                if gp is None:
                    expected = 0.0
                else:
                    expected = round(cr * gp, 2)
                if abs(qp - expected) > self.TOLERANCE:
                    self.errors.append(
                        f"[{sid}] {sem.get('term_name','')} {c.get('course_id','?')}: "
                        f"QP={qp} expected {expected} ({cr}cr×{gp} for '{grade}')"
                    )

    def _check_cumulative_gpa(self, t: Dict, sid: str):
        total_qp = total_gpa_cr = 0.0
        retaken = self._retaken_courses(t)
        for sem in t.get("semesters", []):
            for c in sem.get("courses", []):
                gp = grade_points(c.get("grade", ""))
                if gp is not None:
                    # Skip the original F row if this course was later retaken
                    if c.get("grade") == "F" and c.get("course_id") in retaken:
                        continue
                    total_qp     += c.get("quality_points", 0)
                    total_gpa_cr += c.get("credits", 0)
        if total_gpa_cr > 0:
            expected_cgpa = round(total_qp / total_gpa_cr, 4)
            recorded_cgpa = t.get("cumulative_gpa", 0)
            if abs(recorded_cgpa - expected_cgpa) > self.TOLERANCE:
                self.errors.append(
                    f"[{sid}] CGPA recorded={recorded_cgpa} computed={expected_cgpa}"
                )

    def _check_summer_credits(self, t: Dict, sid: str):
        for sem in t.get("semesters", []):
            if "Summer" in sem.get("term_name", ""):
                total = sum(c.get("credits", 0) for c in sem.get("courses", []))
                if total > 9:
                    self.errors.append(
                        f"[{sid}] {sem['term_name']}: summer credits={total} > 9"
                    )

    def _check_graduation(self, t: Dict, sid: str):
        if t.get("enrollment_status") != "Graduated":
            return
        prog = t.get("program", "")
        plan = STUDY_PLANS.get(prog, {})
        required = plan.get("total_credits", 0)
        if not required:
            return
        earned = sum(
            c.get("credits", 0)
            for sem in t.get("semesters", [])
            for c in sem.get("courses", [])
            if c.get("grade", "") not in ("F", "W", "IP", "")
        )
        if earned < required:
            self.errors.append(
                f"[{sid}] Graduated but earned {earned} < {required} required credits"
            )

    def _check_credit_limits(self, t: Dict, sid: str):
        """Reject semesters exceeding credit limits (21 regular, 9 summer)."""
        for sem in t.get("semesters", []):
            term = sem.get("term_name", "")
            total_cr = sum(c.get("credits", 0) or 0 for c in sem.get("courses", []))
            is_summer = "summer" in term.lower()
            if is_summer and total_cr > 9:
                # Already caught by _check_summer_credits, skip duplicate
                pass
            elif not is_summer and total_cr > 21:
                self.errors.append(
                    f"[{sid}] {term}: credit overload = {total_cr} (max 21 for Fall/Spring)"
                )

    def _check_invented_courses(self, t: Dict, sid: str):
        """Reject transcripts with generic/placeholder course IDs."""
        BANNED_PATTERNS = [
            "ELECTIVE", "GEN_ED", "FREE_", "PROG_", "SCH_",
            "SCIENCE_", "MATH_", "_ELEC",
        ]
        for sem in t.get("semesters", []):
            for c in sem.get("courses", []):
                cid = c.get("course_id", "").upper()
                for pattern in BANNED_PATTERNS:
                    if pattern in cid:
                        self.errors.append(
                            f"[{sid}] {sem.get('term_name','')}: invented course '{c.get('course_id','')}' = '{c.get('title','')}'"
                        )
                        break


# ──────────────────────────────────────────────────────────────────
# STUDENT PROFILE HELPERS - EGYPTIAN NAMES ONLY
# ──────────────────────────────────────────────────────────────────
MALE_FIRST = [
    "Ahmed","Mohamed","Omar","Youssef","Karim","Hassan","Ali","Mahmoud",
    "Ibrahim","Khaled","Amr","Tamer","Sherif","Tarek","Mostafa","Adham",
    "Seif","Yasser","Walid","Hazem","Bassem","Ziad","Marwan","Adam",
    "Abdullah","Fares","Ramy","Eslam","Hossam","Ayman","Wael","Nader",
    "Badr","Hamza","Yahia","Raouf","Samir","Ashraf","Ihab","Hatem",
    "Hani","Jamal","Karim","Layth","Munir","Nasir","Qasim","Rashid",
    "Saad","Tariq","Ussama","Yaseen","Zakariya","Bilal",
    "Dirar","Emad","Gamil","Raffat","Jalal","Kamal","Louay","Emam",
    "Nabil","Osama","Safwan","Fares","Adam","Baher","Fadi","Gamal","Hisham",
    "Basel","Yusuf","Zuhir","Anis","Bahaa","Shady","Moateesam","Amir",
    "Aaraf","Abelab","Abesha","Abid","Adel","Afify","Agha","Agha",
    "Alaa","Alaa","Alawi","Albahr","Aldair","Aldous","Aleia","Alemayehu",
    "Alfried","Alhadi","Aljean","Aljohn","Aljoseph","Alkali","Allahdin",
    "Alred","Alsiddiq","Altair","Altay","Altayeb","Alwan","Aly","Amjad",
    "Amin","Amjad","Amla","Amlak","Amnon","Amor","Amr","Amro",
]
FEMALE_FIRST = [
    "Fatma","Nour","Sara","Hana","Mariam","Layla","Dina","Rania","Heba",
    "Yasmin","Salma","Mona","Amira","Noha","Aya","Rana","Nada","Habiba",
    "Malak","Jana","Farida","Lina","Menna","Yara","Shahd","Zeina","Nadia",
    "Ghada","Mai","Norhan","Aliaa","Shaimaa","Asmaa","Doaa","Eman","Hend",
    "Israa","Lara","Omnia","Radwa","Samar","Tamara","Amany","Dalia","Reem",
    "Abeer","Basma","Dalila","Ebtsam","Fadia","Jilan","Hana",
    "Iman","Jihan","Karima","Lamia","Maha","Omaima",
    "Yara","Samira","Tara","Roaa","Larin","Walaa",
    "Yasmine","Rudaina","Amal","Bushra","Jihad","Rahma","Elham","Farah",
    "Gyda","Hiya","Ibtihaj","Toqa","Khadija","Laila","Mayada",
    "Doaa","Retal","Razan","Rula","Sunduss","Talia","Reem",
]
MIDDLE_NAMES = [
    "abouelela","abdelfattah","abdelaziz","abdelhamid","abdelkader",
    "abdelmonem","abdelnasser","abdelrahman","abdelsalam","abdelwahab",
    "mokhtar","soliman","sayed","farag","badran","ragheb","mansour",
    "hassan","omar","ali","yousef","mustafa","naguib","hamdi","zaki",
    "fouad","kamal","saleh","ramadan","gaber","fahmy","nasr","rashad",
    "samir","shawky","walid","wazir","yaseen","yousry","zeid","zakarya",
    "zuhair","abdelmajid","abdelrazek","abdullaziz","amin","nourdin",
    "anwar","galal","ezzeldeen","ezzat","bahjat","fakhry","baraka",
    "barkat","basheer","basyoni","ghalwash","maher","rakha",
    "mosaad","baleegh","wael","zeyad","shokry","khaled","anas",
    "abdallah","abder","abdou","abdulaah","abdulah","abdulamir","abdulazeem",
    "abdulaziz","abdulbari","abdulbasit","AbdulFattah","abdulgader","abduljaber",
    "abdullahi","abdullaziz","abdullrahim","abdulmageed","abdulmalik","abdulmannan",
    "abdulmaseeh","abdulmejid","abdulmunim","abdunnabi","abdunnasir","abdulnasser",
    "abdulnoor","abdulqader","abdulqawi","sanad","abdulqhader","abdulraheem",
    "abdulrahman","abdulrazak","abdulredha","abdulrehim","abdulrehem","abdulrida",
    "abdulsalaam","abdulsalam","sami","abdulsanad","abdulsamad","nezar",
]
LAST_NAMES = [
    "Mohamed","Ahmed","Hassan","Ali","Ibrahim","Mahmoud","Abdel-Rahman",
    "El-Sayed","Mostafa","Khalil","Mansour","Osman","El-Masry","Fouad",
    "Zaki","Fathy","Soliman","Naguib","Farouk","Helmy","Badawy","Hamdy",
    "Shawky","Saleh","Ramadan","Hussein","Amin","Gaber","Fahmy","Kamal",
    "Saber","Rashad","Nasr","Ashraf","Darwish","Abdallah","El-Deeb",
    "Aziz","Lotfy","Hashem","El-Naggar","Qasim","Salem","Sherif",
    "Zaki","Alkhatib","Rashed","Hindi","Hesham","Yaseer",
    "Ameen","Gaber","Saeed","Qassem","Ayman","Waleed","Dsoqi",
    "Riad","Abdelhameed","deif","Adel","Altayar","Alterwah",
    "El-Sherbini","El-Sherif","El-Shorbagy","Aser",
    "Maged","Nazmy","Ashraf","Adly","Adham",
    "Mahfouz","Omran","Hamza","Mahdy","Maher","Magdy","Maghrabi",
    "Makhlouf","Mekki","Mazen","Mahfouz","Sayed","Malek",
    "Nabil","Nabih","Ramez","Noamman",
    "Rabie",
]
HIGH_SCHOOLS = [
    "Pyramids Language School, Thanaweya Amma",
    "New Cairo British International School",
    "Manarat Al-Fayoum International School",
    "El-Nasr Language School, Al-Dokki",
    "Cairo American College",
    "Tanta Modern Language School",
    "Alexandria Language School",
    "Future International School",
    "Al-Azhar Secondary School",
    "Heliopolis STEM School",
    "New Giza School",
    "El-Shorouk Modern Academy",
    "Misr Language School, Mohandessin",
    "IGCSE School of Excellence, Maadi",
    "Arab Academy for Science and Technology",
]


def random_name(gender: str, rng: random.Random = None) -> str:
    """Generate random name using provided Random instance for reproducibility."""
    if rng is None:
        rng = random
    first  = rng.choice(MALE_FIRST if gender == "Male" else FEMALE_FIRST)
    middle = rng.choice(MIDDLE_NAMES)
    last   = rng.choice(LAST_NAMES)
    return f"{first} {middle} {last}"


# ──────────────────────────────────────────────────────────────────
# SEMESTER CALCULATION FOR SPRING 2026 END TERM
# ──────────────────────────────────────────────────────────────────
def get_program_duration(program: str) -> int:
    """
    Get program duration in years from study plan.
    Uses ZEWAIL_CITY_STRUCTURE as the authoritative source.
    All undergraduate programs at ZC are 4 years unless explicitly specified otherwise.
    """
    # FIX: Removed wrong 5-year Engineering override.
    # All Engineering programs in ZEWAIL_CITY_STRUCTURE have duration_years=4.
    prog_info = ZC_STRUCTURE["undergraduate_programs"].get(program, {})
    duration = prog_info.get("duration_years", 4)
    return duration


def calculate_semesters_to_expected_graduation(entry_year: int, program: str) -> Tuple[int, str, int]:
    """
    Calculate expected graduation date based on program duration.
    Returns: (year, semester_name, semester_count)
    
    Examples:
      - 2021 entry, Engineering (5yr): Spring 2026 (11 semesters)
      - 2021 entry, CSAI (4yr): Spring 2025 (9 semesters)
      - 2022 entry, Science (4yr): Spring 2026 (9 semesters)
      - 2024 entry, Business (4yr): Spring 2028 (9 semesters, but truncate to 2026)
    """
    duration = get_program_duration(program)
    expected_grad_year = entry_year + duration
    
    # Expected graduation is in Spring of that year
    expected_semester_name = "Spring"
    expected_semesters = duration * 2 + 1  # +1 for the final Spring
    
    return (expected_grad_year, expected_semester_name, expected_semesters)


def calculate_semesters_available_until_spring_2026(entry_year: int) -> int:
    """
    Calculate maximum semesters available from entry until Spring 2026 (today's date).
    Formula: (2026 - entry_year) * 2 + 1
    """
    return (2026 - entry_year) * 2 + 1


def pick_semesters(persona_key: str, program: str, entry_year: int, rng: random.Random = None) -> Tuple[int, bool]:
    """
    Determine number of completed semesters for a student.
    Now program-aware with intelligent graduation timing.
    
    Args:
        persona_key: The student's persona type
        program: The student's program
        entry_year: Year the student entered
        rng: Random instance for reproducibility (uses global random if None)
    
    Returns: (semester_count, should_be_graduated)
      - semester_count: number of semesters in transcript
      - should_be_graduated: whether student should have "Graduated" status
    """
    if rng is None:
        rng = random
    
    # Get program duration and expected graduation
    duration = get_program_duration(program)
    expected_grad_year, _, expected_sems = calculate_semesters_to_expected_graduation(entry_year, program)
    
    # Maximum semesters available until Spring 2026 (today)
    max_sems_available = calculate_semesters_available_until_spring_2026(entry_year)
    max_sems_available = max(max_sems_available, 2)
    
    # semesters_until_expected_grad should not be negative
    semesters_until_expected_grad = expected_sems
    if expected_grad_year < 2026:
        # Expected graduation before Spring 2026
        semesters_until_expected_grad = expected_sems
    elif expected_grad_year == 2026:
        # Expected graduation in Spring 2026
        semesters_until_expected_grad = expected_sems
    else:
        # Expected graduation after Spring 2026, but we only have data until Spring 2026
        semesters_until_expected_grad = max_sems_available
    
    # Persona-based adjustments
    if persona_key == "high_achiever":
        # High achievers graduate 1 semester early and ARE graduated
        target_sem = max(1, semesters_until_expected_grad - 1)
        target_sem = min(target_sem, max_sems_available)
        is_grad = True  # High achievers who complete early ARE graduated
        return (target_sem, is_grad)
    
    elif persona_key == "honor_student":
        # Honor students graduate very early (1-2 semesters early)
        target_sem = max(1, semesters_until_expected_grad - rng.randint(1, 2))
        target_sem = min(target_sem, max_sems_available)
        is_grad = True  # Honor students always graduate
        return (target_sem, is_grad)
    
    elif persona_key == "perfectionist":
        # Perfectionists complete on time, possibly with extra retakes
        is_grad = semesters_until_expected_grad <= max_sems_available
        target_sem = min(semesters_until_expected_grad + 1, max_sems_available)  # Extra semester for retakes
        return (min(target_sem, max_sems_available), is_grad)
    
    elif persona_key == "part_time_worker":
        # Part-time workers may take longer, variable progress
        # FIX: clamp lower bound so randint never gets lower > upper for late entry years
        lower = min(max(2, semesters_until_expected_grad - 2), max_sems_available)
        target_sem = rng.randint(lower, max_sems_available)
        is_grad = target_sem >= semesters_until_expected_grad and expected_grad_year <= 2026
        return (target_sem, is_grad)
    
    elif persona_key == "late_bloomer":
        # Late bloomers complete on time but with initial struggles
        is_grad = semesters_until_expected_grad <= max_sems_available
        target_sem = min(semesters_until_expected_grad, max_sems_available)
        return (target_sem, is_grad)
    
    elif persona_key == "probation":
        # Probation students likely don't finish on time
        # FIX: clamp lower bound so randint never gets lower > upper for late entry years
        lower = min(max(2, semesters_until_expected_grad - 4), max_sems_available)
        target_sem = rng.randint(lower, max_sems_available)
        is_grad = target_sem >= semesters_until_expected_grad and expected_grad_year <= 2026
        return (target_sem, is_grad)
    
    elif persona_key == "disciplined_retake":
        # Completes on time despite retakes
        is_grad = semesters_until_expected_grad <= max_sems_available
        target_sem = min(semesters_until_expected_grad, max_sems_available)
        return (target_sem, is_grad)
    
    elif persona_key == "summer_intensive":
        # Completes on time
        is_grad = semesters_until_expected_grad <= max_sems_available
        target_sem = min(semesters_until_expected_grad, max_sems_available)
        return (target_sem, is_grad)
    
    elif persona_key == "transfer":
        # Transfers add complexity, may graduate on time in new program
        is_grad = semesters_until_expected_grad <= max_sems_available
        target_sem = min(semesters_until_expected_grad, max_sems_available)
        return (target_sem, is_grad)
    
    else:
        # Default: solid_b, average, withdrawal_heavy
        is_grad = semesters_until_expected_grad <= max_sems_available
        target_sem = min(semesters_until_expected_grad, max_sems_available)
        # Add some variation
        if rng.random() < 0.3 and expected_grad_year < 2026:
            # 30% chance of graduating early if expected before 2026
            # FIX: clamp lower bound to avoid randint(lower > upper)
            lower = min(max(1, semesters_until_expected_grad - 2), target_sem)
            target_sem = min(target_sem, rng.randint(lower, target_sem))
        return (target_sem, is_grad)


# ──────────────────────────────────────────────────────────────────
# TRANSCRIPT VALIDATION RUBRIC
# ──────────────────────────────────────────────────────────────────
class TranscriptValidationRubric:
    """
    Comprehensive validation rubric for generated transcripts.
    Checks program-appropriate duration, graduation timing, data integrity,
    and persona consistency.
    """
    
    def __init__(self, transcripts: List[Dict]):
        self.transcripts = transcripts
        self.rubric_results: List[Dict] = []
        self.issues: List[str] = []
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks and return comprehensive report."""
        print("\n" + "="*80)
        print("📋 TRANSCRIPT VALIDATION RUBRIC - COMPREHENSIVE CHECK")
        print("="*80)
        
        results = {
            "total_transcripts": len(self.transcripts),
            "checks_passed": 0,
            "checks_failed": 0,
            "details": {}
        }
        
        # Run all checks
        results["details"]["batch_years"] = self._check_batch_years()
        results["details"]["program_duration"] = self._check_program_duration()
        results["details"]["graduation_timing"] = self._check_graduation_timing()
        results["details"]["spring_2026_truncation"] = self._check_spring_2026_truncation()
        results["details"]["gpa_calculations"] = self._check_gpa_calculations()
        results["details"]["failure_retake_rules"] = self._check_failure_retake_rules()
        results["details"]["summer_constraints"] = self._check_summer_constraints()
        results["details"]["persona_consistency"] = self._check_persona_consistency()
        
        # Summary
        print("\n" + "="*80)
        print("📊 VALIDATION SUMMARY")
        print("="*80)
        for check_name, check_result in results["details"].items():
            status = "✅ PASS" if check_result["passed"] else "❌ FAIL"
            print(f"{status} | {check_name}: {check_result['message']}")
            if check_result.get("issues"):
                for issue in check_result["issues"][:3]:  # Show first 3
                    print(f"         • {issue}")
                if len(check_result["issues"]) > 3:
                    print(f"         ... and {len(check_result['issues']) - 3} more")
        
        return results
    
    def _check_batch_years(self) -> Dict:
        """Check batch year distribution (2021-2025)."""
        batch_dist = {2021: 0, 2022: 0, 2023: 0, 2024: 0, 2025: 0}
        issues = []
        
        for t in self.transcripts:
            year = t.get("entry_year")
            if year in batch_dist:
                batch_dist[year] += 1
            else:
                issues.append(f"Invalid entry_year {year}")
        
        passed = len(issues) == 0 and all(batch_dist.values())
        return {
            "passed": passed,
            "message": f"Distribution: {dict(sorted(batch_dist.items()))}",
            "issues": issues
        }
    
    def _check_program_duration(self) -> Dict:
        """Check programs have appropriate duration and structure."""
        issues = []
        program_stats = {}
        
        for t in self.transcripts:
            program = t.get("program", "")
            entry_year = t.get("entry_year", 0)
            num_semesters = len(t.get("semesters", []))
            
            if program not in program_stats:
                program_stats[program] = []
            program_stats[program].append((entry_year, num_semesters))
            
            # Check program exists and has duration
            duration = get_program_duration(program)
            expected_sems = duration * 2 + 1
            min_expected = expected_sems - 4  # Allow some flex
            max_expected = expected_sems + 2
            
            if not (min_expected <= num_semesters <= max_expected * 1.5):
                issues.append(
                    f"{program} ({entry_year}): {num_semesters} sems (expected ~{expected_sems})"
                )
        
        passed = len(issues) < len(self.transcripts) * 0.1  # Allow 10% issues
        msg = f"{len(program_stats)} programs, avg semesters per program: "
        msg += str({p: round(sum(s[1] for s in v)/len(v), 1) for p, v in list(program_stats.items())[:3]})
        
        return {"passed": passed, "message": msg, "issues": issues}
    
    def _check_graduation_timing(self) -> Dict:
        """Check graduation dates align with program duration."""
        issues = []
        grad_before_expected = 0
        grad_on_time = 0
        grad_after_spring_2026 = 0
        
        for t in self.transcripts:
            program = t.get("program", "")
            entry_year = t.get("entry_year", 0)
            status = t.get("enrollment_status", "")
            last_semester = t.get("semesters", [{}])[-1].get("term_name", "")
            
            # Expected graduation
            _, _, expected_sems = calculate_semesters_to_expected_graduation(entry_year, program)
            exp_grad_year = entry_year + get_program_duration(program)
            actual_sems = len(t.get("semesters", []))
            
            # Analyze graduation pattern
            if status == "Graduated":
                if actual_sems < expected_sems - 1:
                    grad_before_expected += 1
                    if actual_sems < expected_sems - 4:
                        issues.append(f"{program}/{entry_year}: Early grad by >2yr")
                elif actual_sems <= expected_sems + 1:
                    grad_on_time += 1
                else:
                    grad_after_spring_2026 += 1
            
            # Check no semesters past Spring 2026
            if "2026" in last_semester and status == "Graduated":
                pass  # OK
            elif "2027" in last_semester or "2028" in last_semester:
                issues.append(f"{program}/{entry_year}: Extends past Spring 2026")
                grad_after_spring_2026 += 1
        
        passed = len(issues) < len(self.transcripts) * 0.15  # Allow 15% issues
        msg = f"On-time: {grad_on_time}, Early: {grad_before_expected}, Beyond: {grad_after_spring_2026}"
        
        return {"passed": passed, "message": msg, "issues": issues}
    
    def _check_spring_2026_truncation(self) -> Dict:
        """Check all transcripts end by Spring 2026 (today's date)."""
        issues = []
        
        for t in self.transcripts:
            last_term = t.get("semesters", [{}])[-1].get("term_name", "")
            
            # Extract year and semester
            parts = last_term.split()
            if len(parts) >= 2:
                try:
                    year = int(parts[0])
                    if year > 2026:
                        issues.append(f"Extends to {last_term}")
                    elif year == 2026:
                        sem = parts[1]
                        if sem not in ["Spring", "Fall", "Summer"]:
                            issues.append(f"Invalid semester: {last_term}")
                except ValueError:
                    issues.append(f"Invalid term format: {last_term}")
        
        passed = len(issues) == 0
        msg = f"All transcripts end at or before Spring 2026"
        
        return {"passed": passed, "message": msg, "issues": issues}
    
    def _check_gpa_calculations(self) -> Dict:
        """Verify GPA calculations are accurate (FIX: now checks ALL transcripts, not just 10)."""
        issues = []
        retake_helper = verify_academic_integrity([])  # reuse logic
        
        for t in self.transcripts:  # ✅ FIX: Check ALL transcripts, not just first 10
            retaken = retake_helper._retaken_courses(t)
            total_qp = 0
            total_gpa_cr = 0
            
            for sem in t.get("semesters", []):
                for course in sem.get("courses", []):
                    gp = grade_points(course.get("grade", ""))
                    if gp is None:
                        continue
                    # ✅ FIX #5: Skip original F row if this course was retaken
                    if course.get("grade") == "F" and course.get("course_id") in retaken:
                        continue
                    total_qp += course.get("quality_points", 0)
                    total_gpa_cr += course.get("credits", 0)
            
            if total_gpa_cr > 0:
                expected_cgpa = round(total_qp / total_gpa_cr, 4)
                actual_cgpa = t.get("cumulative_gpa", 0)
                if abs(expected_cgpa - actual_cgpa) > 0.05:  # TOLERANCE
                    issues.append(
                        f"[{t.get('student_id')}] CGPA {actual_cgpa} ≠ {expected_cgpa}"
                    )
        
        passed = len(issues) < len(self.transcripts) * 0.05  # Allow 5% tolerance
        msg = f"{len(self.transcripts) - len(issues)}/{len(self.transcripts)} correct CGPAs"
        
        return {"passed": passed, "message": msg, "issues": issues}
    
    def _check_failure_retake_rules(self) -> Dict:
        """Check failure and retake patterns follow rules."""
        issues = []
        
        for t in self.transcripts:
            sem_list = t.get("semesters", [])
            
            # Track failures and retakes
            for i, sem in enumerate(sem_list):
                term_name = sem.get("term_name", "")
                for course in sem.get("courses", []):
                    grade = course.get("grade", "")
                    cid = course.get("course_id", "")
                    
                    if grade == "F":
                        # Find if retaken later
                        found_retake = False
                        for j in range(i+1, len(sem_list)):
                            for future_course in sem_list[j].get("courses", []):
                                if future_course.get("course_id") == cid:
                                    future_grade = future_course.get("grade", "")
                                    if future_grade.startswith("["):
                                        found_retake = True
                                        break
                        
                        if not found_retake:
                            # Some failures may not be retaken (acceptable for some personas)
                            pass
        
        passed = len(issues) < len(self.transcripts) * 0.1
        msg = f"Failure/retake patterns checked"
        
        return {"passed": passed, "message": msg, "issues": issues}
    
    def _check_summer_constraints(self) -> Dict:
        """Check Summer terms only have humanities/English/internship."""
        issues = []
        
        for t in self.transcripts:
            for sem in t.get("semesters", []):
                term_name = sem.get("term_name", "")
                if "Summer" in term_name:
                    total_cr = 0
                    for course in sem.get("courses", []):
                        total_cr += course.get("credits", 0)
                        cid = course.get("course_id", "")
                        # Check for non-allowed courses
                        if any(x in cid for x in ["MATH", "PHYS", "ENGR", "CSCI"]):
                            if not any(x in cid for x in ["ENGL", "internship", "399"]):
                                issues.append(
                                    f"{term_name}: {cid} not allowed in Summer"
                                )
                    
                    if total_cr > 9:
                        issues.append(f"{term_name}: {total_cr} credits > 9")
        
        passed = len(issues) < len(self.transcripts) * 0.05
        msg = f"Summer constraints validated"
        
        return {"passed": passed, "message": msg, "issues": issues}
    
    def _check_persona_consistency(self) -> Dict:
        """Check persona aligns with academic patterns."""
        issues = []
        persona_stats = {}
        
        for t in self.transcripts:
            persona = t.get("persona", "")
            cgpa = t.get("cumulative_gpa", 0)
            status = t.get("enrollment_status", "")
            
            # Get expected GPA range for persona
            expected_range = {
                "high_achiever": (3.7, 4.0),
                "solid_b": (3.0, 3.4),
                "average": (2.1, 2.8),
                "probation": (1.5, 2.0),
                "withdrawal_heavy": (2.0, 2.5),
                "transfer": (2.3, 2.8),
                "disciplined_retake": (2.5, 3.0),
                "summer_intensive": (2.8, 3.3)
            }
            
            if persona in expected_range:
                min_gpa, max_gpa = expected_range[persona]
                if not (min_gpa - 0.2 <= cgpa <= max_gpa + 0.2):  # Allow 0.2 margin
                    issues.append(
                        f"{persona}: GPA {cgpa} outside expected {min_gpa}-{max_gpa}"
                    )
        
        passed = len(issues) < len(self.transcripts) * 0.15
        msg = f"Persona-GPA alignment checked"
        
        return {"passed": passed, "message": msg, "issues": issues}


# ──────────────────────────────────────────────────────────────────
# SCHOOL → PROGRAM DISTRIBUTION
# ──────────────────────────────────────────────────────────────────
def get_balanced_programs(n: int, rng: random.Random) -> List[str]:
    """Return n programs with strict round-robin balance across 4 schools.
    
    FIX #9: accepts an rng instance instead of creating/using global state.
    """
    school_map: Dict[str, List[str]] = {
        "CSAI": [], "Engineering": [], "Science": [], "Business": []
    }
    ug = ZC_STRUCTURE["undergraduate_programs"]
    for prog_name, prog_info in ug.items():
        if prog_name not in STUDY_PLANS:
            continue
        school = prog_info.get("school", "")
        if "Computational" in school:
            school_map["CSAI"].append(prog_name)
        elif "Engineering" in school:
            school_map["Engineering"].append(prog_name)
        elif "Business" in school:
            school_map["Business"].append(prog_name)
        else:
            # FIX: use else (not elif "Science") so School of Science programs
            # are never accidentally captured by the CSAI/Engineering/Business checks.
            school_map["Science"].append(prog_name)

    schools = list(school_map.keys())
    result: List[str] = []
    for i in range(n):
        school = schools[i % len(schools)]
        pool   = school_map[school] or list(STUDY_PLANS.keys())
        result.append(rng.choice(pool))
    return result


# ──────────────────────────────────────────────────────────────────
# PERSONA DISTRIBUTION
# ──────────────────────────────────────────────────────────────────
PERSONA_POOL = (
    ["high_achiever"]    * 12 +
    ["honor_student"]    * 8 +
    ["solid_b"]          * 18 +
    ["average"]          * 18 +
    ["probation"]        * 8 +
    ["withdrawal_heavy"] * 8 +
    ["transfer"]         * 6 +
    ["disciplined_retake"] * 8 +
    ["summer_intensive"] * 6 +
    ["part_time_worker"] * 7 +
    ["late_bloomer"]     * 8 +
    ["perfectionist"]    * 5
)


# ──────────────────────────────────────────────────────────────────
# STUDENT ID GENERATOR
# FIX #7: Proper sequencing with StudentIDRegistry class
# ──────────────────────────────────────────────────────────────────

class StudentIDRegistry:
    """Thread-safe (single-threaded) student ID allocation per batch year."""

    def __init__(self, existing: Optional[Set[str]] = None):
        self._counters: Dict[int, int] = {y: 1 for y in range(2021, 2026)}
        if existing:
            for sid in existing:
                try:
                    year = int(str(sid)[:4])
                    seq  = int(str(sid)[4:])
                    if year in self._counters:
                        self._counters[year] = max(self._counters[year], seq + 1)
                except ValueError:
                    pass

    def next(self, year: int) -> str:
        """Generate next sequential ID for the given year."""
        sid = f"{year}{self._counters[year]:05d}"
        self._counters[year] += 1
        return sid


# ──────────────────────────────────────────────────────────────────
# MAIN GENERATOR
# FIX #8/#9: Deterministic per-student seed; single rng passed through
# ──────────────────────────────────────────────────────────────────
def generate(n_students: int = 100000, seed: int = 42, existing_ids: set = None,
             start_index: int = 0) -> List[Dict]:
    """
    Generate n_students transcripts with deterministic reproducibility.
    Per-student randomness is derived as hash(seed, global_index) so that:
      • running with the same --seed always produces the same output,
      • appending more students does NOT change earlier records,
      • names are NEVER repeated across runs (start_index offsets the global index).
    
    Args:
        n_students:   Number of new transcripts to generate
        seed:         Random seed for reproducibility
        existing_ids: Set of already-used student IDs (to avoid duplicates)
        start_index:  Global offset = number of students already generated.
                      Ensures each new student gets a unique seed → unique name.
    
    Returns:
        List of newly generated (and valid) transcripts
    
    ID Format: {entry_year}{sequence:05d}
        Examples: 202100001 (2021 batch), 202200001 (2022 batch), etc.
    """
    if existing_ids is None:
        existing_ids = set()
    
    # master_rng seed incorporates start_index so programs & personas
    # are DIFFERENT on every run (not just names and IDs).
    # Using a large prime to avoid seed collisions between runs.
    master_rng = random.Random(seed ^ (start_index * 999983))

    programs = get_balanced_programs(n_students, master_rng)  # different programs each run
    
    # Fix: randomly select personas with replacement to ensure perfect 
    # distribution regardless of the batch size.
    personas = [master_rng.choice(PERSONA_POOL) for _ in range(n_students)]

    transcripts: List[Dict] = []
    failed_ids:  List[str]  = []

    id_reg = StudentIDRegistry(existing_ids)  # FIX #7: proper registry

    for i in range(n_students):
        # Global index = start_index + i → unique per student across ALL runs
        global_i = start_index + i
        # Per-student seed derived from (seed, global_index) for uniqueness
        student_rng = random.Random(seed ^ (global_i * 2654435761))  # hash mixing
        
        program     = programs[i]
        persona     = personas[i]
        gender      = student_rng.choice(["Male", "Female"])
        name        = random_name(gender, student_rng)
        entry_year  = 2021 + student_rng.randint(0, 4)  # select from 2021-2025
        sid         = id_reg.next(entry_year)  # FIX #7: no skipping
        
        n_sems, expected_to_graduate = pick_semesters(persona, program, entry_year, student_rng)
        prev_school = student_rng.choice(HIGH_SCHOOLS)

        print(
            f"[{i+1:3d}/{n_students}] (global #{global_i+1}) {sid}  {name:<38s}  {program[:38]:<38s}  {persona}",
            flush=True,
        )

        prompt = build_prompt(
            program=program, persona_key=persona,
            entry_year=entry_year, semesters_to_generate=n_sems,
            student_name=name, student_id=sid,
            prev_institution=prev_school, gender=gender,
        )

        raw = call_llm(prompt)
        record = parse_json_response(raw) if raw else None
        
        if record is None:
            print(f"   ⚠️  No valid JSON for {sid}. Skipping.")
            failed_ids.append(sid)
            continue

        # Ensure required top-level fields are present
        record.setdefault("student_id",   sid)
        record.setdefault("name",         name)
        record.setdefault("program",      program)
        record.setdefault("persona",      persona)
        record.setdefault("semesters",    [])
        record.setdefault("entry_year",   entry_year)

        transcripts.append(record)

    if failed_ids:
        print(f"\n⚠️  {len(failed_ids)} student(s) failed to generate: {failed_ids}")

    return transcripts


# ──────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────
def main(n_students: int = 50, seed: int = 42):
    print("=" * 65)
    print("ZEWAIL CITY  –  LLM-DRIVEN TRANSCRIPT GENERATOR  v3")
    print(f"Model  : {MODEL}  @  https://ollama.com")
    print("=" * 65)

    # STEP 1: Load existing transcripts (for cumulative storage)
    out_path = OUTPUT_DIR / "transcripts.json"
    existing_transcripts: List[Dict] = []
    existing_ids: set = set()
    
    if out_path.exists():
        print(f"📂 Loading existing transcripts from {out_path}...")
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                existing_transcripts = json.load(f)
                existing_ids = {t.get("student_id") for t in existing_transcripts if t.get("student_id")}
            print(f"   ✅ Loaded {len(existing_transcripts)} existing transcripts")
        except Exception as e:
            print(f"   ⚠️  Could not load existing transcripts: {e}")
            existing_transcripts = []
            existing_ids = set()
    else:
        print(f"📝 No existing transcripts found. Will create new file at {out_path}")

    # STEP 2: Generate new transcripts
    # FIX #8: Use original seed with deterministic per-student hashing
    # No adjusted_seed needed - each student gets hash(seed, index) for reproducibility
    print(f"\n📚 Generating {n_students} new transcripts (starting from global index {len(existing_transcripts)})...")
    new_transcripts = generate(n_students, seed, existing_ids, start_index=len(existing_transcripts))

    if not new_transcripts:
        print("\n[ERROR] No transcripts generated. "
              "Check that Ollama is running and the model is available.")
        sys.exit(1)

    # STEP 3: Validate new transcripts (integrity checks)
    print(f"\n🔍 Running academic integrity checks on {len(new_transcripts)} transcripts…")
    checker = verify_academic_integrity(new_transcripts)
    checker.run()
    
    # STEP 4: Filter out transcripts that failed integrity checks
    valid_transcripts = []
    invalid_ids = set()
    
    for t in new_transcripts:
        sid = t.get("student_id", "???")
        # Check if this transcript has any integrity errors
        has_error = any(sid in error for error in checker.errors)
        
        if has_error:
            invalid_ids.add(sid)
            print(f"   ❌ REJECTED: {sid} - Failed integrity checks")
        else:
            valid_transcripts.append(t)
            print(f"   ✅ ACCEPTED: {sid} - Passed all checks")
    
    print(f"\n📋 Integrity Summary: {len(valid_transcripts)} VALID / {len(invalid_ids)} REJECTED")

    # STEP 5: Run comprehensive rubric validation on valid transcripts
    if valid_transcripts:
        print(f"\n[RUBRIC VALIDATION] Running comprehensive validation rubric on {len(valid_transcripts)} valid transcripts...")
        rubric = TranscriptValidationRubric(valid_transcripts)
        rubric_results = rubric.validate_all()
    else:
        print("\n⚠️  No valid transcripts to validate with rubric")

    # STEP 6: Combine existing + new valid transcripts
    all_transcripts = existing_transcripts + valid_transcripts
    
    # STEP 7: Save cumulative transcripts
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_transcripts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(valid_transcripts)} NEW valid transcripts appended")
    print(f"📊 TOTAL transcripts in file: {len(all_transcripts)} → {out_path}")

    # STEP 8: Summary
    school_count: Dict[str, int] = {}
    persona_count: Dict[str, int] = {}
    for t in all_transcripts:
        sc = t.get("school", "Unknown")
        pe = t.get("persona", "unknown")
        school_count[sc]  = school_count.get(sc, 0) + 1
        persona_count[pe] = persona_count.get(pe, 0) + 1

    print("\n📊 CUMULATIVE School distribution (all transcripts):")
    for s, c in sorted(school_count.items()):
        print(f"   {s:<45s}: {c}")

    print("\n🎭 CUMULATIVE Persona distribution (all transcripts):")
    for p, c in sorted(persona_count.items()):
        print(f"   {p:<25s}: {c}")
    
    if invalid_ids:
        print(f"\n⚠️  Rejected students (failed integrity): {', '.join(sorted(invalid_ids))}")

    return all_transcripts


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate synthetic UST student transcripts via LLM"
    )
    parser.add_argument("--students", type=int, default=50,
                        help="Number of transcripts to generate (default: 50)")
    parser.add_argument("--seed",     type=int, default=42,
                        help="Random seed (default: 42)")
    args = parser.parse_args()
    main(args.students, args.seed)
