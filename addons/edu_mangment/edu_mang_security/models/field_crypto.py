"""Symmetric field-encryption helper (Fernet / AES-128-CBC + HMAC).

The same key is used by the FastAPI gateway (for MFA secrets it writes) and by
the Odoo service-account rotation cron, so both sides can decrypt each other's
ciphertext. Key resolution order:

1. ``FIELD_ENCRYPTION_KEY`` environment variable (urlsafe-base64 Fernet key).
2. ``security.field_encryption_key`` ``ir.config_parameter`` (auto-generated on
   first use / module install).

This is not a model — it's a plain helper imported where needed.
"""
import logging
import os

_logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
except ImportError:  # pragma: no cover - cryptography ships with Odoo deps
    Fernet = None

CONFIG_PARAM = 'security.field_encryption_key'


def ensure_key(env):
    """Return the active Fernet key (bytes), generating + persisting one in the
    config parameter if neither env nor param is set."""
    env_key = os.getenv('FIELD_ENCRYPTION_KEY')
    if env_key:
        return env_key.encode() if isinstance(env_key, str) else env_key

    param = env['ir.config_parameter'].sudo().get_param(CONFIG_PARAM)
    if param:
        return param.encode()

    if Fernet is None:
        raise RuntimeError(
            "cryptography is not installed; cannot generate field-encryption key")
    new_key = Fernet.generate_key()
    env['ir.config_parameter'].sudo().set_param(CONFIG_PARAM, new_key.decode())
    _logger.info("Generated new field-encryption key in ir.config_parameter")
    return new_key


def encrypt(env, plaintext):
    """Encrypt ``plaintext`` (str) -> token (str). Empty input -> ''."""
    if not plaintext:
        return ''
    if Fernet is None:
        _logger.warning("cryptography missing — storing value WITHOUT encryption")
        return plaintext
    token = Fernet(ensure_key(env)).encrypt(plaintext.encode('utf-8'))
    return token.decode('utf-8')


def decrypt(env, token):
    """Decrypt ``token`` (str) -> plaintext (str). Returns '' on any failure."""
    if not token:
        return ''
    if Fernet is None:
        return token
    try:
        return Fernet(ensure_key(env)).decrypt(token.encode('utf-8')).decode('utf-8')
    except Exception:
        _logger.warning("Failed to decrypt field value", exc_info=True)
        return ''
