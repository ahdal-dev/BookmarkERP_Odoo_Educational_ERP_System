from odoo import models, fields, api


class EducationDepartment(models.Model):
    """
    Lightweight academic department used to route petition escalations to a
    Department Chair. Kept inside edu_mang_petition (rather than coupling to
    OpenEduCat's op.department) so the multi-tier petition engine is
    self-contained and does not depend on the OpenEduCat stack being installed.
    """
    _name = 'education.department'
    _description = 'Academic Department'
    _order = 'name'

    name = fields.Char(string='Department', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    chair_id = fields.Many2one(
        'res.users',
        string='Department Chair',
        help='The Department Chair who can escalate and override petitions '
             'routed to this department.',
    )
    course_ids = fields.One2many(
        'education.course', 'department_id', string='Courses'
    )
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_dept_code', 'unique(code)', 'Department code must be unique!'),
    ]
