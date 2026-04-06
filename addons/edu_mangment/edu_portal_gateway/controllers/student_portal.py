# -*- coding: utf-8 -*-
"""
Student Portal Controller

Implements student-facing portal features:
- Student dashboard with academic overview
- Petition submission and tracking (US 03.01, US 03.02)
- Course catalog browsing
- Registration cart management
- Academic records view

Data Privacy: All queries filter by current user's student record (US 02.04)
"""

import base64
import logging
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from werkzeug.exceptions import Forbidden, NotFound

from .auth import EduPortalAccessMixin

_logger = logging.getLogger(__name__)


class StudentPortalController(http.Controller, EduPortalAccessMixin):
    """
    Controller for student portal views and actions.
    
    All routes require student group membership and enforce data privacy
    by filtering records to the current student only.
    """
    
    STUDENT_GROUP = 'edu_mang_auth.group_erp_student'
    ITEMS_PER_PAGE = 12
    
    # =========================================================================
    # Dashboard
    # =========================================================================
    
    @http.route('/edu-portal/student/dashboard', type='http', auth='user', website=True)
    def student_dashboard(self, **kw):
        """
        Student dashboard - main entry point showing academic overview.
        
        Displays:
        - Quick stats (pending petitions, enrolled courses, etc.)
        - Recent activity
        - Quick action links
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect('session_expired')
        
        # Get student's petitions
        Petition = request.env['student.petition'].sudo()
        student_petitions = Petition.search([
            ('student_id', '=', user.partner_id.id)
        ])
        pending_petitions = student_petitions.filtered(
            lambda p: p.state in ['submitted', 'under_review']
        )
        
        # Get student's registrations
        Registration = request.env['education.registration'].sudo()
        enrolled_courses = Registration.search_count([
            ('student_id', '=', user.id),
            ('state', '=', 'enrolled')
        ])
        
        # Get cart items
        Cart = request.env['education.cart'].sudo()
        cart_count = Cart.search_count([('student_id', '=', user.id)])
        
        # Recent petitions for activity feed
        recent_petitions = Petition.search([
            ('student_id', '=', user.partner_id.id)
        ], limit=5, order='create_date desc')
        
        values = {
            'page_name': 'Student Dashboard',
            'user': user,
            'student_name': user.partner_id.name or user.name,
            'student_email': user.partner_id.email or user.login,
            'pending_petitions': len(pending_petitions),
            'total_petitions': len(student_petitions),
            'enrolled_courses': enrolled_courses,
            'cart_items': cart_count,
            'recent_petitions': recent_petitions,
            'is_on_hold': getattr(user, 'is_on_hold', False),
        }
        
        return request.render('edu_portal_gateway.student_dashboard', values)
    
    # =========================================================================
    # Petition Management (US 03.01, US 03.02)
    # =========================================================================
    
    @http.route('/edu-portal/student/petitions', type='http', auth='user', website=True)
    def student_petitions_list(self, page=1, status=None, **kw):
        """
        List all petitions submitted by the current student.
        
        Supports filtering by status and pagination.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Petition = request.env['student.petition'].sudo()
        
        # Build domain - always filter by current student
        domain = [('student_id', '=', user.partner_id.id)]
        
        if status and status != 'all':
            domain.append(('state', '=', status))
        
        # Pagination
        page = int(page) or 1
        total = Petition.search_count(domain)
        offset = (page - 1) * self.ITEMS_PER_PAGE
        
        petitions = Petition.search(
            domain,
            limit=self.ITEMS_PER_PAGE,
            offset=offset,
            order='create_date desc'
        )
        
        # Status counts for filter badges
        status_counts = {
            'all': Petition.search_count([('student_id', '=', user.partner_id.id)]),
            'draft': Petition.search_count([('student_id', '=', user.partner_id.id), ('state', '=', 'draft')]),
            'submitted': Petition.search_count([('student_id', '=', user.partner_id.id), ('state', '=', 'submitted')]),
            'under_review': Petition.search_count([('student_id', '=', user.partner_id.id), ('state', '=', 'under_review')]),
            'approved': Petition.search_count([('student_id', '=', user.partner_id.id), ('state', '=', 'approved')]),
            'rejected': Petition.search_count([('student_id', '=', user.partner_id.id), ('state', '=', 'rejected')]),
        }
        
        # Pagination info
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        values = {
            'page_name': 'My Petitions',
            'user': user,
            'petitions': petitions,
            'current_status': status or 'all',
            'status_counts': status_counts,
            'page': page,
            'total_pages': total_pages,
            'total': total,
        }
        
        return request.render('edu_portal_gateway.student_petitions_list', values)
    
    @http.route('/edu-portal/student/petitions/new', type='http', auth='user', website=True)
    def student_petition_form(self, **kw):
        """
        Display the new petition submission form.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        # Get petition types
        PetitionType = request.env['petition.type'].sudo()
        petition_types = PetitionType.search([])
        
        values = {
            'page_name': 'New Petition',
            'user': user,
            'petition_types': petition_types,
            'csrf_token': request.csrf_token(),
        }
        
        return request.render('edu_portal_gateway.student_petition_form', values)
    
    @http.route('/edu-portal/student/petitions/submit', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def student_petition_submit(self, **kw):
        """
        Process petition submission with attachments.
        
        Creates a new petition record and handles file attachments.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        try:
            Petition = request.env['student.petition'].sudo()
            Attachment = request.env['ir.attachment'].sudo()
            
            # Validate required fields
            petition_type_id = kw.get('petition_type_id')
            subject = kw.get('subject', '').strip()
            description = kw.get('description', '').strip()
            
            if not petition_type_id or not subject or not description:
                raise ValidationError('Please fill in all required fields.')
            
            # Create petition
            petition_vals = {
                'student_id': user.partner_id.id,
                'petition_type_id': int(petition_type_id),
                'subject': subject,
                'description': description,
                'requested_date': fields.Date.today(),
            }
            
            # Optional fields for overload petitions
            if kw.get('current_credits'):
                petition_vals['current_credits'] = float(kw.get('current_credits', 0))
            if kw.get('requested_credits'):
                petition_vals['requested_credits'] = float(kw.get('requested_credits', 0))
            if kw.get('reason_for_overload'):
                petition_vals['reason_for_overload'] = kw.get('reason_for_overload')
            
            petition = Petition.create(petition_vals)
            
            # Handle file attachments
            attachment_ids = []
            files = request.httprequest.files.getlist('attachments')
            
            for file in files:
                if file and file.filename:
                    # Read file data
                    file_data = file.read()
                    
                    # Validate file size (max 10MB)
                    if len(file_data) > 10 * 1024 * 1024:
                        _logger.warning('File too large: %s', file.filename)
                        continue
                    
                    # Create attachment
                    attachment = Attachment.create({
                        'name': file.filename,
                        'datas': base64.b64encode(file_data),
                        'res_model': 'student.petition',
                        'res_id': petition.id,
                        'mimetype': file.content_type or 'application/octet-stream',
                    })
                    attachment_ids.append(attachment.id)
            
            # Link attachments to petition
            if attachment_ids:
                petition.write({'attachment_ids': [(6, 0, attachment_ids)]})
            
            # Auto-submit if requested
            if kw.get('auto_submit'):
                petition.action_submit()
                _logger.info('Petition submitted: %s by student %s', petition.name, user.login)
            else:
                _logger.info('Petition draft created: %s by student %s', petition.name, user.login)
            
            return request.redirect(f'/edu-portal/student/petitions/{petition.id}?success=1')
            
        except ValidationError as e:
            _logger.warning('Petition validation error: %s', str(e))
            return request.redirect(f'/edu-portal/student/petitions/new?error={str(e)}')
        except Exception as e:
            _logger.error('Petition submission error: %s', str(e))
            return request.redirect('/edu-portal/student/petitions/new?error=An error occurred')
    
    @http.route('/edu-portal/student/petitions/<int:petition_id>', type='http', auth='user', website=True)
    def student_petition_detail(self, petition_id, **kw):
        """
        View petition details and status history.
        
        Only accessible for petitions owned by the current student.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Petition = request.env['student.petition'].sudo()
        petition = Petition.search([
            ('id', '=', petition_id),
            ('student_id', '=', user.partner_id.id)  # Enforce ownership
        ], limit=1)
        
        if not petition:
            raise NotFound('Petition not found.')
        
        values = {
            'page_name': f'Petition {petition.name}',
            'user': user,
            'petition': petition,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.student_petition_detail', values)
    
    @http.route('/edu-portal/student/petitions/<int:petition_id>/submit', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def student_petition_action_submit(self, petition_id, **kw):
        """
        Submit a draft petition for review.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Petition = request.env['student.petition'].sudo()
        petition = Petition.search([
            ('id', '=', petition_id),
            ('student_id', '=', user.partner_id.id),
            ('state', '=', 'draft')
        ], limit=1)
        
        if not petition:
            return request.redirect('/edu-portal/student/petitions?error=Petition not found')
        
        try:
            petition.action_submit()
            return request.redirect(f'/edu-portal/student/petitions/{petition_id}?success=Petition submitted successfully')
        except ValidationError as e:
            return request.redirect(f'/edu-portal/student/petitions/{petition_id}?error={str(e)}')
    
    # =========================================================================
    # Course Catalog & Registration
    # =========================================================================
    
    @http.route('/edu-portal/student/courses', type='http', auth='user', website=True)
    def student_course_catalog(self, page=1, search=None, semester=None, **kw):
        """
        Browse available courses for registration.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        
        # Build domain
        domain = [('active', '=', True)]
        
        if search:
            domain.append('|')
            domain.append(('name', 'ilike', search))
            domain.append(('code', 'ilike', search))
        
        if semester:
            domain.append(('semester', '=', semester))
        
        # Pagination
        page = int(page) or 1
        total = Course.search_count(domain)
        offset = (page - 1) * self.ITEMS_PER_PAGE
        
        courses = Course.search(
            domain,
            limit=self.ITEMS_PER_PAGE,
            offset=offset,
            order='code, name'
        )
        
        # Get cart items for highlighting
        Cart = request.env['education.cart'].sudo()
        cart_items = Cart.search([('student_id', '=', user.id)])
        cart_course_ids = cart_items.mapped('course_id').ids
        
        # Get enrolled courses
        Registration = request.env['education.registration'].sudo()
        enrolled = Registration.search([
            ('student_id', '=', user.id),
            ('state', '=', 'enrolled')
        ])
        enrolled_course_ids = enrolled.mapped('course_id').ids
        
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        values = {
            'page_name': 'Course Catalog',
            'user': user,
            'courses': courses,
            'cart_course_ids': cart_course_ids,
            'enrolled_course_ids': enrolled_course_ids,
            'search': search or '',
            'semester': semester or '',
            'page': page,
            'total_pages': total_pages,
            'total': total,
        }
        
        return request.render('edu_portal_gateway.student_course_catalog', values)
    
    @http.route('/edu-portal/student/cart', type='http', auth='user', website=True)
    def student_cart(self, **kw):
        """
        View and manage registration cart (wishlist).
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Cart = request.env['education.cart'].sudo()
        cart_items = Cart.search([
            ('student_id', '=', user.id)
        ], order='priority, create_date')
        
        # Calculate total credits
        total_credits = sum(item.course_id.credits for item in cart_items)
        
        values = {
            'page_name': 'Registration Cart',
            'user': user,
            'cart_items': cart_items,
            'total_credits': total_credits,
            'is_on_hold': getattr(user, 'is_on_hold', False),
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.student_cart', values)
    
    @http.route('/edu-portal/student/cart/add/<int:course_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def student_cart_add(self, course_id, **kw):
        """
        Add a course to the registration cart.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        try:
            Course = request.env['education.course'].sudo()
            course = Course.browse(course_id)
            
            if not course.exists():
                return request.redirect('/edu-portal/student/courses?error=Course not found')
            
            Cart = request.env['education.cart'].sudo()
            Cart.create({
                'student_id': user.id,
                'course_id': course_id,
            })
            
            return request.redirect('/edu-portal/student/cart?success=Course added to cart')
            
        except ValidationError as e:
            return request.redirect(f'/edu-portal/student/courses?error={str(e)}')
    
    @http.route('/edu-portal/student/cart/remove/<int:cart_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def student_cart_remove(self, cart_id, **kw):
        """
        Remove a course from the registration cart.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Cart = request.env['education.cart'].sudo()
        cart_item = Cart.search([
            ('id', '=', cart_id),
            ('student_id', '=', user.id)
        ], limit=1)
        
        if cart_item:
            cart_item.unlink()
        
        return request.redirect('/edu-portal/student/cart?success=Course removed from cart')
    
    @http.route('/edu-portal/student/cart/register/<int:cart_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def student_cart_register(self, cart_id, **kw):
        """
        Register for a course from the cart.
        
        Validates seat availability and student hold status.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Cart = request.env['education.cart'].sudo()
        cart_item = Cart.search([
            ('id', '=', cart_id),
            ('student_id', '=', user.id)
        ], limit=1)
        
        if not cart_item:
            return request.redirect('/edu-portal/student/cart?error=Cart item not found')
        
        try:
            cart_item.action_register()
            return request.redirect('/edu-portal/student/registrations?success=Successfully registered')
        except (ValidationError, UserError) as e:
            return request.redirect(f'/edu-portal/student/cart?error={str(e)}')
    
    @http.route('/edu-portal/student/registrations', type='http', auth='user', website=True)
    def student_registrations(self, **kw):
        """
        View current course registrations.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Registration = request.env['education.registration'].sudo()
        
        enrolled = Registration.search([
            ('student_id', '=', user.id),
            ('state', '=', 'enrolled')
        ], order='course_code')
        
        dropped = Registration.search([
            ('student_id', '=', user.id),
            ('state', '=', 'dropped')
        ], order='dropped_date desc', limit=10)
        
        total_credits = sum(reg.course_id.credits for reg in enrolled)
        
        values = {
            'page_name': 'My Registrations',
            'user': user,
            'enrolled_courses': enrolled,
            'dropped_courses': dropped,
            'total_credits': total_credits,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.student_registrations', values)
    
    @http.route('/edu-portal/student/registrations/drop/<int:reg_id>', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def student_registration_drop(self, reg_id, **kw):
        """
        Drop a course registration.
        
        Validates add/drop deadline.
        """
        user = self._require_group(self.STUDENT_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Registration = request.env['education.registration'].sudo()
        registration = Registration.search([
            ('id', '=', reg_id),
            ('student_id', '=', user.id),
            ('state', '=', 'enrolled')
        ], limit=1)
        
        if not registration:
            return request.redirect('/edu-portal/student/registrations?error=Registration not found')
        
        try:
            registration.action_drop()
            return request.redirect('/edu-portal/student/registrations?success=Course dropped successfully')
        except (ValidationError, UserError) as e:
            return request.redirect(f'/edu-portal/student/registrations?error={str(e)}')
