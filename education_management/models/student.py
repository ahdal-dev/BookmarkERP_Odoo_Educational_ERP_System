from odoo import models, fields, api

class Student(models.Model):
    _name = 'education.student'
    _description = 'Student Information'

    name = fields.Char(string='Full Name', required=True)
    student_id = fields.Char(string='Student ID', required=True, copy=False, readonly=True,
                             default=lambda self: self._generate_student_id())
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')
    date_of_birth = fields.Date(string='Date of Birth')
    address = fields.Text(string='Address')

    # Academic Information
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today())
    current_semester = fields.Char(string='Current Semester')
    gpa = fields.Float(string='GPA', digits=(3, 2))

    # Relations
    course_ids = fields.Many2many('education.course', string='Enrolled Courses')

    # Status
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _generate_student_id(self):
        # Generate a unique student ID
        last_student = self.search([], order='student_id desc', limit=1)
        if last_student:
            last_id = int(last_student.student_id[3:])  # Remove 'STU' prefix
            new_id = last_id + 1
        else:
            new_id = 1001
        return f'STU{new_id"04d"}'

    def name_get(self):
        return [(student.id, f'{student.student_id} - {student.name}') for student in self]
