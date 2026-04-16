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
                                readonly=True, tracking=True, 
                                default=lambda self: self._get_default_student())
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
    is_own_petition = fields.Boolean(string='Is Own Petition', compute='_compute_is_own_petition')

    def _is_auth_student(self):
        """Check if user has auth student group"""
        return self.env.user.has_group('edu_mangment.group_erp_student')
    
    def _is_auth_admin(self):
        """Check if user has auth admin group"""
        return self.env.user.has_group('edu_mangment.group_erp_admin')
    
    def _is_auth_admission_officer(self):
        """Check if user has auth admission officer group"""
        return self.env.user.has_group('edu_mangment.group_erp_admission_officer')

    def _get_default_student(self):
        """Get the current user's partner record as the student"""
        user = self.env.user
        partner = user.partner_id
        
        # Check if user is a student (has auth student group)
        if not self._is_auth_student():
            raise ValidationError(_('Only students can create petitions. Please login with a student account.'))
        
        if not partner:
            raise ValidationError(_('Your user account is not linked to a partner record.'))
        
        return partner.id

    @api.depends('submitted_date', 'state')
    def _compute_days_pending(self):
        for petition in self:
            if petition.state in ['submitted', 'under_review'] and petition.submitted_date:
                delta = fields.Datetime.now() - petition.submitted_date
                petition.days_pending = delta.days
            else:
                petition.days_pending = 0

    @api.depends('student_id')
    def _compute_is_own_petition(self):
        for petition in self:
            petition.is_own_petition = petition.student_id == self.env.user.partner_id

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle multiple records at once"""
        for vals in vals_list:
            # Force student to be current user
            if 'student_id' not in vals or not vals['student_id']:
                vals['student_id'] = self._get_default_student()
            
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('student.petition') or _('New')
        return super(StudentPetition, self).create(vals_list)

    def write(self, vals):
        # Prevent changing the student field
        if 'student_id' in vals:
            current_student = self.student_id.id
            new_student = vals['student_id']
            if current_student != new_student:
                raise AccessError(_("You cannot change the student on an existing petition."))
            del vals['student_id']
        
        # Restrict students from modifying certain fields
        is_student = self.env.user.has_group('edu_mang_petition.group_petition_student')
        is_admin = self._is_auth_admin()
        is_petition_admin = self.env.user.has_group('edu_mang_petition.group_petition_admin')
        
        if is_student and not (is_admin or is_petition_admin):
            restricted_fields = ['state', 'reviewer_id', 'review_date', 'comments', 'rejection_reason', 'approved_date', 'rejected_date']
            for field in restricted_fields:
                if field in vals:
                    raise AccessError(_("Students cannot modify '%s' field.") % field)
        return super(StudentPetition, self).write(vals)

    def action_submit(self):
        """Submit petition for review"""
        for petition in self:
            if petition.state != 'draft':
                raise ValidationError(_('Only draft petitions can be submitted.'))
            petition.write({
                'state': 'submitted',
                'submitted_date': fields.Datetime.now()
            })
            petition._send_submission_notification()

    def _check_admin_access(self):
        """Check if current user has admin access"""
        # Check both auth admin group and petition admin group
        is_auth_admin = self._is_auth_admin()
        is_petition_admin = self.env.user.has_group('edu_mang_petition.group_petition_admin')
        is_petition_manager = self.env.user.has_group('edu_mang_petition.group_petition_manager')
        
        if not (is_auth_admin or is_petition_admin or is_petition_manager):
            raise AccessError(_("Only administrators can perform this action."))

    def _check_self_review(self):
        """Check if user is trying to review/approve/reject their own petition"""
        for petition in self:
            if petition.student_id == self.env.user.partner_id:
                raise ValidationError(_('You cannot review, approve, or reject your own petition. Only another administrator can review your petition.'))

    def action_review(self):
        """Start reviewing the petition"""
        self._check_admin_access()
        self._check_self_review()
        self.write({
            'state': 'under_review',
            'reviewer_id': self.env.user.id
        })

    def action_approve(self):
        """Approve the petition"""
        self._check_admin_access()
        self._check_self_review()
        for petition in self:
            if petition.state not in ['submitted', 'under_review']:
                raise ValidationError(_('Only submitted or under review petitions can be approved.'))
            petition.write({
                'state': 'approved',
                'review_date': fields.Date.today(),
                'approved_date': fields.Datetime.now()
            })
            petition._send_approval_notification()

    def action_reject(self):
        """Reject the petition"""
        self._check_admin_access()
        self._check_self_review()
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
            petition._send_rejection_notification()

    def action_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft'})

    def action_cancel(self):
        """Cancel the petition"""
        self.write({'state': 'cancelled'})

    def _send_submission_notification(self):
        """Send email notification to admins when petition is submitted"""
        pass

    def _send_approval_notification(self):
        """Send email notification to student when petition is approved"""
        pass

    def _send_rejection_notification(self):
        """Send email notification to student when petition is rejected"""
        pass