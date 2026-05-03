# -*- coding: utf-8 -*-
"""
Tests for custom_registration dashboards: student, officer, and admin.
"""
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestCustomRegistrationDashboards(HttpCase):
    """HTTP tests for custom registration dashboard routes."""

    def test_admin_system_management_unauthenticated(self):
        """Unauthenticated access to system management should redirect or deny."""
        self.authenticate(None, None)
        response = self.url_open('/admin/system_management', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403, 404])

    def test_student_dashboard_unauthenticated(self):
        """Unauthenticated access to student dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/student/dashboard', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_officer_dashboard_unauthenticated(self):
        """Unauthenticated access to officer dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/admission/dashboard', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])
