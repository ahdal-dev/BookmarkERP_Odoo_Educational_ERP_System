from odoo import models, fields

class Course(models.Model):
    _name = 'education.course'
    _description = 'Course Information'

    name = fields.Char(string='Course Name', required=True)
    course_code = fields.Char(string='Course Code', required=True, copy=False, readonly=True,
                              default=lambda self: self._generate_course_code())
    description = fields.Text(string='Description')
    credits = fields.Integer(string='Credits', default=3)
    duration_hours = fields.Integer(string='Duration (Hours)')
    semester = fields.Char(string='Semester')

    # Relations
    teacher_id = fields.Many2one('education.teacher', string='Instructor')
    student_ids = fields.Many2many('education.student', string='Enrolled Students')

    # Status
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _generate_course_code(self):
        # Generate a unique course code
        last_course = self.search([], order='course_code desc', limit=1)
        if last_course:
            last_id = int(last_course.course_code[3:])  # Remove 'CRS' prefix
            new_id = last_id + 1
        else:
            new_id = 1001
        return f'CRS{new_id:04d}'

    def name_get(self):
        return [(course.id, f'{course.course_code} - {course.name}') for course in self]
