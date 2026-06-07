"""
Website Authentication Controller for Educational ERP
======================================================

This controller provides the website-facing login/logout functionality.
It extends the pure auth controller from edu_mang_auth with website-specific
rendering (templates, pages, redirects).

Routes:
- /edu/login: Custom educational login page
- /edu/logout: Logout and redirect to login page
- /web/login: Override to redirect to custom login
"""

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
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
            return '/edu-portal/student/dashboard'

        # Admission Officer group
        if user.has_group('edu_mang_auth.group_erp_admission_officer'):
            _logger.info(f"User {user.login} identified as Admission Officer, redirecting to /admission/dashboard")
            return '/edu-portal/officer/dashboard'

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


class EduWebsiteAuthController(Home, EduAuthMixin):
    """
    Website login controller that extends Odoo's default login behavior
    with custom templates and role-based dashboard routing.
    """

    @http.route('/web/login', type='http', auth='none', website=True, sitemap=False)
    def web_login(self, redirect=None, **kw):
        """
        Override the standard web login to redirect to custom login page.

        GET requests: Redirect to /edu/login (custom login page)
        POST requests: Process authentication, then redirect based on role
        """
        # For GET requests, redirect to custom login page
        if request.httprequest.method == 'GET':
            # If user is already logged in, redirect to their dashboard
            if request.session.uid:
                user = request.env['res.users'].sudo().browse(request.session.uid)
                if user and user.exists():
                    return request.redirect(self._get_user_redirect_url(user))

            # Build redirect URL with any query parameters
            redirect_url = '/edu/login'
            if redirect:
                redirect_url += f'?redirect={redirect}'
            if kw.get('error'):
                separator = '&' if redirect else '?'
                redirect_url += f'{separator}error={kw.get("error")}'
            return request.redirect(redirect_url)

        # For POST requests, process authentication
        response = super().web_login(redirect=redirect, **kw)

        # After successful login, redirect based on role
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)

            if user and user.exists():
                # If no explicit redirect was requested, use role-based routing
                if not redirect or redirect in ['/', '/web', '']:
                    redirect_url = self._get_user_redirect_url(user)
                    return request.redirect(redirect_url)

        return response

    @http.route('/edu/login', type='http', auth='public', website=True, sitemap=False)
    def edu_login_page(self, redirect=None, **kw):
        """
        Custom educational ERP login page endpoint.

        This provides a student-friendly login page that can be accessed
        directly at /edu/login.
        """
        if request.session.uid:
            # User already logged in, redirect to appropriate dashboard
            user = request.env['res.users'].sudo().browse(request.session.uid)
            return request.redirect(self._get_user_redirect_url(user))

        values = {
            'redirect': redirect,
            'error': kw.get('error', ''),
            'login': kw.get('login', ''),
            'page_name': 'Educational ERP Login',
            'csrf_token': request.csrf_token(),
        }

        return request.render('edu_mang_website.edu_login_page', values)

    @http.route('/edu/logout', type='http', auth='user', website=True)
    def edu_logout(self, redirect='/edu/login', **kw):
        """
        Custom logout endpoint that redirects to the educational login page.
        """
        request.session.logout(keep_db=True)
        return request.redirect(redirect)


class EduWebsiteSessionController(http.Controller, EduAuthMixin):
    """
    Controller for session-related endpoints.
    """

    @http.route('/edu/check_session', type='jsonrpc', auth='public', website=True)
    def check_session(self):
        """
        AJAX endpoint to check if user session is still valid.
        Useful for client-side session management.
        """
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            if user.exists():
                return {
                    'logged_in': True,
                    'user_id': user.id,
                    'user_name': user.name,
                    'is_student': user.has_group('edu_mang_auth.group_erp_student'),
                    'is_admission_officer': user.has_group('edu_mang_auth.group_erp_admission_officer'),
                    'is_admin': user.has_group('edu_mang_auth.group_erp_admin'),
                }
        return {'logged_in': False}
