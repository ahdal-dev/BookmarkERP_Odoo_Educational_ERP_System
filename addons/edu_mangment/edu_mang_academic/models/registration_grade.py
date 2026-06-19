from odoo import api, fields, models

from .grade_scale import GRADE_SCALE, GRADE_SELECTION


class EducationRegistrationGrade(models.Model):
    """Add a recorded grade (and derived grade points) to each registration so
    the system can compute real cumulative GPA and earned credits."""
    _inherit = 'education.registration'

    grade = fields.Selection(
        GRADE_SELECTION, string='Grade',
        help='Final letter grade for this course registration.',
    )
    grade_points = fields.Float(
        string='Grade Points', compute='_compute_grade_points', store=True, digits=(3, 2),
    )
    is_graded = fields.Boolean(
        string='Graded', compute='_compute_grade_points', store=True,
    )

    @api.depends('grade')
    def _compute_grade_points(self):
        for reg in self:
            if reg.grade:
                reg.grade_points = GRADE_SCALE.get(reg.grade, 0.0)
                reg.is_graded = True
            else:
                reg.grade_points = 0.0
                reg.is_graded = False
