from odoo import api, models


class StudentPetitionNotify(models.Model):
    _inherit = 'student.petition'

    def _push_notification(self, category, title, message, url='/student/petitions'):
        """Create a notification for the petitioning student's user account."""
        self.ensure_one()
        if not self.student_id:
            return
        user = self.env['res.users'].sudo().search(
            [('partner_id', '=', self.student_id.id)], limit=1)
        if user:
            self.env['edu.notification'].create_for_user(
                user.id, category, title, message, url)

    def action_submit(self):
        res = super().action_submit()
        for pet in self:
            pet._push_notification(
                'petition', 'Petition submitted',
                'Your petition "%s" has been submitted for review.' % (pet.subject or ''))
        return res

    def action_approve(self):
        res = super().action_approve()
        for pet in self:
            pet._push_notification(
                'petition', 'Petition approved',
                'Your petition "%s" was approved.' % (pet.subject or ''))
        return res

    def action_reject(self):
        res = super().action_reject()
        for pet in self:
            pet._push_notification(
                'petition', 'Petition decision',
                'A decision was recorded on your petition "%s".' % (pet.subject or ''))
        return res


class EducationRegistrationNotify(models.Model):
    _inherit = 'education.registration'

    def _notify_student(self, title, message):
        self.ensure_one()
        if self.student_id:
            self.env['edu.notification'].create_for_user(
                self.student_id.id, 'registration', title, message, '/registration')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for reg in records:
            course = reg.course_name or reg.course_code or 'a course'
            state = reg.state
            if state == 'enrolled':
                reg._notify_student('Enrollment confirmed', 'You are now enrolled in %s.' % course)
            elif state == 'waitlist':
                reg._notify_student('Added to waitlist', 'You joined the waitlist for %s.' % course)
        return records


class SchoolAdmissionNotify(models.Model):
    _inherit = 'school.admission'

    def _notify_applicant(self, title, message):
        """Notify the applicant's user account if one exists (created on accept)."""
        self.ensure_one()
        login = self.generated_login_email or self.email
        if not login:
            return
        user = self.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        if user:
            self.env['edu.notification'].create_for_user(
                user.id, 'system', title, message, '/admissions/status')

    def action_accept(self):
        res = super().action_accept()
        for adm in self:
            adm._notify_applicant('Application accepted',
                                  'Congratulations! Your application has been accepted.')
        return res

    def action_reject(self):
        res = super().action_reject()
        for adm in self:
            adm._notify_applicant('Application update',
                                  'A decision has been recorded on your application.')
        return res
