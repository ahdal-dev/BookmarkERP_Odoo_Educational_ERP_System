"""
Seed test data for the Academic Agent chatbot.

Injects the records the 8 chatbot tools read/write, via Odoo XML-RPC (the ORM —
so computed fields, sequences and constraints are respected; do NOT raw-INSERT
into Postgres for these models). Idempotent: re-running updates instead of
duplicating.

Tables (Odoo model -> Postgres table) populated:
  res.users / res.partner        -> res_users / res_partner   (students + holds)
  education.course               -> education_course          (course catalog)
  education.registration         -> education_registration    (enrollments)
  petition.type                  -> petition_type             (petition categories)
  student.petition               -> student_petition          (a sample petition)
  op.course                      -> op_course                 (admissions: course)
  op.admission.register          -> op_admission_register     (admissions: cycle)
  op.admission                   -> op_admission              (a sample application)

Run:
  cd services/RAG-Chatbot && make seed
  # or:  cd services/RAG-Chatbot/Backend && ../venv/Scripts/python.exe seed_chatbot_test_data.py
Reads ODOO_URL/ODOO_DB/ODOO_USERNAME/ODOO_PASSWORD from services/RAG-Chatbot/.env
(defaults: http://localhost:8081 / edu_demo_new / admin / admin).
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except Exception:
    pass

# odoo_client reads ODOO_* env at import time and talks XML-RPC as the admin account.
from odoo_client import execute_kw, search_read  # noqa: E402

YEAR = 2024

# ---------------------------------------------------------------------------
# Student users  (res.users)  — login MUST equal the email the chatbot uses.
# Password lets them log in to the React app; group makes them a "student".
# Format per user: (login/email, full name, password, on_hold, hold_reason)
# ---------------------------------------------------------------------------
STUDENTS = [
    ("student@test.com", "Test Student", "student123", False, None),
    ("held.student@test.com", "Held Student", "student123", True,
     "Outstanding library fines ($45) and an unreturned laptop. "
     "Contact the Library and Student Accounts to clear this hold."),
]

# Course this student is enrolled in (for schedule / records / "my courses").
ENROLL_FOR = "student@test.com"
ENROLL_CODES = ["CS101", "MATH200", "PHYS210"]

# ---------------------------------------------------------------------------
# Course catalog  (education.course)
# ---------------------------------------------------------------------------
COURSES = [
    {"code": "CS101", "name": "Introduction to Computer Science",
     "description": "Foundations of programming and computational thinking.",
     "schedule": "MWF 10:00-11:00", "timing_start": 10.0, "timing_end": 11.0,
     "instructor": "Dr. Alan Turing", "credits": 3, "total_seats": 30,
     "registration_open": True, "semester": "fall", "year": YEAR},
    {"code": "MATH200", "name": "Calculus II",
     "description": "Integration techniques, sequences and series.",
     "schedule": "TR 09:00-10:30", "timing_start": 9.0, "timing_end": 10.5,
     "instructor": "Dr. Katherine Johnson", "credits": 4, "total_seats": 25,
     "registration_open": True, "semester": "fall", "year": YEAR},
    {"code": "BIO102", "name": "General Biology",
     "description": "Cell biology, genetics and evolution.",
     "schedule": "MWF 13:00-14:00", "timing_start": 13.0, "timing_end": 14.0,
     "instructor": "Dr. Rosalind Franklin", "credits": 3, "total_seats": 40,
     "registration_open": False, "semester": "fall", "year": YEAR},
    {"code": "PHYS210", "name": "Classical Mechanics",
     "description": "Newtonian mechanics, energy and momentum.",
     "schedule": "TR 11:00-12:30", "timing_start": 11.0, "timing_end": 12.5,
     "instructor": "Dr. Richard Feynman", "credits": 3, "total_seats": 35,
     "registration_open": True, "semester": "fall", "year": YEAR},
    {"code": "ENG105", "name": "Academic Writing",
     "description": "Composition, rhetoric and research writing.",
     "schedule": "MW 15:00-16:30", "timing_start": 15.0, "timing_end": 16.5,
     "instructor": "Prof. Maya Angelou", "credits": 3, "total_seats": 28,
     "registration_open": True, "semester": "fall", "year": YEAR},
]

# ---------------------------------------------------------------------------
# Petition categories  (petition.type)  — codes the agent maps to.
# ---------------------------------------------------------------------------
PETITION_TYPES = [
    ("GRADE_APPEAL", "Grade Appeal"),
    ("LATE_REG", "Late Registration"),
    ("COURSE_EXCEPTION", "Course Exception"),
    ("PREREQ_WAIVER", "Prerequisite Waiver"),
    ("OTHER", "Other"),
]


def _student_group_id():
    rows = search_read("ir.model.data",
                       [["module", "=", "edu_mang_auth"], ["name", "=", "group_erp_student"]],
                       ["res_id"], limit=1)
    return rows[0]["res_id"] if rows else None


def ensure_students():
    gid = _student_group_id()
    result = {}
    for login, name, password, on_hold, reason in STUDENTS:
        hold_vals = {
            "is_on_hold": on_hold,
            "hold_reason": reason or False,
            "hold_date": str(date.today()) if on_hold else False,
        }
        existing = search_read("res.users", [["login", "=", login]], ["id"], limit=1)
        if existing:
            uid = existing[0]["id"]
            execute_kw("res.users", "write", [[uid], hold_vals])
            print(f"  user OK (exists): {login} (uid={uid}) hold={on_hold}")
        else:
            vals = {"name": name, "login": login, "password": password,
                    "email": login, **hold_vals}
            if gid:
                # Odoo 19 renamed res.users.groups_id -> group_ids.
                vals["group_ids"] = [(4, gid)]
            try:
                uid = execute_kw("res.users", "create", [vals])
                print(f"  user CREATED: {login} (uid={uid}) hold={on_hold}")
            except Exception as e:  # noqa: BLE001
                print(f"  user SKIP (create failed) {login}: {e}")
                continue
        result[login] = uid
    return result


def ensure_courses():
    ids = {}
    for c in COURSES:
        existing = search_read("education.course", [["code", "=", c["code"]]], ["id"], limit=1)
        if existing:
            cid = existing[0]["id"]
            execute_kw("education.course", "write", [[cid], c])
            print(f"  course OK (updated): {c['code']}")
        else:
            cid = execute_kw("education.course", "create", [c])
            print(f"  course CREATED: {c['code']}")
        ids[c["code"]] = cid
    return ids


def ensure_registrations(student_uid, course_ids):
    for code in ENROLL_CODES:
        cid = course_ids.get(code)
        if not cid:
            continue
        existing = search_read(
            "education.registration",
            [["student_id", "=", student_uid], ["course_id", "=", cid], ["state", "=", "enrolled"]],
            ["id"], limit=1)
        if existing:
            print(f"  enrollment OK (exists): {code}")
            continue
        # is_officer_override bypasses registration_open / seat / hold checks during seeding.
        execute_kw("education.registration", "create",
                   [{"student_id": student_uid, "course_id": cid, "is_officer_override": True}])
        print(f"  enrollment CREATED: {code}")


def ensure_petition_sequence():
    """The student.petition reference (e.g. SP00001) comes from this ir.sequence.
    Without it, every petition is named 'New' and reference lookups fail."""
    existing = search_read("ir.sequence", [["code", "=", "student.petition"]], ["id"], limit=1)
    if existing:
        print("  petition sequence OK")
        return
    execute_kw("ir.sequence", "create", [{
        "name": "Student Petition", "code": "student.petition",
        "prefix": "SP", "padding": 5, "number_increment": 1, "number_next": 1,
    }])
    print("  petition sequence CREATED (prefix SP)")


def ensure_petition_types():
    ids = {}
    for code, name in PETITION_TYPES:
        existing = search_read("petition.type", [["code", "=", code]], ["id"], limit=1)
        if existing:
            ids[code] = existing[0]["id"]
            print(f"  petition.type OK: {code}")
        else:
            ids[code] = execute_kw("petition.type", "create",
                                   [{"code": code, "name": name, "active": True}])
            print(f"  petition.type CREATED: {code}")
    return ids


def seed_sample_petition(student_uid):
    u = search_read("res.users", [["id", "=", student_uid]], ["partner_id"], limit=1)
    if not u or not u[0].get("partner_id"):
        print("  sample petition SKIP: student has no partner")
        return
    pid = u[0]["partner_id"][0]
    marker = "[CS101] Late registration (seed)"
    existing = search_read("student.petition",
                           [["student_id", "=", pid], ["subject", "=", marker]], ["id"], limit=1)
    if existing:
        print("  sample petition OK (exists)")
        return
    pt = search_read("petition.type", [["code", "=", "LATE_REG"]], ["id"], limit=1)
    if not pt:
        print("  sample petition SKIP: LATE_REG type missing")
        return
    try:
        nid = execute_kw("student.petition", "create", [{
            "student_id": pid,
            "petition_type_id": pt[0]["id"],
            "subject": marker,
            "description": "Seeded petition: missed the deadline due to a documented medical emergency.",
            "requested_date": str(date.today()),
        }])
        execute_kw("student.petition", "action_submit", [[nid]])
        ref = search_read("student.petition", [["id", "=", nid]], ["name"], limit=1)
        print(f"  sample petition CREATED: {ref[0]['name'] if ref else nid}")
    except Exception as e:  # noqa: BLE001
        print(f"  sample petition WARN: {e}")


def seed_admissions():
    """Best-effort: ensure an active admission cycle (op.admission.register) tied to
    an op.course, plus one sample application for status-lookup testing."""
    try:
        courses = search_read("op.course", [], ["id"], limit=1)
        cid = courses[0]["id"] if courses else execute_kw(
            "op.course", "create", [{"name": "General Studies", "code": "GEN"}])

        regs = search_read("op.admission.register",
                           [["active", "=", True], ["course_id", "!=", False]], ["id"], limit=1)
        if regs:
            rid = regs[0]["id"]
            print("  admission cycle OK (exists)")
        else:
            rid = execute_kw("op.admission.register", "create", [{
                "name": "QA Admission Cycle %s" % YEAR,
                "course_id": cid, "admission_base": "course", "state": "application",
                "min_count": 1, "max_count": 50,
            }])
            print(f"  admission cycle CREATED (id={rid})")

        sample = "existing.applicant@example.com"
        if not search_read("op.admission", [["email", "=", sample]], ["id"], limit=1):
            execute_kw("op.admission", "create", [{
                "name": "Existing Applicant", "first_name": "Existing", "last_name": "Applicant",
                "email": sample, "birth_date": "2001-03-10", "gender": "m",
                "application_date": str(date.today()), "course_id": cid, "register_id": rid,
            }])
            print(f"  sample admission CREATED: {sample}")
        else:
            print("  sample admission OK (exists)")
    except Exception as e:  # noqa: BLE001
        print(f"  admissions WARN (OpenEduCat setup may need attention): {e}")


def main():
    print("Seeding Academic Agent chatbot test data...")
    print("[1/6] petition types");      ensure_petition_sequence(); ensure_petition_types()
    print("[2/6] courses");             course_ids = ensure_courses()
    print("[3/6] students");            users = ensure_students()
    print("[4/6] enrollments")
    if ENROLL_FOR in users:
        ensure_registrations(users[ENROLL_FOR], course_ids)
    else:
        print(f"  SKIP: {ENROLL_FOR} not available")
    print("[5/6] sample petition")
    if ENROLL_FOR in users:
        seed_sample_petition(users[ENROLL_FOR])
    print("[6/6] admissions");          seed_admissions()
    print("\nDone. Log in as student@test.com / student123 (no holds) or "
          "held.student@test.com / student123 (on hold) to test.")


if __name__ == "__main__":
    main()
