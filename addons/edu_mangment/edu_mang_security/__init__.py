from . import models


def post_init_hook(env):
    """Initialise the field-encryption key and stamp password_changed_at on
    existing internal users so the 90-day expiry check doesn't fire on day one."""
    from odoo import fields as odoo_fields
    from .models import field_crypto

    # Ensure the symmetric field-encryption key exists (used for MFA secrets and
    # service-account API keys). No-op if FIELD_ENCRYPTION_KEY env or the config
    # parameter is already set.
    field_crypto.ensure_key(env)

    users = env['res.users'].sudo().search([
        ('share', '=', False),
        ('password_changed_at', '=', False),
    ])
    if users:
        users.write({'password_changed_at': odoo_fields.Datetime.now()})
