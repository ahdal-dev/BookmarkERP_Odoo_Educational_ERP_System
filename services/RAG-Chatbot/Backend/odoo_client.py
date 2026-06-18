import os
import re
import xmlrpc.client
from typing import Any, Optional

ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8081")
ODOO_DB = os.getenv("ODOO_DB", "edu_demo_new")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "admin")


class OdooError(Exception):
    """A business/validation error raised by an Odoo model (safe to show to the user)."""
    pass


class OdooConnectionError(OdooError):
    """Odoo is unreachable or authentication failed (not safe to show raw details)."""
    pass


_uid: Optional[int] = None


def _clean_fault(fault_string: str) -> str:
    """Reduce an Odoo XML-RPC fault traceback to a short, user-facing message."""
    m = re.search(r'(?:odoo\.exceptions\.\w+|UserError|ValidationError|ValueError):\s*(.+)', fault_string)
    msg = m.group(1).strip() if m else None
    if not msg:
        lines = [l.strip() for l in fault_string.strip().splitlines() if l.strip()]
        msg = lines[-1] if lines else fault_string.strip()
    # Odoo often wraps the message as a tuple repr, e.g. ('Some message', None)
    m2 = re.match(r"^\(['\"](.+?)['\"]\s*,?\s*(?:None)?\)$", msg)
    if m2:
        msg = m2.group(1)
    return msg


def _get_uid() -> int:
    global _uid
    if _uid is None:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        try:
            _uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        except Exception as e:
            raise OdooConnectionError(f"Odoo authentication failed: {e}")
        if not _uid:
            raise OdooConnectionError("Odoo authentication failed: invalid credentials")
    return _uid


def _models():
    return xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def execute_kw(model: str, method: str, args: list, kwargs: Optional[dict] = None) -> Any:
    uid = _get_uid()
    try:
        return _models().execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD, model, method, args, kwargs or {}
        )
    except xmlrpc.client.Fault as e:
        # Some Odoo action methods (e.g. action_submit) return None; the server's
        # XML-RPC response encoder rejects that ("cannot marshal None"). The method
        # has already run and committed, so treat it as a successful void return.
        if "cannot marshal None" in (e.faultString or ""):
            return None
        raise OdooError(_clean_fault(e.faultString))
    except (ConnectionError, OSError) as e:
        raise OdooConnectionError(f"Cannot reach Odoo at {ODOO_URL}: {e}")


def search_read(model: str, domain: list, fields: list, limit: Optional[int] = None,
                 order: Optional[str] = None) -> list:
    kwargs = {"fields": fields}
    if limit:
        kwargs["limit"] = limit
    if order:
        kwargs["order"] = order
    return execute_kw(model, "search_read", [domain], kwargs)


def find_student(email: str) -> Optional[dict]:
    rows = search_read(
        "res.users",
        [["login", "=", email]],
        ["id", "partner_id", "is_on_hold", "hold_reason", "hold_date"],
        limit=1,
    )
    return rows[0] if rows else None
