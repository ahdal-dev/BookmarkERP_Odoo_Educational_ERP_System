from odoo import models, fields


class PetitionDecision(models.Model):
    """
    Immutable audit line recording each ruling made on a petition as it moves
    through the Instructor -> Advisor -> Chair tiers. Provides the approval
    audit trail required by the RBAC matrix.
    """
    _name = 'petition.decision'
    _description = 'Petition Decision (Audit Trail)'
    _order = 'decision_date desc, id desc'

    petition_id = fields.Many2one(
        'student.petition', string='Petition', required=True,
        ondelete='cascade', index=True,
    )
    tier = fields.Selection([
        ('instructor', 'Instructor'),
        ('advisor', 'Academic Advisor'),
        ('chair', 'Department Chair'),
    ], string='Tier', required=True)
    action = fields.Selection([
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('escalate', 'Escalated'),
        ('override', 'Overridden'),
    ], string='Action', required=True)
    user_id = fields.Many2one(
        'res.users', string='Decided By', required=True,
    )
    reason = fields.Text(string='Reason / Comments')
    decision_date = fields.Datetime(
        string='Decision Date', default=fields.Datetime.now, readonly=True,
    )
