from odoo import models, fields

class Enrollment(models.Model):
    _name = 'education.enrollment'
    _description = 'Student Course Enrollment'

    student_id = fields.Many2one('education.student', string='Student', required=True)
    course_id = fields.Many2one('education.course', string='Course', required=True)
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today())
    grade = fields.Char(string='Grade')
    status = fields.Selection([
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ], string='Status', default='enrolled')

    # Prevent duplicate enrollments
    _sql_constraints = [
        ('unique_enrollment', 'unique(student_id, course_id)',
         'Student is already enrolled in this course!')
    ]
