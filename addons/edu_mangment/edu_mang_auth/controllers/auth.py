"""
Pure Authentication Controller for Educational ERP
===================================================

This module provides pure HTTP-based authentication without website dependencies.
It can be used for API authentication, mobile apps, or any non-website context.

Key Features:
- Role-based redirect URL determination
- Session check API (JSON)
- Authentication mixin for use by other modules

This controller does NOT depend on the website module.
"""

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class EduAuthMixin:
    """
    Mixin class providing authentication utilities.
    Can be inherited by other controllers to add role-based routing.
    """

    def _get_user_redirect_url(self, user):
        """
        Determine the appropriate redirect URL based on user's group membership.

        Args:
            user: The res.users record of the authenticated user

        Returns:
            str: The URL to redirect the user to
        """
        if not user:
            return '/web'

        # Check groups in order of specificity (most restrictive first)
        # Student group (portal-based)
        if user.has_group('edu_mang_auth.group_erp_student'):
            _logger.info(f"User {user.login} identified as Student, redirecting to /student/dashboard")
            return '/student/dashboard'

        # Admission Officer group
        if user.has_group('edu_mang_auth.group_erp_admission_officer'):
            _logger.info(f"User {user.login} identified as Admission Officer, redirecting to /admission/dashboard")
            return '/admission/dashboard'

        # ERP Admin group
        if user.has_group('edu_mang_auth.group_erp_admin'):
            _logger.info(f"User {user.login} identified as ERP Admin, redirecting to /admin/dashboard")
            return '/admin/dashboard'

        # Default fallback - check if internal user or portal
        if user.has_group('base.group_user'):
            _logger.info(f"User {user.login} is internal user, redirecting to /web")
            return '/web'

        # Portal users without specific role
        _logger.info(f"User {user.login} is portal user, redirecting to /my")
        return '/my'


class EduAuthController(http.Controller, EduAuthMixin):
    """
    Pure HTTP authentication controller.
    Provides JSON API endpoints for authentication operations.
    Does not depend on website module.
    """

    @http.route('/edu/api/session', type='jsonrpc', auth='public', cors='*')
    def api_check_session(self):
        """
        JSON API endpoint to check current session status.
        Returns user information if logged in, or logged_in: False otherwise.
        
        This is a pure API endpoint (no website rendering).
        """
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            if user.exists():
                return {
                    'logged_in': True,
                    'user_id': user.id,
                    'user_name': user.name,
                    'login': user.login,
                    'is_student': user.has_group('edu_mang_auth.group_erp_student'),
                    'is_admission_officer': user.has_group('edu_mang_auth.group_erp_admission_officer'),
                    'is_admin': user.has_group('edu_mang_auth.group_erp_admin'),
                    'redirect_url': self._get_user_redirect_url(user),
                }
        return {'logged_in': False}

    @http.route('/edu/api/user_roles', type='jsonrpc', auth='user', cors='*')
    def api_get_user_roles(self):
        """
        JSON API endpoint to get current user's roles.
        Requires authentication.
        """
        user = request.env.user
        return {
            'user_id': user.id,
            'user_name': user.name,
            'roles': {
                'is_student': user.has_group('edu_mang_auth.group_erp_student'),
                'is_admission_officer': user.has_group('edu_mang_auth.group_erp_admission_officer'),
                'is_admin': user.has_group('edu_mang_auth.group_erp_admin'),
                'is_internal_user': user.has_group('base.group_user'),
                'is_portal_user': user.has_group('base.group_portal'),
            },
            'redirect_url': self._get_user_redirect_url(user),
        }

    @http.route('/edu/api/logout', type='jsonrpc', auth='user', cors='*')
    def api_logout(self):
        """
        JSON API endpoint to logout current user.
        Returns success status.
        """
        try:
            request.session.logout(keep_db=True)
            return {'success': True, 'message': 'Logged out successfully'}
        except Exception as e:
            _logger.error(f"Logout error: {e}")
            return {'success': False, 'message': str(e)}
