from odoo import models, fields


class EducationCourse(models.Model):
    """
    Additive extension of the registration course (defined in
    custom_registration) so petitions can be routed to the responsible
    instructor and department. We inherit here instead of editing
    custom_registration to keep that module's concurrency-critical code
    untouched.
    """
    _inherit = 'education.course'

    instructor_user_id = fields.Many2one(
        'res.users',
        string='Instructor (User)',
        help='The internal user who teaches this course. Course-specific '
             'petitions are routed to this user at the Instructor tier.',
    )
    department_id = fields.Many2one(
        'education.department',
        string='Department',
        help='Owning department. Escalated petitions are routed to this '
             "department's Chair.",
    )
