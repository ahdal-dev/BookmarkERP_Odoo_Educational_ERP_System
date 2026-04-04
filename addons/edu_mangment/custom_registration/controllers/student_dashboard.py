# -*- coding: utf-8 -*-
"""
Student Dashboard Controller for Registration Management.

Provides web routes for students to manage their course registration,
wishlist/cart, and schedule.
"""
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class StudentDashboardController(http.Controller):
    """
    Controller for student registration dashboard.
    
    All routes require the group_erp_student role.
    """

    def _check_student_access(self):
        """Verify the user has student access rights."""
        if not request.env.user.has_group('edu_mang_auth.group_erp_student'):
            raise AccessError(_('Access denied. Student role required.'))
        return True

    def _get_student_data(self):
        """Get common student dashboard data."""
        user = request.env.user
        return {
            'user': user,
            'is_on_hold': user.is_on_hold,
            'hold_reason': user.hold_reason,
        }

    @http.route('/student/registration', type='http', auth='user', website=True)
    def student_registration_dashboard(self, **kwargs):
        """
        Main student registration dashboard.
        
        Displays course catalog, cart, and current schedule.
        """
        self._check_student_access()
        user = request.env.user
        
        # Get available courses
        Course = request.env['education.course'].sudo()
        courses = Course.search([
            ('active', '=', True),
            ('available_seats', '>', 0),
        ], order='code')
        
        # Get student's cart items
        Cart = request.env['education.cart'].sudo()
        cart_items = Cart.search([
            ('student_id', '=', user.id)
        ], order='priority, added_date desc')
        
        # Get student's current registrations
        Registration = request.env['education.registration'].sudo()
        registrations = Registration.search([
            ('student_id', '=', user.id),
            ('state', '=', 'enrolled')
        ], order='registration_date desc')
        
        values = {
            **self._get_student_data(),
            'courses': courses,
            'cart_items': cart_items,
            'registrations': registrations,
            'page_title': 'Course Registration',
        }
        
        return request.render('custom_registration.student_registration_template', values)

    @http.route('/student/cart/add', type='http', auth='user', website=True, methods=['POST'])
    def add_to_cart(self, course_id, **kwargs):
        """Add a course to the student's cart/wishlist."""
        self._check_student_access()
        
        try:
            course_id = int(course_id)
            Cart = request.env['education.cart'].sudo()
            
            # Check if already in cart
            existing = Cart.search([
                ('student_id', '=', request.env.user.id),
                ('course_id', '=', course_id)
            ], limit=1)
            
            if existing:
                return request.redirect('/student/registration?message=already_in_cart')
            
            # Check if already registered
            Registration = request.env['education.registration'].sudo()
            enrolled = Registration.search([
                ('student_id', '=', request.env.user.id),
                ('course_id', '=', course_id),
                ('state', '=', 'enrolled')
            ], limit=1)
            
            if enrolled:
                return request.redirect('/student/registration?message=already_enrolled')
            
            Cart.create({
                'student_id': request.env.user.id,
                'course_id': course_id,
            })
            
            return request.redirect('/student/registration?message=added_to_cart')
            
        except Exception as e:
            _logger.error('Error adding to cart: %s', str(e))
            return request.redirect('/student/registration?error=' + str(e))

    @http.route('/student/cart/remove', type='http', auth='user', website=True, methods=['POST'])
    def remove_from_cart(self, cart_id, **kwargs):
        """Remove a course from the student's cart."""
        self._check_student_access()
        
        try:
            cart_id = int(cart_id)
            Cart = request.env['education.cart'].sudo()
            cart_item = Cart.search([
                ('id', '=', cart_id),
                ('student_id', '=', request.env.user.id)
            ], limit=1)
            
            if cart_item:
                cart_item.unlink()
                return request.redirect('/student/registration?message=removed_from_cart')
            else:
                return request.redirect('/student/registration?error=cart_item_not_found')
                
        except Exception as e:
            _logger.error('Error removing from cart: %s', str(e))
            return request.redirect('/student/registration?error=' + str(e))

    @http.route('/student/register', type='http', auth='user', website=True, methods=['POST'])
    def register_course(self, course_id=None, cart_id=None, **kwargs):
        """
        Register for a course directly or from cart.
        
        Performs real-time seat validation and hold status check.
        """
        self._check_student_access()
        user = request.env.user
        
        # Check hold status
        if user.is_on_hold:
            return request.redirect('/student/registration?error=account_on_hold')
        
        try:
            Registration = request.env['education.registration'].sudo()
            Cart = request.env['education.cart'].sudo()
            
            if cart_id:
                # Register from cart item
                cart_id = int(cart_id)
                cart_item = Cart.search([
                    ('id', '=', cart_id),
                    ('student_id', '=', user.id)
                ], limit=1)
                
                if not cart_item:
                    return request.redirect('/student/registration?error=cart_item_not_found')
                
                course_id = cart_item.course_id.id
                
            elif course_id:
                course_id = int(course_id)
            else:
                return request.redirect('/student/registration?error=no_course_specified')
            
            # Create registration (validation happens in model)
            Registration.create({
                'student_id': user.id,
                'course_id': course_id,
            })
            
            # Remove from cart if exists
            cart_item = Cart.search([
                ('student_id', '=', user.id),
                ('course_id', '=', course_id)
            ], limit=1)
            if cart_item:
                cart_item.unlink()
            
            return request.redirect('/student/registration?message=registration_success')
            
        except ValidationError as e:
            _logger.warning('Registration validation error: %s', str(e))
            return request.redirect('/student/registration?error=' + str(e.args[0]))
        except Exception as e:
            _logger.error('Registration error: %s', str(e))
            return request.redirect('/student/registration?error=' + str(e))

    @http.route('/student/register/all', type='http', auth='user', website=True, methods=['POST'])
    def register_all_cart_items(self, **kwargs):
        """Register for all courses in the cart."""
        self._check_student_access()
        user = request.env.user
        
        if user.is_on_hold:
            return request.redirect('/student/registration?error=account_on_hold')
        
        try:
            Cart = request.env['education.cart'].sudo()
            Registration = request.env['education.registration'].sudo()
            
            cart_items = Cart.search([
                ('student_id', '=', user.id)
            ], order='priority')
            
            success_count = 0
            failed_courses = []
            
            for item in cart_items:
                try:
                    Registration.create({
                        'student_id': user.id,
                        'course_id': item.course_id.id,
                    })
                    item.unlink()
                    success_count += 1
                except ValidationError as e:
                    failed_courses.append(f"{item.course_id.code}: {e.args[0]}")
            
            if failed_courses:
                error_msg = f"Registered for {success_count} courses. Failed: " + "; ".join(failed_courses)
                return request.redirect('/student/registration?error=' + error_msg)
            
            return request.redirect(f'/student/registration?message=registered_{success_count}_courses')
            
        except Exception as e:
            _logger.error('Bulk registration error: %s', str(e))
            return request.redirect('/student/registration?error=' + str(e))

    @http.route('/student/drop', type='http', auth='user', website=True, methods=['POST'])
    def drop_course(self, registration_id, **kwargs):
        """Drop a registered course within the add/drop period."""
        self._check_student_access()
        
        try:
            registration_id = int(registration_id)
            Registration = request.env['education.registration'].sudo()
            
            registration = Registration.search([
                ('id', '=', registration_id),
                ('student_id', '=', request.env.user.id),
                ('state', '=', 'enrolled')
            ], limit=1)
            
            if not registration:
                return request.redirect('/student/registration?error=registration_not_found')
            
            registration.action_drop(is_officer_override=False)
            
            return request.redirect('/student/registration?message=course_dropped')
            
        except ValidationError as e:
            _logger.warning('Drop validation error: %s', str(e))
            return request.redirect('/student/registration?error=' + str(e.args[0]))
        except Exception as e:
            _logger.error('Drop error: %s', str(e))
            return request.redirect('/student/registration?error=' + str(e))

    @http.route('/student/schedule', type='http', auth='user', website=True)
    def student_schedule(self, **kwargs):
        """View student's current course schedule."""
        self._check_student_access()
        
        Registration = request.env['education.registration'].sudo()
        registrations = Registration.search([
            ('student_id', '=', request.env.user.id),
            ('state', '=', 'enrolled')
        ], order='course_id')
        
        values = {
            **self._get_student_data(),
            'registrations': registrations,
            'page_title': 'My Schedule',
        }
        
        return request.render('custom_registration.student_schedule_template', values)

    @http.route('/student/registration/api/courses', type='jsonrpc', auth='user')
    def api_get_courses(self, **kwargs):
        """API endpoint to get available courses (JSON)."""
        self._check_student_access()
        
        Course = request.env['education.course'].sudo()
        courses = Course.search([
            ('active', '=', True),
        ])
        
        return [{
            'id': c.id,
            'code': c.code,
            'name': c.name,
            'description': c.description,
            'schedule': c.schedule,
            'available_seats': c.available_seats,
            'total_seats': c.total_seats,
            'registration_open': c.registration_open,
        } for c in courses]
