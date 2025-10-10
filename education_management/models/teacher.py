from odoo import models, fields

class Teacher(models.Model):
    _name = 'education.teacher'
    _description = 'Teacher Information'

    name = fields.Char(string='Full Name', required=True)
    teacher_id = fields.Char(string='Teacher ID', required=True, copy=False, readonly=True,
                             default=lambda self: self._generate_teacher_id())
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    department = fields.Char(string='Department')
    qualification = fields.Char(string='Qualification')
    experience_years = fields.Integer(string='Years of Experience')
    hire_date = fields.Date(string='Hire Date', default=fields.Date.today())

    # Relations
    course_ids = fields.One2many('education.course', 'teacher_id', string='Courses Taught')

    # Status
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _generate_teacher_id(self):
        # Generate a unique teacher ID
        last_teacher = self.search([], order='teacher_id desc', limit=1)
        if last_teacher:
            last_id = int(last_teacher.teacher_id[3:])  # Remove 'TCH' prefix
            new_id = last_id + 1
        else:
            new_id = 1001
        return f'TCH{new_id:04d}'

    def name_get(self):
        return [(teacher.id, f'{teacher.teacher_id} - {teacher.name}') for teacher in self]
