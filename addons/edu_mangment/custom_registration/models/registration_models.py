# -*- coding: utf-8 -*-
"""
Registration Models for Educational ERP System.

This module defines the core data models for course registration:
- education.course: Course catalog
- education.cart: Student wishlist/cart
- education.registration: Actual course enrollments
"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class EducationCourse(models.Model):
    """
    Course model for educational offerings.

    Stores course details including seat availability for registration management.
    """
    _name = 'education.course'
    _description = 'Education Course'
    _order = 'code, name'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Course Name',
        required=True,
        index=True,
        help='Full name of the course'
    )
    code = fields.Char(
        string='Course Code',
        index=True,
        default='NEW',
        help='Unique course identifier (e.g., CS101)'
    )
    description = fields.Text(
        string='Description',
        help='Detailed course description'
    )
    total_seats = fields.Integer(
        string='Total Seats',
        required=True,
        default=30,
        help='Maximum number of students that can enroll'
    )
    available_seats = fields.Integer(
        string='Available Seats',
        compute='_compute_available_seats',
        store=True,
        help='Number of seats currently available'
    )
    schedule = fields.Char(
        string='Schedule',
        help='Course schedule (e.g., MWF 10:00-11:00)'
    )
    timing_start = fields.Float(
        string='Start Time',
        help='Course start time'
    )
    timing_end = fields.Float(
        string='End Time',
        help='Course end time'
    )
    instructor = fields.Char(
        string='Instructor',
        help='Display name of the course instructor'
    )
    credits = fields.Integer(
        string='Credits',
        default=3,
        help='Number of credit hours'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to False to archive the course'
    )
    registration_open = fields.Boolean(
        string='Registration Open',
        default=False,
        help='Whether registration is currently open for this course'
    )
    registration_start = fields.Date(
        string='Registration Start Date',
        help='Date when registration opens'
    )
    registration_end = fields.Date(
        string='Registration End Date',
        help='Date when registration closes'
    )
    add_drop_deadline = fields.Date(
        string='Add/Drop Deadline',
        help='Last date to add or drop this course'
    )
    semester = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Semester', default='fall')
    year = fields.Integer(
        string='Year',
        default=lambda self: fields.Date.today().year
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    # Relational fields
    registration_ids = fields.One2many(
        'education.registration',
        'course_id',
        string='Registrations'
    )
    cart_ids = fields.One2many(
        'education.cart',
        'course_id',
        string='Cart Items'
    )

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for course in self:
            if course.code and course.code != 'NEW':
                course.display_name = f"[{course.code}] {course.name}"
            else:
                course.display_name = course.name or ''

    @api.depends('total_seats', 'registration_ids.state')
    def _compute_available_seats(self):
        for course in self:
            enrolled_count = self.env['education.registration'].search_count([
                ('course_id', '=', course.id),
                ('state', '=', 'enrolled')
            ])
            course.available_seats = course.total_seats - enrolled_count

    @api.constrains('total_seats')
    def _check_total_seats(self):
        for record in self:
            if record.total_seats < 0:
                raise ValidationError(_('Total seats cannot be negative.'))

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            if record.code and record.code != 'NEW':
                existing = self.search([
                    ('code', '=', record.code),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError(_('Course code must be unique.'))

    def action_open_registration(self):
        """Open registration for this course."""
        self.write({'registration_open': True})
        return True

    def action_close_registration(self):
        """Close registration for this course."""
        self.write({'registration_open': False})
        return True


class EducationCart(models.Model):
    """
    Cart/Wishlist model for students to pre-select courses.
    
    Students can add courses to their cart before registration opens.
    """
    _name = 'education.cart'
    _description = 'Student Course Cart/Wishlist'
    _order = 'create_date desc'

    student_id = fields.Many2one(
        'res.users',
        string='Student',
        required=True,
        ondelete='cascade',
        default=lambda self: self.env.user.id,
        index=True
    )
    course_id = fields.Many2one(
        'education.course',
        string='Course',
        required=True,
        ondelete='cascade',
        index=True
    )
    added_date = fields.Datetime(
        string='Added Date',
        default=fields.Datetime.now,
        readonly=True
    )
    priority = fields.Integer(
        string='Priority',
        default=10,
        help='Lower number = higher priority'
    )
    notes = fields.Text(
        string='Notes',
        help='Student notes about this course selection'
    )

    # Computed fields for UI
    course_name = fields.Char(
        related='course_id.name',
        string='Course Name',
        store=True
    )
    course_code = fields.Char(
        related='course_id.code',
        string='Course Code',
        store=True
    )
    available_seats = fields.Integer(
        related='course_id.available_seats',
        string='Available Seats'
    )
    registration_open = fields.Boolean(
        related='course_id.registration_open',
        string='Registration Open'
    )

    @api.constrains('student_id', 'course_id')
    def _check_unique_cart_entry(self):
        for record in self:
            existing = self.search([
                ('student_id', '=', record.student_id.id),
                ('course_id', '=', record.course_id.id),
                ('id', '!=', record.id)
            ], limit=1)
            if existing:
                raise ValidationError(
                    _('This course is already in your cart.')
                )

    def action_register(self):
        """
        Convert cart item to actual registration.
        
        Performs validation for seat availability and student hold status.
        """
        self.ensure_one()
        Registration = self.env['education.registration']
        
        # Check if student is on hold
        if self.student_id.is_on_hold:
            raise ValidationError(
                _('Your account is on hold. Please contact the administration.')
            )
        
        # Check if registration is open
        if not self.course_id.registration_open:
            raise ValidationError(
                _('Registration is not currently open for this course.')
            )
        
        # Check seat availability
        if self.course_id.available_seats <= 0:
            raise ValidationError(
                _('No seats available for this course.')
            )
        
        # Create registration
        registration = Registration.create({
            'student_id': self.student_id.id,
            'course_id': self.course_id.id,
        })
        
        # Remove from cart
        self.unlink()
        
        return registration


class EducationRegistration(models.Model):
    """
    Registration model for actual course enrollments.
    
    Records student enrollments with real-time seat validation.
    """
    _name = 'education.registration'
    _description = 'Course Registration'
    _order = 'registration_date desc'

    student_id = fields.Many2one(
        'res.users',
        string='Student',
        required=True,
        ondelete='cascade',
        index=True
    )
    course_id = fields.Many2one(
        'education.course',
        string='Course',
        required=True,
        ondelete='cascade',
        index=True
    )
    registration_date = fields.Datetime(
        string='Registration Date',
        default=fields.Datetime.now,
        readonly=True
    )
    state = fields.Selection([
        ('enrolled', 'Enrolled'),
        ('dropped', 'Dropped'),
        ('waitlist', 'Waitlist'),
    ], string='Status', default='enrolled', required=True)
    dropped_date = fields.Datetime(
        string='Dropped Date',
        readonly=True
    )
    is_officer_override = fields.Boolean(
        string='Officer Override',
        default=False,
        help='True if registration was created/modified by officer override'
    )

    # Computed fields for UI
    student_name = fields.Char(
        related='student_id.name',
        string='Student Name',
        store=True
    )
    course_name = fields.Char(
        related='course_id.name',
        string='Course Name',
        store=True
    )
    course_code = fields.Char(
        related='course_id.code',
        string='Course Code',
        store=True
    )
    course_schedule = fields.Char(
        related='course_id.schedule',
        string='Schedule'
    )
    course_instructor = fields.Char(
        related='course_id.instructor',
        string='Instructor'
    )

    @api.constrains('student_id', 'course_id', 'state')
    def _check_unique_enrollment(self):
        for record in self:
            if record.state == 'enrolled':
                existing = self.search([
                    ('student_id', '=', record.student_id.id),
                    ('course_id', '=', record.course_id.id),
                    ('state', '=', 'enrolled'),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        _('Student is already enrolled in this course.')
                    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to validate seat availability with row-level locking.
        
        Uses FOR UPDATE to handle concurrent registrations.
        """
        for vals in vals_list:
            course_id = vals.get('course_id')
            student_id = vals.get('student_id')
            is_officer = vals.get('is_officer_override', False)
            
            if not course_id or not student_id:
                continue
            
            # Lock the course row for update to prevent race conditions
            self.env.cr.execute("""
                SELECT id, registration_open, total_seats
                FROM education_course
                WHERE id = %s
                FOR UPDATE
            """, (course_id,))
            
            course_data = self.env.cr.fetchone()
            
            if not course_data:
                raise ValidationError(_('Course not found.'))
            
            course_id_db, registration_open, total_seats = course_data
            
            # Calculate current enrollments
            self.env.cr.execute("""
                SELECT COUNT(*)
                FROM education_registration
                WHERE course_id = %s AND state = 'enrolled'
            """, (course_id,))
            current_enrolled = self.env.cr.fetchone()[0]
            real_available = total_seats - current_enrolled
            
            # Validate seat availability
            if real_available <= 0 and not is_officer:
                raise ValidationError(
                    _('No seats available for this course. '
                      'All %d seats are currently filled.') % total_seats
                )
            
            # Check if registration is open (unless officer override)
            if not registration_open and not is_officer:
                raise ValidationError(
                    _('Registration is not currently open for this course.')
                )
            
            # Check student hold status
            student = self.env['res.users'].sudo().browse(student_id)
            if student.is_on_hold and not is_officer:
                raise ValidationError(
                    _('Your account is on hold. Please contact the administration.')
                )
            
            # Check for existing enrollment
            existing = self.search([
                ('student_id', '=', student_id),
                ('course_id', '=', course_id),
                ('state', '=', 'enrolled')
            ], limit=1)
            
            if existing:
                raise ValidationError(
                    _('Student is already enrolled in this course.')
                )
        
        registrations = super().create(vals_list)
        
        # Invalidate course cache to update available_seats
        for reg in registrations:
            reg.course_id._compute_available_seats()
        
        return registrations

    def action_drop(self, is_officer_override=False):
        """
        Drop the course registration.
        
        Validates add/drop deadline unless officer override.
        """
        self.ensure_one()
        
        if self.state == 'dropped':
            raise UserError(_('Course already dropped.'))
        
        # Check add/drop deadline (unless officer override)
        if not is_officer_override and self.course_id.add_drop_deadline:
            if fields.Date.today() > self.course_id.add_drop_deadline:
                raise ValidationError(
                    _('Add/Drop deadline has passed for this course. '
                      'Please contact an admission officer.')
                )
        
        self.write({
            'state': 'dropped',
            'dropped_date': fields.Datetime.now(),
            'is_officer_override': is_officer_override,
        })
        
        # Update available seats
        self.course_id._compute_available_seats()
        
        _logger.info(
            'Registration dropped: Student %s, Course %s, Officer Override: %s',
            self.student_id.name, self.course_id.code, is_officer_override
        )
        
        return True

    def action_reenroll(self):
        """Re-enroll a dropped registration (officer action)."""
        self.ensure_one()
        
        if self.state == 'enrolled':
            raise UserError(_('Already enrolled in this course.'))
        
        # Check seat availability
        if self.course_id.available_seats <= 0:
            raise ValidationError(_('No seats available for re-enrollment.'))
        
        self.write({
            'state': 'enrolled',
            'dropped_date': False,
            'is_officer_override': True,
        })
        
        # Update available seats
        self.course_id._compute_available_seats()
        
        return True
