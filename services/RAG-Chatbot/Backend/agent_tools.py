from datetime import date
from typing import Optional

from odoo_client import search_read, execute_kw, find_student, OdooError, OdooConnectionError
from mq import publish_event, mq_enabled, MQUnavailable, QUEUE_REGISTRATION, QUEUE_PETITION

SYSTEM_DOWN_MSG = (
    "I'm having trouble accessing the student records system right now. "
    "Please try again shortly, or contact Student Services at "
    "studentservices@university.edu."
)

NO_PROFILE_MSG = (
    "I couldn't find a student profile linked to your account. "
    "Please contact the Registrar."
)

PETITION_TYPE_CODES = {
    "grade_appeal": "GRADE_APPEAL",
    "late_registration": "LATE_REG",
    "course_exception": "COURSE_EXCEPTION",
    "prerequisite_waiver": "PREREQ_WAIVER",
    "other": "OTHER",
}

# op.admission.gender is a Selection field restricted to 'm'/'f'.
GENDER_CODES = {
    "male": "m", "m": "m",
    "female": "f", "f": "f",
}

# Standard 4.0 letter-grade scale, used by gpa_calculator.
GRADE_POINTS = {
    "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Two-letter day codes are checked before single-letter ones, e.g. "Th" -> Thursday
# before "T" -> Tuesday. Used to parse education.course.schedule (e.g. "MWF 10:00-11:00").
_DAY_CODES_2 = {
    "mo": "Monday", "tu": "Tuesday", "we": "Wednesday", "th": "Thursday",
    "fr": "Friday", "sa": "Saturday", "su": "Sunday",
}
_DAY_CODES_1 = {
    "m": "Monday", "t": "Tuesday", "w": "Wednesday", "r": "Thursday",
    "f": "Friday", "s": "Saturday",
}


def _parse_schedule_days(schedule: str) -> list:
    days = []
    s = (schedule or "").lower()
    i = 0
    while i < len(s):
        ch = s[i]
        if not ch.isalpha():
            i += 1
            continue
        two = s[i:i + 2]
        if two in _DAY_CODES_2:
            if _DAY_CODES_2[two] not in days:
                days.append(_DAY_CODES_2[two])
            i += 2
            continue
        one = _DAY_CODES_1.get(ch)
        if one:
            if one not in days:
                days.append(one)
            i += 1
            continue
        i += 1
    return sorted(days, key=WEEKDAY_NAMES.index)


def _format_time(value) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "TBD"
    hours = int(value)
    minutes = round((value - hours) * 60)
    if minutes == 60:
        hours += 1
        minutes = 0
    return f"{hours:02d}:{minutes:02d}"


PETITION_STATE_LABELS = {
    "draft": "draft (not yet submitted)",
    "submitted": "submitted, awaiting review",
    "under_review": "under review",
    "approved": "approved",
    "rejected": "rejected",
    "cancelled": "cancelled",
}


def _error_message(e: OdooError) -> str:
    """Turn a caught OdooError into a user-facing message: connection issues get a
    generic 'system unavailable' reply, business/validation errors are shown as-is
    (already cleaned up by odoo_client._clean_fault)."""
    if isinstance(e, OdooConnectionError):
        return SYSTEM_DOWN_MSG
    return str(e)


def course_info(args: dict, student_email: Optional[str]) -> dict:
    course_code = (args.get("course_code") or "").strip()
    action = args.get("action") or "schedule"
    if not course_code:
        return {"ok": False, "message": "Which course code would you like information about?"}

    try:
        rows = search_read(
            "education.course",
            [["code", "=ilike", course_code]],
            ["name", "code", "description", "schedule", "timing_start", "timing_end",
             "instructor", "credits", "available_seats", "total_seats",
             "registration_open", "semester", "year"],
            limit=1,
        )
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}

    if not rows:
        return {"ok": False, "message": f"I couldn't find a course with code {course_code}."}

    c = rows[0]
    status = "open" if c.get("registration_open") else "closed"
    message = (
        f"{c['name']} ({c['code']}), {c.get('credits', 0)} credits. "
        f"Schedule: {c.get('schedule') or 'TBD'} "
        f"({c.get('timing_start', '')}-{c.get('timing_end', '')}). "
        f"Instructor: {c.get('instructor') or 'TBD'}. "
        f"Seats available: {c.get('available_seats', 0)}/{c.get('total_seats', 0)}. "
        f"Registration is currently {status} "
        f"({c.get('semester', '')} {c.get('year', '')})."
    )
    if action == "prerequisites":
        message += " Note: prerequisite information is not tracked in this system."

    return {"ok": True, "data": c, "message": message}


