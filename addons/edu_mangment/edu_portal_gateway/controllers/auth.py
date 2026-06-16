# -*- coding: utf-8 -*-
"""
Authentication Controller for Educational Portal Gateway

Implements:
- Role-based dashboard routing after authentication
- Session management and secure logout
- CSRF protection for all forms

Note: Student-facing login is handled by the React frontend (bookmark-frontend).
Backend login uses Odoo's native /web/login.
"""

import logging
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from werkzeug.exceptions import Forbidden

_logger = logging.getLogger(__name__)


class EduPortalAuthController(http.Controller):
    """
    Main authentication controller for the Educational Portal.
    
    Provides role-specific dashboards and session management.
    Student-facing login is handled by the React frontend.
    """

    # =========================================================================
    # Role Detection & Routing
    # =========================================================================
    
    def _get_user_role(self, user):
        """
        Detect the primary role of the authenticated user.
        
        Args:
            user: res.users record
            
        Returns:
            str: Role identifier ('student', 'officer', 'admin', 'unknown')
        """
        if not user or not user.exists():
            return 'unknown'
        
        # Check groups in order of specificity (most privileged first)
        if user.has_group('edu_mang_auth.group_erp_admin'):
            return 'admin'
        if user.has_group('edu_mang_auth.group_erp_admission_officer'):
            return 'officer'
        if user.has_group('edu_mang_auth.group_erp_student'):
            return 'student'
        
        # Fallback for internal users
        if user.has_group('base.group_user'):
            return 'staff'
        
        return 'unknown'
    
    def _get_dashboard_url(self, role):
        """
        Get the appropriate dashboard URL for a given role.
        
        Args:
            role: str role identifier
            
        Returns:
            str: Dashboard URL path
        """
        role_dashboards = {
            'admin': '/edu-portal/admin/dashboard',
            'officer': '/edu-portal/officer/dashboard',
            'student': '/edu-portal/student/dashboard',
            'staff': '/web',  # Internal staff go to Odoo backend
        }
        return role_dashboards.get(role, '/edu/login')
    
    # =========================================================================
    # Portal Entry Point
    # =========================================================================
    
    @http.route('/edu-portal', type='http', auth='public', website=True)
    def portal_home(self, **kw):
        """
        Portal home - redirects to login or dashboard based on auth status.
        """
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            if user.exists():
                role = self._get_user_role(user)
                return request.redirect(self._get_dashboard_url(role))
        return request.redirect('/edu/login')
    
    @http.route('/edu-portal/logout', type='http', auth='user', website=True)
    def portal_logout(self, **kw):
        """
        Logout endpoint - clears session and redirects to login.
        """
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            _logger.info('Portal logout: user=%s', user.login if user else 'unknown')
        
        request.session.logout(keep_db=True)
        return request.redirect('/edu/login')
    
    # =========================================================================
    # Password Reset (US 02.02)
    # =========================================================================
    
    @http.route('/edu-portal/forgot-password', type='http', auth='public', website=True)
    def forgot_password(self, **kw):
        """
        Password reset request page.
        """
        message = ''
        success = False
        
        if request.httprequest.method == 'POST':
            email = kw.get('email', '').strip()
            
            if not email:
                message = 'Please enter your email address.'
            else:
                # Find user by email
                user = request.env['res.users'].sudo().search([
                    '|', 
                    ('login', '=', email),
                    ('email', '=', email)
                ], limit=1)
                
                if user:
                    try:
                        # Trigger password reset email
                        user.action_reset_password()
                        success = True
                        message = 'Password reset instructions have been sent to your email.'
                        _logger.info('Password reset requested: user=%s', email)
                    except Exception as e:
                        _logger.error('Password reset failed: user=%s, error=%s', email, str(e))
                        message = 'Unable to send reset email. Please contact support.'
                else:
                    # Don't reveal if email exists (security best practice)
                    success = True
                    message = 'If this email exists in our system, you will receive reset instructions.'
        
        values = {
            'page_name': 'Forgot Password',
            'message': message,
            'success': success,
            'csrf_token': request.csrf_token(),
        }
        
        return request.render('edu_portal_gateway.portal_forgot_password', values)
    
    # =========================================================================
    # Session API
    # =========================================================================
    
    @http.route('/edu-portal/api/session', type='jsonrpc', auth='public')
    def check_session(self):
        """
        JSON-RPC endpoint to check current session status.
        
        Returns:
            dict: Session information including login status and user role
        """
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            if user.exists():
                return {
                    'logged_in': True,
                    'user_id': user.id,
                    'user_name': user.name,
                    'role': self._get_user_role(user),
                    'is_student': user.has_group('edu_mang_auth.group_erp_student'),
                    'is_officer': user.has_group('edu_mang_auth.group_erp_admission_officer'),
                    'is_admin': user.has_group('edu_mang_auth.group_erp_admin'),
                }
        
        return {'logged_in': False}


class EduPortalAccessMixin:
    """
    Mixin class providing access control utilities for portal controllers.
    
    Inherit from this mixin to add role-based access checking to any controller.
    """
    
    def _require_auth(self):
        """
        Verify user is authenticated. Redirect to login if not.
        
        Returns:
            res.users record if authenticated
            
        Raises:
            Redirects to login page if not authenticated
        """
        if not request.session.uid:
            return None
        
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if not user.exists():
            return None
        
        return user
    
    def _require_group(self, group_xml_id):
        """
        Verify user belongs to the specified group.
        
        Args:
            group_xml_id: XML ID of the required group
            
        Returns:
            res.users record if authorized
            
        Raises:
            Forbidden: If user lacks required group membership
        """
        user = self._require_auth()
        if not user:
            return None
        
        if not user.has_group(group_xml_id):
            raise Forbidden(
                description='You do not have permission to access this page.'
            )
        
        return user
    
    def _get_login_redirect(self, error=None):
        """
        Build redirect response to login page.
        
        Args:
            error: Optional error message to display
            
        Returns:
            werkzeug.wrappers.Response
        """
        url = '/edu/login'
        if error:
            url += f'?error={error}'
        return request.redirect(url)
    
    def _render_access_denied(self, message=None):
        """
        Render access denied page.
        
        Args:
            message: Custom error message
            
        Returns:
            Rendered template response
        """
        return request.render('edu_portal_gateway.portal_access_denied', {
            'error_message': message or 'You do not have permission to access this page.',
        })
