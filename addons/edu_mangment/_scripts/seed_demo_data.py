# -*- coding: utf-8 -*-
"""
Idempotent demo-data seeder for the Bookmark Academic ERP.

Run inside the Odoo shell (full registry, direct ORM):

    venv\\Scripts\\python.exe odoo\\odoo-bin shell -c odoo.conf\\odoo.conf \\
        -d edu_demo_new --no-http < addons\\edu_mangment\\_scripts\\seed_demo_data.py

Seeds (only what's missing): departments + chair, courses (with instructors,
windows, prerequisites), student enrollments across states + grades, advisor
links, sample petitions, support tickets, and audit-log entries. Notifications
are produced automatically by the workflow hooks.
"""

from datetime import date, timedelta

env = env  # noqa: F821  (provided by odoo-bin shell)


def ref(xmlid):
    try:
        return env.ref(xmlid)
    except Exception:
        return None


def get_or_create_user(login, name, group_xmlid):
    User = env['res.users'].sudo()
    user = User.search([('login', '=', login)], limit=1)
    if user:
        return user
    groups = []
    g = ref(group_xmlid)
    if g:
        groups = [(4, g.id)]
    return User.create({
        'login': login, 'name': name, 'email': login,
        'password': 'demo1234', 'groups_id': groups,
    })


print('Seeding demo data...')

# --- Faculty / staff -------------------------------------------------------
instructor = get_or_create_user('instructor.demo@bookmark.edu', 'Dr. Alan Turing',
                                'edu_mang_auth.group_erp_instructor')
advisor = get_or_create_user('advisor.demo@bookmark.edu', 'Dr. Grace Hopper',
                             'edu_mang_auth.group_erp_academic_advisor')
chair = get_or_create_user('chair.demo@bookmark.edu', 'Dr. Edsger Dijkstra',
                           'edu_mang_auth.group_erp_department_chair')

# --- Students --------------------------------------------------------------
students = []
STUDENT_NAMES = [
    'Aya Hassan', 'Omar Khaled', 'Lina Saad', 'Marcus Thorne', 'Elena Lunt',
    'Yusuf Adel', 'Mona Farid', 'Karim Nabil',
]
for i, nm in enumerate(STUDENT_NAMES, start=1):
    students.append(get_or_create_user(f'student{i}.demo@bookmark.edu', nm,
                                       'edu_mang_auth.group_erp_student'))

# advisor links
for s in students:
    if not s.advisor_id:
        s.sudo().write({'advisor_id': advisor.id})

# --- Department ------------------------------------------------------------
Dept = env['education.department'].sudo()
dept = Dept.search([('code', '=', 'CS')], limit=1)
if not dept:
    dept = Dept.create({'name': 'Computer Science', 'code': 'CS', 'chair_id': chair.id})
else:
    dept.write({'chair_id': chair.id})

# --- Courses ---------------------------------------------------------------
Course = env['education.course'].sudo()
today = date.today()
COURSES = [
    ('CS101', 'Introduction to Computer Science', 3, 40, True, 'fall'),
    ('CS201', 'Data Structures', 3, 35, True, 'fall'),
    ('CS301', 'Advanced Algorithms', 3, 30, True, 'fall'),
    ('CS305', 'Machine Learning', 4, 25, True, 'fall'),
    ('MATH200', 'Calculus II', 4, 50, True, 'fall'),
    ('ENG105', 'Academic Writing', 3, 28, True, 'fall'),
]
courses = {}
for code, name, credits, seats, is_open, sem in COURSES:
    c = Course.search([('code', '=', code)], limit=1)
    vals = {
        'name': name, 'code': code, 'credits': credits, 'total_seats': seats,
        'registration_open': is_open, 'semester': sem, 'year': today.year,
        'instructor': instructor.name, 'instructor_user_id': instructor.id,
        'registration_start': today - timedelta(days=10),
        'registration_end': today + timedelta(days=60),
    }
    if c:
        c.write(vals)
    else:
        c = Course.create(vals)
    courses[code] = c

# link courses to department
dept.write({'course_ids': [(6, 0, [c.id for c in courses.values()])]})