def _enroll_core(student: dict, course_code: str) -> dict:
    """Synchronous enrollment write. Raises OdooError on failure. Shared by the
    direct (MQ-disabled) path and the RabbitMQ worker."""
    courses = search_read(
        "education.course", [["code", "=ilike", course_code]],
        ["id", "name", "code", "credits"], limit=1,
    )
    if not courses:
        return {"ok": False, "message": f"I couldn't find a course with code {course_code}."}
    course = courses[0]
    execute_kw("education.registration", "create", [{
        "student_id": student["id"],
        "course_id": course["id"],
    }])
    return {
        "ok": True,
        "data": course,
        "message": f"You're registered for {course['name']} ({course['code']}), {course.get('credits', 0)} credits.",
    }


def _drop_core(student: dict, course_code: str) -> dict:
    """Synchronous drop write. Raises OdooError on failure. Shared with the worker."""
    regs = search_read(
        "education.registration",
        [["student_id", "=", student["id"]], ["course_id.code", "=ilike", course_code], ["state", "=", "enrolled"]],
        ["id"], limit=1,
    )
    if not regs:
        return {"ok": False, "message": f"You're not currently enrolled in {course_code}."}
    execute_kw("education.registration", "action_drop", [[regs[0]["id"]]])
    return {"ok": True, "message": f"You've been dropped from {course_code}."}


def register_course(args: dict, student_email: Optional[str]) -> dict:
    action = args.get("action") or "check_status"
    course_code = (args.get("course_code") or "").strip()

    if not student_email:
        return {"ok": False, "message": NO_PROFILE_MSG}

    try:
        student = find_student(student_email)
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}

    if not student:
        return {"ok": False, "message": NO_PROFILE_MSG}

    if action in ("register", "drop"):
        if not course_code:
            verb = "register for" if action == "register" else "drop"
            return {"ok": False, "message": f"Which course code would you like to {verb}?"}

        # High-concurrency writes are queued to RabbitMQ to avoid DB locking; a
        # worker performs the actual Odoo write. If the broker is unreachable we
        # fall back to a synchronous write so the request still succeeds.
        if mq_enabled():
            try:
                publish_event(QUEUE_REGISTRATION, {
                    "student_email": student_email,
                    "course_code": course_code,
                    "action": action,
                })
                phrase = "register you for" if action == "register" else "drop you from"
                return {
                    "ok": True,
                    "queued": True,
                    "message": (
                        f"Your request to {phrase} {course_code} has been received and is being "
                        f"processed. You can ask me to check your registration status in a moment."
                    ),
                }
            except MQUnavailable as e:
                print(f"MQ unavailable, falling back to synchronous {action}: {e}")

        try:
            return _enroll_core(student, course_code) if action == "register" else _drop_core(student, course_code)
        except OdooError as e:
            return {"ok": False, "message": _error_message(e)}

    # check_status
    try:
        regs = search_read(
            "education.registration",
            [["student_id", "=", student["id"]], ["state", "=", "enrolled"]],
            ["course_id", "registration_date"],
        )
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}

    if not regs:
        return {"ok": True, "data": [], "message": "You have no active registrations."}

    lines = [f"{r['course_id'][1]} (registered {r['registration_date']})" for r in regs]
    return {"ok": True, "data": regs, "message": "Your active registrations: " + "; ".join(lines)}


