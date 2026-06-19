from odoo import api, fields, models


class AuditLog(models.Model):
    """Persisted security/audit events. Written best-effort by the API gateway
    (login, role change, config change, data export) and shown in the admin
    Audit Log page."""
    _name = 'audit.log'
    _description = 'Audit Log Entry'
    _order = 'create_date desc, id desc'
    _rec_name = 'event_type'

    event_type = fields.Char(string='Event', required=True, index=True)
    severity = fields.Selection([
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Severity', default='info', index=True)
    user_id = fields.Many2one('res.users', string='Actor')
    actor_login = fields.Char(string='Actor Login')
    ip = fields.Char(string='IP Address')
    detail = fields.Text(string='Detail')

    @api.model
    def log_event(self, event_type, severity='info', user_id=None, actor_login=None, ip=None, detail=None):
        return self.sudo().create({
            'event_type': event_type,
            'severity': severity or 'info',
            'user_id': user_id or False,
            'actor_login': actor_login or '',
            'ip': ip or '',
            'detail': detail or '',
        })
