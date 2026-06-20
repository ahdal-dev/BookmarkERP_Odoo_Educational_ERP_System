# -*- coding: utf-8 -*-
"""
Rotate all demo/test user passwords to policy-compliant values and pre-enrol MFA
for the privileged accounts (admin@test.com, registrar@test.com, admin superuser).

Run via the Odoo shell:
  venv\\Scripts\\python.exe odoo\\odoo-bin shell -c odoo.conf\\odoo.conf -d edu_demo_new --no-http < addons\\edu_mangment\\_scripts\\set_secure_passwords.py

It is idempotent: missing test users are created with the correct security group,
and held.student@test.com is created with a registration hold.

Passwords intentionally avoid the role word / email local-part so they pass the
gateway's full password validator (>=12, upper+lower+digit+special, no name/email
substring). The literal "<Role>Secure#2026" pattern would fail that name rule.
"""
import base64
import hashlib
import json
import os
import secrets

from odoo import fields

try:
    from odoo.addons.edu_mang_security.models import field_crypto
except Exception:  # pragma: no cover
    field_crypto = None

# login, password, display name, role group xmlid, extra vals
USERS = [
    ("student@test.com",      "ScholarSecure#2026",   "Student Test",     "edu_mang_auth.group_erp_student",            {}),
    ("held.student@test.com", "OnHoldSecure#2026",    "Held Student",     "edu_mang_auth.group_erp_student",            {"is_on_hold": True, "hold_reason": "Demo registration hold"}),
    ("instructor@test.com",   "TeacherSecure#2026",   "Instructor Test",  "edu_mang_auth.group_erp_instructor",         {}),
    ("advisor@test.com",      "MentorSecure#2026",    "Advisor Test",     "edu_mang_auth.group_erp_academic_advisor",   {}),
    ("chair@test.com",        "DeanboardSecure#2026", "Chair Test",       "edu_mang_auth.group_erp_department_chair",   {}),
    ("registrar@test.com",    "RecordsSecure#2026",   "Registrar Test",   "edu_mang_auth.group_erp_registrar",          {}),
    ("support@test.com",      "HelpdeskSecure#2026",  "Support Test",     "edu_mang_auth.group_erp_support_technician", {}),
    ("officer@test.com",      "AdmitSecure#2026",     "Officer Test",     "edu_mang_auth.group_erp_admission_officer",  {}),
    ("prospective@test.com",  "ApplicantSecure#2026", "Prospective Test", "edu_mang_auth.group_erp_prospective_student",{}),
    ("admin@test.com",        "ControlSecure#2026",   "Admin Test",       "edu_mang_auth.group_erp_admin",              {}),
    ("admin",                 "MasterSecure#2026",    None,               None,                                         {}),
]

MFA_LOGINS = {"admin@test.com", "registrar@test.com", "admin"}
ISSUER = "Bookmark Academic ERP"

now = fields.Datetime.now()
emitted_mfa = {}


def _gen_secret():
    return base64.b32encode(os.urandom(20)).decode("ascii").rstrip("=")


def _gen_backup_codes(n=10):
    return ["%s-%s" % (secrets.token_hex(2).upper(), secrets.token_hex(2).upper())
            for _ in range(n)]


def _hash_code(code):
    return hashlib.sha256(code.strip().upper().encode("utf-8")).hexdigest()


def _otpauth(login, secret):
    iss = ISSUER.replace(" ", "%20")
    return "otpauth://totp/%s:%s?secret=%s&issuer=%s" % (iss, login, secret, iss)


# Ensure the password-expiry window is set explicitly.
env["ir.config_parameter"].sudo().set_param("auth.password_expiry_days", "90")
# Ensure the field-encryption key exists (so MFA secrets encrypt/decrypt).
if field_crypto:
    field_crypto.ensure_key(env)

for login, password, name, group_xmlid, extra in USERS:
    user = env["res.users"].sudo().search([("login", "=", login)], limit=1)
    if not user:
        if not group_xmlid:
            print("  ! superuser '%s' not found, skipping" % login)
            continue
        group = env.ref(group_xmlid, raise_if_not_found=False)
        vals = {
            "name": name or login,
            "login": login,
            "email": login if "@" in login else False,
            "password": password,
        }
        if group:
            vals["groups_id"] = [(6, 0, [group.id])]
        user = env["res.users"].sudo().create(vals)
        print("  + created %s" % login)

    write_vals = {
        "password": password,
        "password_history": False,
        "password_changed_at": now,
    }
    # Apply extra fields only if present on the model (e.g. is_on_hold).
    for k, v in extra.items():
        if k in user._fields:
            write_vals[k] = v
    user.sudo().write(write_vals)

    # Pre-enrol MFA for privileged accounts.
    if login in MFA_LOGINS and field_crypto:
        secret = _gen_secret()
        codes = _gen_backup_codes()
        user.sudo().write({
            "mfa_enabled": True,
            "mfa_secret": field_crypto.encrypt(env, secret),
            "mfa_backup_codes": json.dumps([_hash_code(c) for c in codes]),
        })
        emitted_mfa[login] = {"secret": secret, "uri": _otpauth(login, secret), "codes": codes}
        print("  * MFA enrolled for %s" % login)
    else:
        # Make sure non-privileged accounts have MFA off.
        if "mfa_enabled" in user._fields:
            user.sudo().write({"mfa_enabled": False, "mfa_secret": False, "mfa_backup_codes": False})

    print("  = %s -> %s" % (login, password))

env.cr.commit()

print("\n" + "=" * 70)
print("MFA SECRETS (scan into an authenticator app, or enter the secret):")
print("=" * 70)
for login, m in emitted_mfa.items():
    print("\n[%s]" % login)
    print("  secret    : %s" % m["secret"])
    print("  otpauth   : %s" % m["uri"])
    print("  backup    : %s" % ", ".join(m["codes"]))
print("\nDone. All passwords rotated; MFA enrolled for: %s" % ", ".join(emitted_mfa.keys()))
