"""Password policy: strength validation + reuse history.

Strength rules (enforced on change-password and admin user creation):
  * >= 12 characters
  * contains uppercase, lowercase, digit, and a special character
  * must not contain the user's name tokens or email local-part
  * must not match any of the last N (=5) passwords

History entries are independent of Odoo's own PBKDF2 password hash — we keep our
own salted PBKDF2 hashes purely to detect reuse, since Odoo's stored hash isn't
directly comparable to a candidate without an auth round-trip.
"""
import hashlib
import hmac
import json
import os
import re
from typing import List, Tuple

HISTORY_LIMIT = 5
_PBKDF2_ITERATIONS = 120_000
_SPECIAL = re.compile(r"[^A-Za-z0-9]")


def validate_password_strength(
    password: str, name: str = "", email: str = ""
) -> Tuple[bool, List[str]]:
    """Return ``(ok, errors)``. ``ok`` is True only when ``errors`` is empty."""
    errors: List[str] = []
    if len(password or "") < 12:
        errors.append("Password must be at least 12 characters long.")
    if not re.search(r"[A-Z]", password or ""):
        errors.append("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password or ""):
        errors.append("Password must contain a lowercase letter.")
    if not re.search(r"\d", password or ""):
        errors.append("Password must contain a digit.")
    if not _SPECIAL.search(password or ""):
        errors.append("Password must contain a special character.")

    lowered = (password or "").lower()
    # Reject if it contains the email local-part.
    if email and "@" in email:
        local = email.split("@", 1)[0].lower()
        if len(local) >= 3 and local in lowered:
            errors.append("Password must not contain your email address.")
    # Reject if it contains any name token of length >= 3.
    for token in re.split(r"[\s._-]+", (name or "").lower()):
        if len(token) >= 3 and token in lowered:
            errors.append("Password must not contain your name.")
            break
    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# Reuse history
# ---------------------------------------------------------------------------
def _hash(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return dk.hex()


def hash_for_history(password: str) -> dict:
    salt = os.urandom(16)
    return {"salt": salt.hex(), "hash": _hash(password, salt)}


def parse_history(raw) -> List[dict]:
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (ValueError, TypeError):
        return []


def matches_any_history(password: str, history: List[dict]) -> bool:
    for entry in history or []:
        try:
            salt = bytes.fromhex(entry["salt"])
            if hmac.compare_digest(_hash(password, salt), entry["hash"]):
                return True
        except (KeyError, ValueError, TypeError):
            continue
    return False


def append_history(password: str, history: List[dict]) -> str:
    """Append the new password's hash, trim to HISTORY_LIMIT, return JSON str."""
    updated = (history or []) + [hash_for_history(password)]
    updated = updated[-HISTORY_LIMIT:]
    return json.dumps(updated)
