"""Gateway-side cryptography helpers.

Two independent concerns:

1. **Field encryption** (Fernet) for MFA secrets the gateway writes to Odoo.
   The key must match the one Odoo's ``edu_mang_security`` uses so either side
   can decrypt. Resolution: ``FIELD_ENCRYPTION_KEY`` env first, otherwise the
   key injected at startup from Odoo's ``security.field_encryption_key`` config
   parameter (see :func:`set_field_key`).

2. **Backup encryption** (AES-256-GCM) for ``pg_dump`` output, keyed by a
   32-byte key derived from ``BACKUP_ENCRYPTION_KEY``.
"""
import base64
import hashlib
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------------------------------------------------------------------------
# Field encryption (Fernet) — shared with Odoo edu_mang_security
# ---------------------------------------------------------------------------
_field_key: Optional[bytes] = None
_env_field_key = os.getenv("FIELD_ENCRYPTION_KEY")
if _env_field_key:
    _field_key = _env_field_key.encode()


def set_field_key(key: str) -> None:
    """Inject the field-encryption key fetched from Odoo at startup. The env var
    always wins if it was set."""
    global _field_key
    if _env_field_key:
        return
    if key:
        _field_key = key.encode() if isinstance(key, str) else key


def field_key_available() -> bool:
    return _field_key is not None


def field_encrypt(plaintext: str) -> str:
    if not plaintext:
        return ""
    if _field_key is None:
        raise RuntimeError("Field-encryption key is not configured")
    return Fernet(_field_key).encrypt(plaintext.encode("utf-8")).decode("utf-8")


def field_decrypt(token: str) -> str:
    if not token:
        return ""
    if _field_key is None:
        raise RuntimeError("Field-encryption key is not configured")
    try:
        return Fernet(_field_key).decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Backup encryption (AES-256-GCM)
# ---------------------------------------------------------------------------
def _backup_key() -> bytes:
    raw = os.getenv("BACKUP_ENCRYPTION_KEY")
    if not raw:
        raise RuntimeError(
            "BACKUP_ENCRYPTION_KEY is not set — cannot encrypt/decrypt backups")
    # Derive a stable 32-byte key from whatever string is provided.
    return hashlib.sha256(raw.encode("utf-8")).digest()


def backup_encrypt(data: bytes) -> bytes:
    """AES-256-GCM encrypt; output is ``nonce(12) || ciphertext||tag``."""
    nonce = os.urandom(12)
    ct = AESGCM(_backup_key()).encrypt(nonce, data, None)
    return nonce + ct


def backup_decrypt(blob: bytes) -> bytes:
    nonce, ct = blob[:12], blob[12:]
    return AESGCM(_backup_key()).decrypt(nonce, ct, None)
