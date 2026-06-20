from odoo import fields, models


class ResUsersSecurity(models.Model):
    """Strong-authentication fields on res.users. The actual TOTP verification
    and password-policy enforcement live in the FastAPI gateway; Odoo just
    persists the (encrypted / hashed) state."""
    _inherit = 'res.users'

    mfa_enabled = fields.Boolean(string='MFA Enabled', default=False, copy=False)
    # Fernet-encrypted base32 TOTP secret (written by the gateway).
    mfa_secret = fields.Char(string='MFA Secret (encrypted)', copy=False)
    # JSON list of hashed one-time backup codes.
    mfa_backup_codes = fields.Text(string='MFA Backup Codes (hashed)', copy=False)
    # JSON list of {salt, hash} records for the last N passwords.
    password_history = fields.Text(string='Password History (hashed)', copy=False)
    password_changed_at = fields.Datetime(string='Password Changed At', copy=False)

    @property
    def SELF_READABLE_FIELDS(self):
        """Allow a user to see whether MFA is enabled on their own account."""
        return super().SELF_READABLE_FIELDS + ['mfa_enabled', 'password_changed_at']