def create_petition(args: dict, student_email: Optional[str]) -> dict:
    action = args.get("action") or "submit"

    if not student_email:
        return {"ok": False, "message": NO_PROFILE_MSG}

    try:
        student = find_student(student_email)
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}
    if not student:
        return {"ok": False, "message": NO_PROFILE_MSG}

    if action == "check_status":
        reference = (args.get("reference") or "").strip()
        domain = [["student_id", "=", student["partner_id"][0]]]
        if reference:
            domain.append(["name", "=", reference])

        try:
            petitions = search_read(
                "student.petition", domain,
                ["name", "subject", "state", "petition_type_id", "rejection_reason"],
                limit=5, order="create_date desc",
            )
        except OdooError:
            return {"ok": False, "message": SYSTEM_DOWN_MSG}

        if not petitions:
            if reference:
                return {"ok": False, "message": f"I couldn't find a petition with reference {reference} on your account."}
            return {"ok": True, "data": [], "message": "You don't have any petitions on file yet."}

        lines = []
        for p in petitions:
            label = PETITION_STATE_LABELS.get(p["state"], p["state"])
            type_name = p["petition_type_id"][1] if p.get("petition_type_id") else "Petition"
            line = f"{p['name']} ({type_name} - {p['subject']}): {label}"
            if p["state"] == "rejected" and p.get("rejection_reason"):
                line += f" - {p['rejection_reason']}"
            lines.append(line)

        prefix = "Status: " if reference else "Your recent petitions: "
        return {"ok": True, "data": petitions, "message": prefix + "; ".join(lines)}

    # action == "submit"
    subject = (args.get("subject") or "").strip()
    description = (args.get("description") or "").strip()

    if not subject or not description:
        return {"ok": False, "message": "Could you provide a brief subject and description for your petition?"}

    # Publish the submission to RabbitMQ (202-style accept); a worker writes it to
    # Odoo. Falls back to a synchronous write if the broker is unreachable.
    if mq_enabled():
        try:
            publish_event(QUEUE_PETITION, {
                "student_email": student_email,
                "petition_type": args.get("petition_type") or "other",
                "subject": subject,
                "description": description,
                "course_code": (args.get("course_code") or "").strip(),
            })
            return {
                "ok": True,
                "queued": True,
                "message": (
                    "Your petition has been submitted and is being processed. You'll be able to "
                    "check its status shortly — just ask me to check your recent petitions."
                ),
            }
        except MQUnavailable as e:
            print(f"MQ unavailable, falling back to synchronous petition submit: {e}")

    try:
        return _create_petition_core(student, args)
    except OdooError as e:
        return {"ok": False, "message": _error_message(e)}


def _create_petition_core(student: dict, args: dict) -> dict:
    """Synchronous petition create + submit. Raises OdooError on failure. Shared by
    the direct (MQ-disabled) path and the RabbitMQ worker."""
    petition_type = args.get("petition_type") or "other"
    subject = (args.get("subject") or "").strip()
    description = (args.get("description") or "").strip()
    course_code = (args.get("course_code") or "").strip()

    code = PETITION_TYPE_CODES.get(petition_type, "OTHER")
    ptypes = search_read("petition.type", [["code", "=", code], ["active", "=", True]], ["id", "name"], limit=1)
    if not ptypes:
        ptypes = search_read("petition.type", [["code", "=", "OTHER"], ["active", "=", True]], ["id", "name"], limit=1)
    if not ptypes:
        return {"ok": False, "message": "Petition types are not configured yet — please contact the registrar."}

    if course_code:
        subject = f"[{course_code}] {subject}"

    new_id = execute_kw("student.petition", "create", [{
        "student_id": student["partner_id"][0],
        "petition_type_id": ptypes[0]["id"],
        "subject": subject,
        "description": description,
        "requested_date": str(date.today()),
    }])
    execute_kw("student.petition", "action_submit", [[new_id]])
    created = search_read("student.petition", [["id", "=", new_id]], ["name"], limit=1)
    ref_name = created[0]["name"] if created else str(new_id)

    return {
        "ok": True,
        "data": {"id": new_id, "name": ref_name},
        "message": f"Your {ptypes[0]['name']} petition has been submitted (reference {ref_name}). You can ask me to check its status anytime by giving me that reference.",
    }


def check_holds(args: dict, student_email: Optional[str]) -> dict:
    hold_type = args.get("hold_type") or "all"

    if not student_email:
        return {"ok": False, "message": NO_PROFILE_MSG}

    try:
        student = find_student(student_email)
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}

    if not student:
        return {"ok": False, "message": NO_PROFILE_MSG}

    if not student.get("is_on_hold"):
        return {"ok": True, "data": {"is_on_hold": False}, "message": "You have no active holds on your account."}

    message = (
        f"You have a hold on your account placed on {student.get('hold_date')}: "
        f"{student.get('hold_reason')}. Please contact the office responsible for resolving this."
    )
    if hold_type != "all":
        message += f" (Note: hold categories such as '{hold_type}' aren't tracked separately in this system.)"

    return {"ok": True, "data": student, "message": message}


