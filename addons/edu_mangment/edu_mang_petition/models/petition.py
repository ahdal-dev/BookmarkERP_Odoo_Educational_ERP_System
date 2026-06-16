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

    # ------------------------------------------------------------------
    # Multi-tier routing (Instructor -> Advisor -> Chair) + override
    # ------------------------------------------------------------------
    course_id = fields.Many2one(
        'education.course', string='Related Course', tracking=True,
        help='Course-specific petitions are routed to this course\'s '
             'instructor at the Instructor tier.',
    )
    department_id = fields.Many2one(
        'education.department', string='Department',
        related='course_id.department_id', store=True, readonly=True,
        help='Owning department, used to route escalations to the Chair.',
    )
    current_tier = fields.Selection([
        ('instructor', 'Instructor'),
        ('advisor', 'Academic Advisor'),
        ('chair', 'Department Chair'),
        ('done', 'Closed'),
    ], string='Current Tier', tracking=True,
        help='Which faculty tier currently owns this petition for review.')
    is_escalated = fields.Boolean(
        string='Escalated', default=False, tracking=True,
        help='True once a Department Chair has pulled this petition for final '
             'escalation/override.',
    )
    override_reason = fields.Text(
        string='Override Reason',
        help='Justification recorded when a Department Chair overrides the '
             'prior instructor/advisor rulings.',
    )
    override_user_id = fields.Many2one(
        'res.users', string='Overridden By', readonly=True,
    )
    decision_ids = fields.One2many(
        'petition.decision', 'petition_id', string='Decision Trail',
    )

    def _is_auth_student(self):
        """Check if user has auth student group"""
        return self.env.user.has_group('edu_mang_auth.group_erp_student')

    def _is_auth_admin(self):
        """Check if user has auth admin group"""
        return self.env.user.has_group('edu_mang_auth.group_erp_admin')

    def _is_auth_admission_officer(self):
        """Check if user has auth admission officer group"""
        return self.env.user.has_group('edu_mang_auth.group_erp_admission_officer')

    def _is_auth_instructor(self):
        """Check if user has auth instructor group"""
        return self.env.user.has_group('edu_mang_auth.group_erp_instructor')

    def _is_auth_advisor(self):
        """Check if user has auth academic advisor group"""
        return self.env.user.has_group('edu_mang_auth.group_erp_academic_advisor')

    def _is_auth_chair(self):
        """Check if user has auth department chair group"""
        return self.env.user.has_group('edu_mang_auth.group_erp_department_chair')

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
        """Submit petition for review and route it to the first faculty tier."""
        for petition in self:
            if petition.state != 'draft':
                raise ValidationError(_('Only draft petitions can be submitted.'))
            petition.write({
                'state': 'submitted',
                'submitted_date': fields.Datetime.now(),
                'current_tier': petition._initial_tier(),
            })
            petition._send_submission_notification()

    def _initial_tier(self):
        """First tier to own a freshly-submitted petition.

        Course-specific petitions start at the Instructor tier (if the course
        has an instructor); otherwise they go straight to the Advisor tier.
        """
        self.ensure_one()
        if self.course_id and self.course_id.instructor_user_id:
            return 'instructor'
        return 'advisor'

    def _next_tier(self):
        """Instructor -> Advisor -> Chair progression."""
        self.ensure_one()
        order = ['instructor', 'advisor', 'chair']
        if self.current_tier in order:
            idx = order.index(self.current_tier)
            if idx + 1 < len(order):
                return order[idx + 1]
        return 'done'

    # ------------------------------------------------------------------
    # Tier decision engine
    # ------------------------------------------------------------------
    def _log_decision(self, tier, action, user, reason=None):
        """Append an immutable line to the petition's decision audit trail."""
        self.ensure_one()
        self.env['petition.decision'].sudo().create({
            'petition_id': self.id,
            'tier': tier,
            'action': action,
            'user_id': user.id,
            'reason': reason,
        })

    def _acting_user(self, acting_user_id=None):
        """Resolve the acting user. The API gateway runs as a service account
        and passes the real actor via ``acting_user_id``; interactive backend
        use falls back to ``self.env.user``."""
        if acting_user_id:
            return self.env['res.users'].sudo().browse(acting_user_id)
        return self.env.user

    def tier_approve(self, acting_user_id=None, reason=None):
        """Approve at the current tier. Advances to the next tier; reaching the
        end (or an explicit final tier) finalises the petition as approved."""
        for petition in self:
            if petition.state not in ('submitted', 'under_review'):
                raise ValidationError(_('Only active petitions can be reviewed.'))
            user = petition._acting_user(acting_user_id)
            if petition.student_id == user.partner_id:
                raise ValidationError(_('You cannot review your own petition.'))
            petition._log_decision(petition.current_tier, 'approve', user, reason)
            nxt = petition._next_tier()
            if nxt == 'done':
                petition.write({
                    'state': 'approved',
                    'current_tier': 'done',
                    'reviewer_id': user.id,
                    'review_date': fields.Date.today(),
                    'approved_date': fields.Datetime.now(),
                    'comments': reason or petition.comments,
                })
                petition._send_approval_notification()
            else:
                petition.write({'state': 'under_review', 'current_tier': nxt})
        return True

    def tier_reject(self, acting_user_id=None, reason=None):
        """Reject at the current tier. Terminal unless a Chair later overrides."""
        for petition in self:
            if petition.state not in ('submitted', 'under_review'):
                raise ValidationError(_('Only active petitions can be reviewed.'))
            if not reason:
                raise ValidationError(_('Please provide a reason for rejection.'))
            user = petition._acting_user(acting_user_id)
            if petition.student_id == user.partner_id:
                raise ValidationError(_('You cannot review your own petition.'))
            petition._log_decision(petition.current_tier, 'reject', user, reason)
            petition.write({
                'state': 'rejected',
                'current_tier': 'done',
                'reviewer_id': user.id,
                'review_date': fields.Date.today(),
                'rejected_date': fields.Datetime.now(),
                'rejection_reason': reason,
            })
            petition._send_rejection_notification()
        return True

    def action_escalate(self, acting_user_id=None, reason=None):
        """Pull the petition up to the Department Chair tier for final review."""
        for petition in self:
            user = petition._acting_user(acting_user_id)
            petition._log_decision(petition.current_tier or 'advisor',
                                   'escalate', user, reason)
            petition.write({
                'state': 'under_review',
                'current_tier': 'chair',
                'is_escalated': True,
            })
        return True

    def chair_override(self, acting_user_id=None, decision='approve', reason=None):
        """Department Chair final override of prior rulings.

        ``decision`` is 'approve' or 'reject'. An override reason is mandatory
        and the chair's identity is recorded for the audit trail.
        """
        if decision not in ('approve', 'reject'):
            raise ValidationError(_("Override decision must be 'approve' or 'reject'."))
        for petition in self:
            user = petition._acting_user(acting_user_id)
            if not petition._is_chair_user(user):
                raise AccessError(_('Only a Department Chair can override a petition.'))
            if not reason:
                raise ValidationError(_('An override reason is required.'))
            if petition.student_id == user.partner_id:
                raise ValidationError(_('You cannot override your own petition.'))
            petition._log_decision('chair', 'override', user, reason)
            vals = {
                'current_tier': 'done',
                'is_escalated': True,
                'override_reason': reason,
                'override_user_id': user.id,
                'reviewer_id': user.id,
                'review_date': fields.Date.today(),
            }
            if decision == 'approve':
                vals.update({'state': 'approved', 'approved_date': fields.Datetime.now()})
            else:
                vals.update({'state': 'rejected', 'rejected_date': fields.Datetime.now(),
                             'rejection_reason': reason})
            petition.write(vals)
        return True

    def _is_chair_user(self, user):
        """Whether ``user`` holds the Department Chair group."""
        return user.has_group('edu_mang_auth.group_erp_department_chair') or \
            user.has_group('edu_mang_auth.group_erp_admin')

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