from odoo import api, fields, models


class EducationCourseWaitlist(models.Model):
    _inherit = 'education.course'

    def _promote_waitlist(self):
        """Promote oldest (FIFO) waitlisted students into freed seats."""
        Reg = self.env['education.registration'].sudo()
        Notif = self.env['edu.notification'].sudo()
        for course in self:
            course._compute_available_seats()
            seats = course.available_seats
            if seats <= 0:
                continue
            waiting = Reg.search(
                [('course_id', '=', course.id), ('state', '=', 'waitlist')],
                order='registration_date asc',
            )
            for reg in waiting:
                if seats <= 0:
                    break
                student = reg.student_id
                if student and student.is_on_hold:
                    continue
                reg.write({'state': 'enrolled'})
                seats -= 1
                if student:
                    Notif.create_for_user(
                        student.id, 'registration', 'Enrolled from the waitlist',
                        'A seat opened in %s and you were automatically enrolled.'
                        % (course.code or course.name or 'a course'),
                        '/registration',
                    )
            course._compute_available_seats()


class EducationRegistrationWaitlist(models.Model):
    _inherit = 'education.registration'

    def action_drop(self, is_officer_override=False):
        res = super().action_drop(is_officer_override=is_officer_override)
        # A seat just freed — pull from the waitlist immediately.
        self.course_id._promote_waitlist()
        return res

    @api.model
    def cron_promote_waitlist(self):
        """Safety-net: sweep courses with free seats and promote waitlists."""
        courses = self.env['education.course'].sudo().search([('available_seats', '>', 0)])
        courses._promote_waitlist()