def student_records(args: dict, student_email: Optional[str]) -> dict:
    action = args.get("action") or "enrollment_verify"

    if action in ("grades", "gpa", "degree_audit"):
        message = (
            "Official grades, GPA, and degree audits aren't available through this "
            "assistant yet — please request them from the Registrar's Office at "
            "registrar@university.edu."
        )
        if action == "gpa":
            message += (
                " If you'd like to estimate a GPA from courses, credits, and grades, "
                "just give me those and I can calculate it for you."
            )
        return {"ok": False, "message": message}

    if not student_email:
        return {"ok": False, "message": NO_PROFILE_MSG}

    try:
        student = find_student(student_email)
        if not student:
            return {"ok": False, "message": NO_PROFILE_MSG}

        regs = search_read(
            "education.registration",
            [["student_id", "=", student["id"]]],
            ["course_id", "state", "registration_date", "dropped_date"],
        )

        course_ids = sorted({r["course_id"][0] for r in regs if r.get("course_id")})
        courses = {}
        if course_ids:
            for c in search_read("education.course", [["id", "in", course_ids]], ["name", "code", "credits", "semester", "year"]):
                courses[c["id"]] = c
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}

    enrolled, dropped = [], []
    total_credits = 0
    for r in regs:
        cid = r["course_id"][0] if r.get("course_id") else None
        c = courses.get(cid, {})
        item = {
            "code": c.get("code"),
            "name": c.get("name"),
            "credits": c.get("credits", 0),
            "semester": c.get("semester"),
            "year": c.get("year"),
            "registration_date": r.get("registration_date"),
            "dropped_date": r.get("dropped_date"),
        }
        if r["state"] == "enrolled":
            enrolled.append(item)
            total_credits += c.get("credits", 0)
        elif r["state"] == "dropped":
            dropped.append(item)

    if action == "transcript":
        if not enrolled and not dropped:
            message = "You have no enrollment records on file yet."
        else:
            groups = {}
            for item, status in [(c, "enrolled") for c in enrolled] + [(c, "dropped") for c in dropped]:
                term = f"{(item['semester'] or '').title()} {item['year'] or ''}".strip() or "Unspecified term"
                groups.setdefault(term, []).append(f"{item['code']} - {item['name']} ({item['credits']} credits, {status})")
            lines = [f"{term}: " + "; ".join(items) for term, items in groups.items()]
            message = (
                "Unofficial enrollment summary (no grades available — for an official "
                "transcript with grades, contact the Registrar's Office at registrar@university.edu):\n"
                + "\n".join(lines)
                + f"\nTotal credits currently enrolled: {total_credits}"
            )
        return {"ok": True, "data": {"enrolled": enrolled, "dropped": dropped, "total_credits": total_credits}, "message": message}

    if not enrolled:
        message = "You have no active enrollments."
    else:
        lines = [f"{c['code']} - {c['name']} ({c['credits']} credits)" for c in enrolled]
        message = f"You're enrolled in {len(enrolled)} course(s), {total_credits} total credits: " + "; ".join(lines)

    if dropped:
        message += f". Dropped courses: " + "; ".join(f"{c['code']} - {c['name']}" for c in dropped)

    return {"ok": True, "data": {"enrolled": enrolled, "dropped": dropped, "total_credits": total_credits}, "message": message}


