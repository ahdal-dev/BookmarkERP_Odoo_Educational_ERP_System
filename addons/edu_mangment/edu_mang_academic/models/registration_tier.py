from odoo import fields, models


class RegistrationTier(models.Model):
    """A registration tier / window. Students become eligible based on their
    earned credits (seniority), and the window controls when each tier opens."""
    _name = 'education.registration.tier'
    _description = 'Registration Tier / Window'
    _order = 'sequence, min_credits desc'

    name = fields.Char(string='Tier', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    color = fields.Char(string='Color', default='#4caf27')
    min_credits = fields.Integer(string='Min Earned Credits', default=0)
    max_credits = fields.Integer(string='Max Earned Credits', default=0,
                                 help='0 means no upper bound.')
    registration_start = fields.Date(string='Window Opens')
    registration_end = fields.Date(string='Window Closes')
    active = fields.Boolean(string='Active', default=True)
    notify_students = fields.Boolean(
        string='Notify Students', default=True,
        help='Send a notification to eligible students when this window opens.',
    )

    def is_open_now(self):
        self.ensure_one()
        today = fields.Date.today()
        if self.registration_start and today < self.registration_start:
            return False
        if self.registration_end and today > self.registration_end:
            return False
        return True

    def eligible_for(self, earned_credits):
        self.ensure_one()
        if earned_credits < self.min_credits:
            return False
        if self.max_credits and earned_credits > self.max_credits:
            return False
        return True
