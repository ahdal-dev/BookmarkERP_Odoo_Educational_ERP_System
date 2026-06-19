from odoo import api, fields, models


class ResUsersAcademic(models.Model):
    """Computed academic standing for students: cumulative GPA, earned credits,
    class year (by earned credits), and academic standing."""
    _inherit = 'res.users'

    cumulative_gpa = fields.Float(
        string='Cumulative GPA', compute='_compute_academic', store=True, digits=(3, 2),
    )
    earned_credits = fields.Integer(
        string='Earned Credits', compute='_compute_academic', store=True,
    )
    class_year = fields.Selection([
        ('freshman', 'Freshman'),
        ('sophomore', 'Sophomore'),
        ('junior', 'Junior'),
        ('senior', 'Senior'),
    ], string='Class Year', compute='_compute_academic', store=True)
    academic_standing = fields.Selection([
        ('new', 'New'),
        ('deans_list', "Dean's List"),
        ('good', 'Good Standing'),
        ('probation', 'Academic Probation'),
    ], string='Academic Standing', compute='_compute_academic', store=True)

    @api.depends('registration_ids.grade', 'registration_ids.grade_points',
                 'registration_ids.is_graded', 'registration_ids.course_id.credits')
    def _compute_academic(self):
        for user in self:
            graded = user.registration_ids.filtered('is_graded')
            quality_points = 0.0
            gpa_credits = 0
            earned = 0
            for reg in graded:
                credits = reg.course_id.credits or 0
                quality_points += reg.grade_points * credits
                gpa_credits += credits
                if reg.grade_points > 0:
                    earned += credits

            gpa = round(quality_points / gpa_credits, 2) if gpa_credits else 0.0
            user.cumulative_gpa = gpa
            user.earned_credits = earned
            user.class_year = self._class_year_for(earned)
            user.academic_standing = self._standing_for(gpa, bool(graded))

    @staticmethod
    def _class_year_for(earned_credits):
        if earned_credits >= 90:
            return 'senior'
        if earned_credits >= 60:
            return 'junior'
        if earned_credits >= 30:
            return 'sophomore'
        return 'freshman'

    @staticmethod
    def _standing_for(gpa, has_grades):
        if not has_grades:
            return 'new'
        if gpa >= 3.5:
            return 'deans_list'
        if gpa >= 2.0:
            return 'good'
        return 'probation'