def gpa_calculator(args: dict, student_email: Optional[str]) -> dict:
    courses = args.get("courses") or []
    current_gpa = args.get("current_gpa")
    current_credits = args.get("current_credits")

    if not courses:
        return {
            "ok": False,
            "message": "Tell me the courses you'd like to include, each with its credit hours and a "
                       "(actual or hypothetical) letter grade, and I'll calculate the GPA.",
        }

    total_points = 0.0
    total_credits = 0.0
    breakdown = []
    unknown = []

    for c in courses:
        label = (c.get("course_code") or "course").strip()
        grade = str(c.get("grade") or "").strip().upper()
        try:
            credits = float(c.get("credits"))
        except (TypeError, ValueError):
            return {"ok": False, "message": f"What are the credit hours for {label}?"}

        points = GRADE_POINTS.get(grade)
        if points is None:
            unknown.append(f"{label} ({grade or 'no grade given'})")
            continue

        total_points += points * credits
        total_credits += credits
        breakdown.append(f"{label}: {grade} ({credits:g} credits)")

    if unknown:
        return {
            "ok": False,
            "message": (
                "I don't recognize the grade for: " + ", ".join(unknown) +
                ". Please use standard letter grades (A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F)."
            ),
        }

    if current_gpa is not None and current_credits:
        try:
            total_points += float(current_gpa) * float(current_credits)
            total_credits += float(current_credits)
        except (TypeError, ValueError):
            pass

    if total_credits == 0:
        return {"ok": False, "message": "I need at least one course with valid credit hours and a recognized letter grade."}

    gpa = round(total_points / total_credits, 2)
    message = f"Estimated GPA: {gpa} (based on {total_credits:g} credit hours: {'; '.join(breakdown)})."
    return {"ok": True, "data": {"gpa": gpa, "total_credits": total_credits}, "message": message}


def semester_schedule(args: dict, student_email: Optional[str]) -> dict:
    semester = (args.get("semester") or "").strip().lower()
    year = args.get("year")

    if not student_email:
        return {"ok": False, "message": NO_PROFILE_MSG}

    try:
        student = find_student(student_email)
        if not student:
            return {"ok": False, "message": NO_PROFILE_MSG}

        regs = search_read(
            "education.registration",
            [["student_id", "=", student["id"]], ["state", "=", "enrolled"]],
            ["course_id"],
        )
        course_ids = sorted({r["course_id"][0] for r in regs if r.get("course_id")})
        courses = []
        if course_ids:
            courses = search_read(
                "education.course", [["id", "in", course_ids]],
                ["code", "name", "schedule", "timing_start", "timing_end", "instructor", "semester", "year", "credits"],
            )
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}

    if not courses:
        return {"ok": True, "data": {}, "message": "You have no active enrollments to build a schedule from."}

    if semester:
        courses = [c for c in courses if (c.get("semester") or "").lower() == semester]
    if year is not None:
        try:
            year_int = int(year)
            courses = [c for c in courses if c.get("year") == year_int]
        except (TypeError, ValueError):
            pass

    if not courses:
        term = " ".join(part for part in [semester.title() if semester else "", str(year) if year is not None else ""] if part)
        return {"ok": True, "data": {}, "message": f"You have no enrolled courses for {term}." if term else "You have no enrolled courses matching that term."}

    grid = {day: [] for day in WEEKDAY_NAMES}
    unscheduled = []
    for c in courses:
        days = _parse_schedule_days(c.get("schedule"))
        start = _format_time(c.get("timing_start"))
        end = _format_time(c.get("timing_end"))
        label = f"{start}-{end} {c['code']} - {c['name']} ({c.get('instructor') or 'TBD'})"
        if not days:
            unscheduled.append(f"{c['code']} - {c['name']} ({c.get('schedule') or 'schedule TBD'})")
            continue
        for day in days:
            grid[day].append((c.get("timing_start") or 0, label))

    lines = []
    for day in WEEKDAY_NAMES:
        entries = sorted(grid[day], key=lambda x: x[0])
        if entries:
            lines.append(f"{day}: " + "; ".join(label for _, label in entries))

    sems = sorted({(c.get("semester") or "").title() for c in courses if c.get("semester")})
    yrs = sorted({c.get("year") for c in courses if c.get("year")})
    term_label = ""
    if sems and yrs:
        term_label = f" for {'/'.join(sems)} {'/'.join(str(y) for y in yrs)}"

    if lines:
        message = f"Weekly schedule template{term_label}:\n" + "\n".join(lines)
    else:
        message = f"No recognizable weekly meeting times in your enrolled courses{term_label}."
    if unscheduled:
        message += "\nCourses with unspecified/irregular meeting times: " + "; ".join(unscheduled)
    total_credits = sum(c.get("credits", 0) for c in courses)
    message += f"\nTotal credits: {total_credits}"

    return {
        "ok": True,
        "data": {"grid": {d: [l for _, l in grid[d]] for d in WEEKDAY_NAMES}, "unscheduled": unscheduled, "total_credits": total_credits},
        "message": message,
    }


