import logging
import secrets
from datetime import timedelta

from odoo import api, fields, models

from . import field_crypto

_logger = logging.getLogger(__name__)


class ServiceAccount(models.Model):
    """A machine credential (e.g. a microservice API key) subject to automated
    rotation. The key is stored Fernet-encrypted; only a 4-char hint is shown in
    listings. The plaintext is returned exactly once, at create/rotate time."""
    _name = 'service.account'
    _description = 'Service Account Credential'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')
    api_key = fields.Char(string='API Key (encrypted)', copy=False)
    api_key_hint = fields.Char(string='Key Hint', copy=False, readonly=True)
    last_rotated = fields.Datetime(string='Last Rotated', readonly=True, copy=False)
    rotation_interval_days = fields.Integer(string='Rotation Interval (days)', default=30)
    active = fields.Boolean(string='Active', default=True)

    @property
    def is_due(self):
        self.ensure_one()
        if not self.last_rotated:
            return True
        due = self.last_rotated + timedelta(days=self.rotation_interval_days or 30)
        return fields.Datetime.now() >= due

    # ------------------------------------------------------------------
    @api.model
    def _generate_key(self):
        return secrets.token_urlsafe(32)

    def rotate_key(self):
        """Generate a new key, store it encrypted, update hint + timestamp, and
        return the plaintext (the only time it is ever exposed)."""
        self.ensure_one()
        plaintext = self._generate_key()
        self.write({
            'api_key': field_crypto.encrypt(self.env, plaintext),
            'api_key_hint': plaintext[-4:],
            'last_rotated': fields.Datetime.now(),
        })
        return plaintext

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # Always start with a freshly generated, encrypted key.
            if not rec.api_key:
                rec.rotate_key()
        return records

    # ------------------------------------------------------------------
    @api.model
    def cron_rotate_due(self):
        """Daily: rotate every active account whose interval has elapsed, log it
        to audit.log, and notify admins via in-app notification."""
        AuditLog = self.env['audit.log'].sudo()
        Notification = self.env['edu.notification'].sudo()
        admin_group = self.env.ref('edu_mang_auth.group_erp_admin', raise_if_not_found=False)
        admin_uids = admin_group.users.ids if admin_group else []

        rotated = 0
        for account in self.sudo().search([('active', '=', True)]):
            if not account.is_due:
                continue
            account.rotate_key()
            rotated += 1
            AuditLog.log_event(
                'service_account_rotation', 'warning',
                detail='Rotated key for service account "%s" (hint ****%s)' % (
                    account.name, account.api_key_hint or ''),
            )
            for uid in admin_uids:
                Notification.create_for_user(
                    uid, 'system',
                    'Service account key rotated',
                    'The API key for "%s" was automatically rotated.' % account.name,
                    action_url='/admin/service-accounts',
                )
            _logger.info("Rotated service account %s", account.name)
        return rotated
