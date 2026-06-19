from odoo import api, fields, models


class EduNotification(models.Model):
    """First-class in-app notification shown in the decoupled React frontend's
    centralized Notifications hub. Created by workflow hooks (petitions,
    registrations, admissions) and read/marked via the FastAPI gateway."""
    _name = 'edu.notification'
    _description = 'In-App Notification'
    _order = 'create_date desc, id desc'
    _rec_name = 'title'

    user_id = fields.Many2one(
        'res.users', string='Recipient', required=True, index=True, ondelete='cascade',
    )
    category = fields.Selection([
        ('petition', 'Petition'),
        ('registration', 'Registration'),
        ('system', 'System'),
        ('other', 'Other'),
    ], string='Category', required=True, default='other', index=True)
    title = fields.Char(string='Title', required=True)
    message = fields.Text(string='Message')
    is_read = fields.Boolean(string='Read', default=False, index=True)
    action_url = fields.Char(string='Action URL')

    @api.model
    def create_for_user(self, user_id, category, title, message=None, action_url=None):
        """Convenience factory used by workflow hooks and the gateway."""
        if not user_id:
            return self.browse()
        return self.sudo().create({
            'user_id': user_id,
            'category': category or 'other',
            'title': title or 'Notification',
            'message': message or '',
            'action_url': action_url or False,
        })
