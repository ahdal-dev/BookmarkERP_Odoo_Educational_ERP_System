import hashlib
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


# record_type -> target model + candidate PII text fields to scrub on anonymize.
# Only fields that actually exist on the model are touched, so this stays robust
# across schema differences between modules.
RETENTION_TARGETS = {
    'student_record': {
        'model': 'education.registration',
        'pii': ['notes'],
    },
    'admission': {
        'model': 'school.admission',
        'pii': ['name', 'email', 'phone', 'mobile', 'partner_name',
                'applicant_name', 'street', 'street2', 'description'],
    },
    'petition': {
        'model': 'student.petition',
        'pii': ['description', 'justification', 'student_comment', 'reason'],
    },
    'support_ticket': {
        'model': 'support.ticket',
        'pii': ['description', 'subject', 'requester_email', 'requester_name'],
    },
    'audit_log': {
        'model': 'audit.log',
        'pii': ['actor_login', 'ip', 'detail'],
    },
}


class DataRetentionPolicy(models.Model):
    """A single retention rule: how long to keep a record type, and what to do
    once it expires (archive / anonymize / delete). A daily cron evaluates every
    active policy via :meth:`run_retention`."""
    _name = 'data.retention.policy'
    _description = 'Data Retention Policy'
    _order = 'record_type'

    name = fields.Char(string='Policy Name', required=True)
    record_type = fields.Selection([
        ('student_record', 'Student Records'),
        ('admission', 'Admission Applications'),
        ('petition', 'Petitions'),
        ('support_ticket', 'Support Tickets'),
        ('audit_log', 'Audit Logs'),
    ], string='Record Type', required=True, default='student_record')
    retention_days = fields.Integer(
        string='Retention (days)', required=True, default=2555,
        help='Records older than this many days are subject to the action below.',
    )
    action = fields.Selection([
        ('archive', 'Archive'),
        ('anonymize', 'Anonymize (hash PII)'),
        ('delete', 'Delete'),
    ], string='Action', required=True, default='archive')
    active = fields.Boolean(string='Active', default=True)
    last_run = fields.Datetime(string='Last Run', readonly=True)
    last_purged_count = fields.Integer(string='Last Purged Count', readonly=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _hash_placeholder(value):
        digest = hashlib.sha256((str(value or '')).encode('utf-8')).hexdigest()
        return digest[:12]

    def _expired_records(self):
        """Return the recordset of expired records for this policy (or False if
        the target model is not available in this DB)."""
        self.ensure_one()
        target = RETENTION_TARGETS.get(self.record_type)
        if not target:
            return False
        model_name = target['model']
        if model_name not in self.env:
            _logger.warning("Retention: model %s not installed, skipping %s",
                            model_name, self.record_type)
            return False
        Model = self.env[model_name].sudo()
        cutoff = fields.Datetime.now() - timedelta(days=self.retention_days)
        # include archived rows too, so 'delete' eventually reaps archived records
        domain = [('create_date', '<', fields.Datetime.to_string(cutoff))]
        if 'active' in Model._fields:
            return Model.with_context(active_test=False).search(domain)
        return Model.search(domain)

    def _apply_action(self, records):
        """Apply this policy's action to ``records``; return count affected."""
        self.ensure_one()
        if not records:
            return 0
        Model = records.browse(records.ids)
        action = self.action
        count = len(records)

        if action == 'delete':
            records.unlink()
            return count

        if action == 'archive':
            if 'active' in Model._fields:
                records.write({'active': False})
                return count
            # No archive flag on this model — fall back to anonymize so the
            # policy still minimizes data instead of silently doing nothing.
            action = 'anonymize'

        if action == 'anonymize':
            target = RETENTION_TARGETS.get(self.record_type, {})
            pii_fields = [f for f in target.get('pii', []) if f in Model._fields]
            for rec in records:
                vals = {}
                for fname in pii_fields:
                    field = Model._fields[fname]
                    token = self._hash_placeholder('%s-%s' % (rec.id, fname))
                    if getattr(field, 'type', '') == 'char' and fname in (
                            'email', 'requester_email'):
                        vals[fname] = '%s@redacted.invalid' % token
                    else:
                        vals[fname] = 'anon-%s' % token
                if vals:
                    rec.write(vals)
            return count

        return 0

    # ------------------------------------------------------------------
    # Cron entry point
    # ------------------------------------------------------------------
    @api.model
    def run_retention(self):
        """Evaluate every active policy and apply its action. Called daily by the
        ``ir.cron`` and on-demand from the admin gateway endpoint."""
        AuditLog = self.env['audit.log'].sudo()
        policies = self.sudo().search([('active', '=', True)])
        total = 0
        for policy in policies:
            try:
                records = policy._expired_records()
                if records is False:
                    continue
                count = policy._apply_action(records)
                total += count
                policy.write({
                    'last_run': fields.Datetime.now(),
                    'last_purged_count': count,
                })
                AuditLog.log_event(
                    'data_retention_purge',
                    'warning' if count else 'info',
                    detail='%s/%s: %s record(s)' % (
                        policy.record_type, policy.action, count),
                )
                _logger.info("Retention %s/%s purged %s records",
                             policy.record_type, policy.action, count)
            except Exception as exc:  # never let one policy break the whole run
                _logger.exception("Retention policy %s failed", policy.name)
                AuditLog.log_event(
                    'data_retention_purge', 'critical',
                    detail='%s FAILED: %s' % (policy.record_type, exc),
                )
        return total