# prerequisites: CS201 requires CS101; CS301 requires CS201
courses['CS201'].write({'prerequisite_course_ids': [(6, 0, [courses['CS101'].id])]})
courses['CS301'].write({'prerequisite_course_ids': [(6, 0, [courses['CS201'].id])]})

# --- Enrollments + grades --------------------------------------------------
Reg = env['education.registration'].sudo()


def enroll(student, course, state='enrolled', grade=None):
    existing = Reg.search([('student_id', '=', student.id), ('course_id', '=', course.id)], limit=1)
    if existing:
        reg = existing
    else:
        reg = Reg.create({
            'student_id': student.id, 'course_id': course.id,
            'state': state, 'is_officer_override': True,
        })
    if state and reg.state != state:
        reg.write({'state': state})
    if grade and reg.grade != grade:
        reg.write({'grade': grade})
    return reg


# Past (graded) courses → drive GPA / class year, and satisfy prerequisites.
PAST_GRADES = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'A', 'B+']
for idx, s in enumerate(students):
    # everyone completed CS101 (so CS201 prereq is met) + a couple more graded
    enroll(s, courses['CS101'], 'enrolled', PAST_GRADES[idx % len(PAST_GRADES)])
    enroll(s, courses['MATH200'], 'enrolled', PAST_GRADES[(idx + 1) % len(PAST_GRADES)])
    enroll(s, courses['ENG105'], 'enrolled', PAST_GRADES[(idx + 2) % len(PAST_GRADES)])
    # current (ungraded) enrollment
    enroll(s, courses['CS201'], 'enrolled', None)

# Fill CS305 and add a waitlist to demo the waitlist promotion.
for s in students[:3]:
    enroll(s, courses['CS305'], 'enrolled', None)
for s in students[3:6]:
    enroll(s, courses['CS305'], 'waitlist', None)

# --- Petitions -------------------------------------------------------------
PType = env['petition.type'].sudo()
ptype = PType.search([], limit=1)
if not ptype:
    ptype = PType.create({'name': 'Course Overload', 'code': 'OVERLOAD'})

Petition = env['student.petition'].sudo()
for s in students[:4]:
    partner = s.partner_id
    if not partner:
        continue
    exists = Petition.search([('student_id', '=', partner.id)], limit=1)
    if exists:
        continue
    pet = Petition.create({
        'student_id': partner.id,
        'petition_type_id': ptype.id,
        'subject': 'Request to overload to 19 credits',
        'description': 'Strong academic standing; requesting an additional course this term.',
        'course_id': courses['CS305'].id,
    })
    try:
        pet.action_submit()
    except Exception as exc:  # pragma: no cover
        print('  petition submit skipped:', exc)

# --- Support tickets -------------------------------------------------------
Ticket = env['support.ticket'].sudo()
TICKETS = [
    ('Cannot register — account hold', 'registration', 'high', 'open'),
    ('Forgot my portal password', 'account', 'medium', 'open'),
    ('Transcript shows wrong grade', 'technical', 'medium', 'in_progress'),
]
for i, (subj, cat, prio, state) in enumerate(TICKETS):
    if not Ticket.search([('subject', '=', subj)], limit=1):
        Ticket.create({
            'subject': subj, 'category': cat, 'priority': prio, 'state': state,
            'user_id': students[i % len(students)].id,
            'description': 'Auto-seeded demo ticket.',
        })

# --- Audit log -------------------------------------------------------------
Audit = env['audit.log'].sudo()
if Audit.search_count([]) == 0:
    Audit.log_event('login_success', 'info', user_id=advisor.id, actor_login=advisor.login,
                    ip='10.0.0.9', detail='role=academic_advisor')
    Audit.log_event('config_change', 'warning', user_id=chair.id, actor_login=chair.login,
                    ip='10.0.0.4', detail='Updated registration ruleset')
    Audit.log_event('failed_auth', 'critical', actor_login='unknown',
                    ip='102.44.9.1', detail='3 failed attempts for student1.demo@bookmark.edu')

env.cr.commit()
print('Demo data seeded successfully.')
