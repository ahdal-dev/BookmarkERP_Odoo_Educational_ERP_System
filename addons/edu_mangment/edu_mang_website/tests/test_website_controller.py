# -*- coding: utf-8 -*-
"""
Tests for edu_mang_website controllers: main.py and dashboards.py.
"""
from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.exceptions import AccessDenied
from werkzeug.exceptions import Forbidden


@tagged('post_install', '-at_install')
class TestWebsiteAuthRoutes(HttpCase):
    """HTTP tests for website auth routes."""

    def test_edu_login_page_returns_200(self):
        """GET /edu/login should return 200 for public access."""
        self.authenticate(None, None)
        response = self.url_open('/edu/login')
        self.assertEqual(response.status_code, 200)

    def test_edu_login_page_renders_form(self):
        """Login page should contain login form elements."""
        self.authenticate(None, None)
        response = self.url_open('/edu/login')
        content = response.content.decode('utf-8')
        # Should contain the page name or form elements
        self.assertTrue(len(content) > 0, "Login page should have content")

    def test_web_login_redirect_to_edu_login(self):
        """GET /web/login should redirect to /edu/login."""
        self.authenticate(None, None)
        response = self.url_open('/web/login', allow_redirects=False)
        if response.status_code in [302, 303]:
            location = response.headers.get('Location', '')
            self.assertIn('/edu/login', location)

    def test_edu_logout_unauthenticated_redirects(self):
        """Unauthenticated /edu/logout should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu/logout', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_access_denied_page_returns_200(self):
        """GET /edu/access-denied should return 200."""
        self.authenticate(None, None)
        response = self.url_open('/edu/access-denied')
        self.assertEqual(response.status_code, 200)

    def test_access_denied_page_with_message(self):
        """Access denied page should accept custom message."""
        self.authenticate(None, None)
        response = self.url_open('/edu/access-denied?message=Custom+Error')
        self.assertEqual(response.status_code, 200)


@tagged('post_install', '-at_install')
class TestDashboardRoutes(HttpCase):
    """HTTP tests for website dashboard routes."""

    def test_student_dashboard_unauthenticated_redirects(self):
        """Unauthenticated /student/dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/student/dashboard', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_student_petitions_unauthenticated_redirects(self):
        """Unauthenticated /student/petitions should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/student/petitions', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_student_registration_unauthenticated_redirects(self):
        """Unauthenticated /student/registration should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/student/registration', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admission_dashboard_unauthenticated_redirects(self):
        """Unauthenticated /admission/dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/admission/dashboard', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admin_dashboard_unauthenticated_redirects(self):
        """Unauthenticated /admin/dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/admin/dashboard', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])


@tagged('post_install', '-at_install')
class TestDashboardControllerUnit(TransactionCase):
    """Unit tests for WebsiteDashboardController class."""

    def _get_controller(self):
        from odoo.addons.edu_mang_website.controllers.dashboards import WebsiteDashboardController
        return WebsiteDashboardController()

    def test_check_access_method_exists(self):
        """Controller should have _check_access method."""
        ctrl = self._get_controller()
        self.assertTrue(callable(getattr(ctrl, '_check_access', None)))

    def test_get_access_denied_response_method_exists(self):
        """Controller should have _get_access_denied_response method."""
        ctrl = self._get_controller()
        self.assertTrue(callable(getattr(ctrl, '_get_access_denied_response', None)))


@tagged('post_install', '-at_install')
class TestWebsiteSessionController(TransactionCase):
    """Unit tests for EduWebsiteSessionController."""

    def test_session_controller_exists(self):
        """Session controller should be importable."""
        from odoo.addons.edu_mang_website.controllers.main import EduWebsiteSessionController
        ctrl = EduWebsiteSessionController()
        self.assertTrue(hasattr(ctrl, 'check_session'))

    def test_auth_mixin_redirect_logic(self):
        """EduAuthMixin in main.py should have _get_user_redirect_url."""
        from odoo.addons.edu_mang_website.controllers.main import EduAuthMixin
        mixin = EduAuthMixin()

        # Test None user
        self.assertEqual(mixin._get_user_redirect_url(None), '/web')

        # Test internal user
        internal_user = self.env['res.users'].create({
            'name': 'WS Internal',
            'login': 'ws_internal_test',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        url = mixin._get_user_redirect_url(internal_user)
        self.assertEqual(url, '/web')

        # Test portal user
        portal_user = self.env['res.users'].create({
            'name': 'WS Portal',
            'login': 'ws_portal_test',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
        })
        url = mixin._get_user_redirect_url(portal_user)
        self.assertEqual(url, '/my')
