# -*- coding: utf-8 -*-
"""
Tests for AdminPortalController.
Covers dashboard, user management, settings, registration windows, and reports.
"""
from odoo.tests import HttpCase, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAdminPortalRoutes(HttpCase):
    """HTTP tests for admin portal routes."""

    def test_admin_dashboard_unauthenticated_redirects(self):
        """Unauthenticated access to admin dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/admin/dashboard', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admin_users_list_unauthenticated_redirects(self):
        """Unauthenticated access to users list should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/admin/users', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admin_users_create_unauthenticated_redirects(self):
        """Unauthenticated access to user create form should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/admin/users/create', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admin_settings_unauthenticated_redirects(self):
        """Unauthenticated access to settings should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/admin/settings', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admin_registration_windows_unauthenticated_redirects(self):
        """Unauthenticated access to registration windows should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/admin/registration-windows', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admin_courses_unauthenticated_redirects(self):
        """Unauthenticated access to courses should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/admin/courses', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_admin_reports_unauthenticated_redirects(self):
        """Unauthenticated access to reports should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/admin/reports', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])


@tagged('post_install', '-at_install')
class TestAdminPortalControllerUnit(TransactionCase):
    """Unit tests for AdminPortalController class."""

    def test_admin_group_constant(self):
        from odoo.addons.edu_portal_gateway.controllers.admin_portal import AdminPortalController
        ctrl = AdminPortalController()
        self.assertEqual(ctrl.ADMIN_GROUP, 'edu_mang_auth.group_erp_admin')

    def test_items_per_page_constant(self):
        from odoo.addons.edu_portal_gateway.controllers.admin_portal import AdminPortalController
        ctrl = AdminPortalController()
        self.assertEqual(ctrl.ITEMS_PER_PAGE, 25)
