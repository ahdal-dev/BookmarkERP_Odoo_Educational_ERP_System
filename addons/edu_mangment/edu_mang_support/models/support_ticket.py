from odoo import api, fields, models


class SupportTicket(models.Model):
    """Support ticket + live-chat thread raised by a user and handled by a
    support technician. Uses mail.thread for the conversation."""
    _name = 'support.ticket'
    _description = 'Support Ticket'
    _inherit = ['mail.thread']
    _order = 'create_date desc, id desc'
    _rec_name = 'subject'

    name = fields.Char(string='Reference', default='New', copy=False, readonly=True)
    subject = fields.Char(string='Subject', required=True, tracking=True)
    description = fields.Text(string='Description')
    category = fields.Selection([
        ('technical', 'Technical'),
        ('account', 'Account'),
        ('registration', 'Registration'),
        ('other', 'Other'),
    ], string='Category', default='other')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority', default='medium', tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ], string='Status', default='open', tracking=True)
    channel = fields.Selection([
        ('chat', 'Live Chat'),
        ('ticket', 'Ticket'),
    ], string='Channel', default='ticket')
    user_id = fields.Many2one('res.users', string='Requester', required=True, index=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.name or rec.name == 'New':
                rec.name = 'TKT%05d' % rec.id
        return records

    def post_message(self, body, author_id=None):
        """Append a chat/ticket message to the thread."""
        self.ensure_one()
        self.message_post(body=body, author_id=author_id)
        return True
