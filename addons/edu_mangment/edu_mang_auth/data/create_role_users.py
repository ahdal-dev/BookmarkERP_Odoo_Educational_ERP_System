# Creates demo users for the 6 additional RBAC roles via the Odoo shell.
# Run with the FULLY-LOADED registry so res.partner defaults (e.g.
# account.autopost_bills) are applied — this is why it is NOT in demo_users.xml.
#
# Usage:
#   venv\Scripts\python.exe odoo\odoo-bin shell -c odoo.conf\odoo.conf \
#       -d edu_demo_new --no-http < addons/edu_mangment/edu_mang_auth/data/create_role_users.py

ROLE_USERS = [
    ("Instructor Test",  "instructor@test.com",  "instructor123",  "edu_mang_auth.group_erp_instructor"),
    ("Advisor Test",     "advisor@test.com",     "advisor123",     "edu_mang_auth.group_erp_academic_advisor"),
    ("Chair Test",       "chair@test.com",       "chair123",       "edu_mang_auth.group_erp_department_chair"),
    ("Registrar Test",   "registrar@test.com",   "registrar123",   "edu_mang_auth.group_erp_registrar"),
    ("Support Test",     "support@test.com",      "support123",     "edu_mang_auth.group_erp_support_technician"),
    ("Prospective Test", "prospective@test.com", "prospective123", "edu_mang_auth.group_erp_prospective_student"),
]

Users = env["res.users"].with_context(no_reset_password=True)

for name, login, password, group_xmlid in ROLE_USERS:
    group = env.ref(group_xmlid)
    existing = Users.search([("login", "=", login)], limit=1)
    if existing:
        existing.write({"group_ids": [(4, group.id)], "password": password, "active": True})
        print(f"[updated] {login} -> {group_xmlid}")
    else:
        Users.create({
            "name": name,
            "login": login,
            "password": password,
            "email": login,
            "group_ids": [(6, 0, [group.id])],
            "active": True,
        })
        print(f"[created] {login} -> {group_xmlid}")

env.cr.commit()
print("Done. Committed role demo users.")
