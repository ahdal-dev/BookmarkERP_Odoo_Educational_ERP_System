from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta

class StudentPetition(models.Model):
    _name = 'student.petition'
    _description = 'Student Petition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char(string='Petition Reference', required=True, copy=False, 
                      readonly=True, default=lambda self: _('New'))
    student_id = fields.Many2one('res.partner', string='Student', required=True,
                                tracking=True, default=lambda self: self._get_default_student())
    petition_type_id = fields.Many2one('petition.type', string='Petition Type', 
                                      required=True, tracking=True)
    
    # Petition Details
    subject = fields.Char(string='Subject', required=True, tracking=True)
    description = fields.Text(string='Description', required=True)
    requested_date = fields.Date(string='Requested Date', required=True,
                                default=fields.Date.today)
    desired_completion_date = fields.Date(string='Desired Completion Date')
    
    # For Overload Petitions
    current_credits = fields.Float(string='Current Credits')
    requested_credits = fields.Float(string='Requested Credits')
    reason_for_overload = fields.Text(string='Reason for Overload')
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Approval Details
    reviewer_id = fields.Many2one('res.users', string='Reviewed By', readonly=True)
    review_date = fields.Date(string='Review Date', readonly=True)
    comments = fields.Text(string='Review Comments')
    rejection_reason = fields.Text(string='Rejection Reason')
    
    # Document Attachment
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Tracking fields
    submitted_date = fields.Datetime(string='Submitted Date', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    rejected_date = fields.Datetime(string='Rejected Date', readonly=True)
    
    # Computed fields
    days_pending = fields.Integer(string='Days Pending', compute='_compute_days_pending')
    
    def _get_default_student(self):
        """Get the current user's partner record"""
        user = self.env.user
        # In a real scenario, you might want to check if the partner is a student
        # You could add a boolean field 'is_student' to res.partner in another module
        return user.partner_id.id if user.partner_id else False
    
    @api.depends('submitted_date', 'state')
    def _compute_days_pending(self):
        for petition in self:
            if petition.state in ['submitted', 'under_review'] and petition.submitted_date:
                delta = fields.Datetime.now() - petition.submitted_date
                petition.days_pending = delta.days
            else:
                petition.days_pending = 0
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle multiple records at once"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('student.petition') or _('New')
        return super(StudentPetition, self).create(vals_list)
    
    def action_submit(self):
        """Submit petition for review"""
        for petition in self:
            if petition.state != 'draft':
                raise ValidationError(_('Only draft petitions can be submitted.'))
            petition.write({
                'state': 'submitted',
                'submitted_date': fields.Datetime.now()
            })
            # Send email notification to admins
            petition._send_submission_notification()
    
    def action_review(self):
        """Start reviewing the petition"""
        self._check_admin_access()
        self.write({
            'state': 'under_review',
            'reviewer_id': self.env.user.id
        })
    
    def action_approve(self):
        """Approve the petition"""
        self._check_admin_access()
        for petition in self:
            if petition.state not in ['submitted', 'under_review']:
                raise ValidationError(_('Only submitted or under review petitions can be approved.'))
            petition.write({
                'state': 'approved',
                'review_date': fields.Date.today(),
                'approved_date': fields.Datetime.now()
            })
            # Send email notification to student
            petition._send_approval_notification()
    
    def action_reject(self):
        """Reject the petition"""
        self._check_admin_access()
        for petition in self:
            if petition.state not in ['submitted', 'under_review']:
                raise ValidationError(_('Only submitted or under review petitions can be rejected.'))
            if not petition.rejection_reason:
                raise ValidationError(_('Please provide a reason for rejection.'))
            petition.write({
                'state': 'rejected',
                'review_date': fields.Date.today(),
                'rejected_date': fields.Datetime.now()
            })
            # Send email notification to student
            petition._send_rejection_notification()
    
    def action_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft'})
    
    def action_cancel(self):
        """Cancel the petition"""
        self.write({'state': 'cancelled'})
    
    def _send_submission_notification(self):
        """Send email notification to admins when petition is submitted"""
        # Comment out until email templates are created
        # template = self.env.ref('petition_system.email_template_petition_submitted', raise_if_not_found=False)
        # if template:
        #     template.send_mail(self.id, force_send=True)
        pass
    
    def _send_approval_notification(self):
        """Send email notification to student when petition is approved"""
        # Comment out until email templates are created
        pass
    
    def _send_rejection_notification(self):
        """Send email notification to student when petition is rejected"""
        # Comment out until email templates are created
        pass
    
    def _check_admin_access(self):
        """Check if current user has admin access"""
        if not self.env.user.has_group('petition_system.group_petition_admin'):
            raise AccessError(_("Only administrators can perform this action."))
    
    @api.model
    def get_student_petitions(self):
        """Get petitions for current student"""
        student = self.env.user.partner_id
        return self.search([('student_id', '=', student.id)])
    
    def write(self, vals):
        # Restrict students from modifying certain fields
        if self.env.user.has_group('petition_system.group_petition_student') and not self.env.user.has_group('petition_system.group_petition_admin'):
            restricted_fields = ['state', 'reviewer_id', 'review_date', 'comments', 'rejection_reason', 'approved_date', 'rejected_date']
            for field in restricted_fields:
                if field in vals:
                    raise AccessError(_("Students cannot modify '%s' field.") % field)
        return super(StudentPetition, self).write(vals)