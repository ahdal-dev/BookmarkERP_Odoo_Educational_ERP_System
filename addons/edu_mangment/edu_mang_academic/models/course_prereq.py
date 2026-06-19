from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationCoursePrerequisite(models.Model):
    _inherit = 'education.course'

    prerequisite_course_ids = fields.Many2many(
        'education.course', 'education_course_prereq_rel', 'course_id', 'prereq_id',
        string='Prerequisites',
        help='Courses a student must have passed before enrolling in this one.',
    )


class EducationRegistrationPrerequisite(models.Model):
    _inherit = 'education.registration'

    @api.model_create_multi
    def create(self, vals_list):
        check = self.env['ir.config_parameter'].sudo().get_param('edu.reg.prerequisite_check')
        enforce = str(check).lower() in ('1', 'true', 'yes')
        if enforce:
            for vals in vals_list:
                self._check_prerequisites(vals)
        return super().create(vals_list)

    @api.model
    def _check_prerequisites(self, vals):
        """Block enrolment if the student hasn't passed the course prerequisites."""
        if vals.get('is_officer_override'):
            return
        if vals.get('state') == 'dropped':
            return
        course = self.env['education.course'].sudo().browse(vals.get('course_id'))
        student_id = vals.get('student_id')
        if not course or not course.prerequisite_course_ids or not student_id:
            return

        Reg = self.env['education.registration'].sudo()
        missing = []
        for prereq in course.prerequisite_course_ids:
            passed = Reg.search_count([
                ('student_id', '=', student_id),
                ('course_id', '=', prereq.id),
                ('is_graded', '=', True),
                ('grade_points', '>=', 1.0),
            ])
            if not passed:
                missing.append(prereq.code or prereq.name)
        if missing:
            raise ValidationError(_(
                'Cannot enroll in %s — missing prerequisite(s): %s'
            ) % (course.code or course.name, ', '.join(missing)))
