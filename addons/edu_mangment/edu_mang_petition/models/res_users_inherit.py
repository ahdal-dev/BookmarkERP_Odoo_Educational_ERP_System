from odoo import models, fields


class ResUsers(models.Model):
    """
    Additive extension of res.users to model the advisor relationship used by
    the Academic Advisor petition tier. A student's petitions are routed to
    their assigned advisor.
    """
    _inherit = 'res.users'

    advisor_id = fields.Many2one(
        'res.users',
        string='Academic Advisor',
        help='The Academic Advisor assigned to this student. Cohort/advisee '
             'petitions are routed to this advisor.',
    )
    advisee_ids = fields.One2many(
        'res.users', 'advisor_id', string='Advisees'
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['advisor_id']
