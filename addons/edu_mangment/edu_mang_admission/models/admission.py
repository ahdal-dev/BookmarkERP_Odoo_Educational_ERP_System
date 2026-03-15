from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import logging
_logger = logging.getLogger(__name__)

class SchoolAdmission(models.Model):
    _name = 'school.admission'
    _description = 'School Admission Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Applicant Name',
        required=True,
        tracking=True
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True
    )
    
    phone = fields.Char(
        string='Phone Number',
        required=True,
        tracking=True
    )
    
    national_id = fields.Char(
        string='National ID',
        required=True,
        tracking=True
    )
    
    address = fields.Text(
        string='Address',
        tracking=True
    )
    
    previous_school = fields.Char(
        string='Previous School',
        tracking=True
    )
    
    gpa = fields.Float(
        string='GPA',
        digits=(3, 2),
        tracking=True
    )
    
    program_id = fields.Many2one(
        'school.program',
        string='Program',
        required=True,
        tracking=True
    )
    
    transcript_document = fields.Binary(
        string='Transcript/Documents',
        attachment=True
    )
    
    transcript_filename = fields.Char(
        string='Filename'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)
    
    reference = fields.Char(
        string='Reference',
        readonly=True,
        copy=False
    )
    
    application_date = fields.Datetime(
        string='Application Date',
        readonly=True
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', False) == False:
                vals['reference'] = self.env['ir.sequence'].next_by_code('school.admission') or 'New'
        return super(SchoolAdmission, self).create(vals_list)
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError('Please enter a valid email address.')
    
    @api.constrains('gpa')
    def _check_gpa(self):
        for record in self:
            if record.gpa and (record.gpa < 0 or record.gpa > 4.0):
                raise ValidationError('GPA must be between 0.0 and 4.0')
    
    def action_submit(self):
        for record in self:
            record.write({
                'state': 'submitted',
                'application_date': fields.Datetime.now()
            })
        return True
    
    def action_under_review(self):
        self.write({'state': 'under_review'})
        return True
    
    def action_accept(self):
        self.write({'state': 'accepted'})
        template = self.env.ref('edu_mang_admission.email_template_admission_status')
        if template:
            mail_id = template.sudo().send_mail(self.id, force_send=True)
            _logger.info("Mail queued: %s", mail_id)
        return True
    
    def action_reject(self):
        self.write({'state': 'rejected'})
        template = self.env.ref('edu_mang_admission.email_template_admission_status')
        if template:
            mail_id = template.sudo().send_mail(self.id, force_send=True)
            _logger.info("Mail queued: %s", mail_id)

        return True
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        return True


class SchoolProgram(models.Model):
    _name = 'school.program'
    _description = 'School Academic Program'
    _order = 'name'

    name = fields.Char(
        string='Program Name',
        required=True
    )
    
    code = fields.Char(
        string='Program Code'
    )
    
    description = fields.Text(
        string='Description'
    )
    
    duration = fields.Integer(
        string='Duration (Years)'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    admission_ids = fields.One2many(
        'school.admission',
        'program_id',
        string='Admissions'
    )
    
    admission_count = fields.Integer(
        string='Applications',
        compute='_compute_admission_count'
    )
    
    @api.depends('admission_ids')
    def _compute_admission_count(self):
        for record in self:
            record.admission_count = len(record.admission_ids)