def admission_application(args: dict, student_email: Optional[str]) -> dict:
    action = args.get("action") or "start_application"
    course_code = (args.get("course_code") or "").strip()
    full_name = (args.get("full_name") or "").strip()
    email = (args.get("email") or "").strip() or (student_email or "")
    phone = (args.get("phone") or "").strip()
    birth_date = (args.get("birth_date") or "").strip()
    gender = (args.get("gender") or "").strip()

    if action == "check_status":
        if not email:
            return {"ok": False, "message": "What email address was used for the application?"}
        try:
            apps = search_read(
                "op.admission", [["email", "=", email]],
                ["name", "state", "application_date", "course_id"],
                limit=5, order="application_date desc",
            )
        except OdooError:
            return {"ok": False, "message": SYSTEM_DOWN_MSG}

        if not apps:
            return {"ok": False, "message": f"I couldn't find any admission applications for {email}."}

        latest = apps[0]
        course_name = latest["course_id"][1] if latest.get("course_id") else "N/A"
        message = (
            f"Your most recent application ({latest['name']}, for {course_name}) "
            f"is currently '{latest['state']}' (submitted {latest['application_date']})."
        )
        return {"ok": True, "data": apps, "message": message}

    # start_application / submit
    if not (full_name and email and birth_date and gender):
        return {
            "ok": False,
            "message": "To start your application I need your full name, email, date of birth, and gender. Could you provide those?",
        }

    gender_code = GENDER_CODES.get(gender.strip().lower())
    if not gender_code:
        return {"ok": False, "message": "Could you confirm your gender as male or female for the application form?"}

    try:
        regs = search_read(
            "op.admission.register",
            [["active", "=", True], ["course_id", "!=", False]],
            ["id", "name", "course_id", "admission_base"],
            order="id desc",
        )
    except OdooError:
        return {"ok": False, "message": SYSTEM_DOWN_MSG}

    if not regs:
        return {"ok": False, "message": "Admissions are not currently open — please contact the admissions office at admissions@university.edu."}

    register = regs[0]
    note = ""
    if course_code:
        note = f" (filed under the {register['name']} admission cycle, since course-specific cycles aren't available)"

    name_parts = full_name.split()
    if len(name_parts) > 1:
        first_name = " ".join(name_parts[:-1])
        last_name = name_parts[-1]
    else:
        first_name = last_name = full_name

    try:
        new_id = execute_kw("op.admission", "create", [{
            "name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "application_date": str(date.today()),
            "birth_date": birth_date,
            "gender": gender_code,
            "course_id": register["course_id"][0],
            "register_id": register["id"],
        }])
    except OdooError as e:
        return {"ok": False, "message": _error_message(e)}

    return {
        "ok": True,
        "data": {"id": new_id},
        "message": f"Your application has been started (reference #{new_id}){note}. We'll follow up with next steps and required documents.",
    }


# --- RabbitMQ worker entry points --------------------------------------------
# Called by worker.py when consuming queued events. They resolve the student from
# the trusted email in the message and reuse the same core write logic as the
# synchronous path. They may raise OdooError, which the worker handles.

def process_registration_event(payload: dict) -> dict:
    """Perform a queued registration.attempt (enroll/drop)."""
    email = payload.get("student_email")
    course_code = (payload.get("course_code") or "").strip()
    action = payload.get("action")
    if not email:
        return {"ok": False, "message": NO_PROFILE_MSG}
    student = find_student(email)
    if not student:
        return {"ok": False, "message": NO_PROFILE_MSG}
    if action == "register":
        return _enroll_core(student, course_code)
    if action == "drop":
        return _drop_core(student, course_code)
    return {"ok": False, "message": f"Unknown registration action: {action}"}


def process_petition_event(payload: dict) -> dict:
    """Perform a queued petition.submitted event."""
    email = payload.get("student_email")
    if not email:
        return {"ok": False, "message": NO_PROFILE_MSG}
    student = find_student(email)
    if not student:
        return {"ok": False, "message": NO_PROFILE_MSG}
    return _create_petition_core(student, payload)
