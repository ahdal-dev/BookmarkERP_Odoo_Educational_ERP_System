# -*- coding: utf-8 -*-
"""
Authenticated tests for edu_mang_website dashboards.
"""
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestWebsiteDashboardFull(HttpCase):
    """Test suite for website dashboards with authenticated sessions."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create Student User
        cls.student_user = cls.env['res.users'].create({
            'name': 'Website Student',
            'login': 'ws_student',
            'email': 'ws_student@example.com',
            'password': 'password',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id, cls.env.ref('edu_mang_auth.group_erp_student').id])],
        })

        # Create Admin User
        cls.admin_user = cls.env['res.users'].create({
            'name': 'Website Admin',
            'login': 'ws_admin',
            'email': 'ws_admin@example.com',
            'password': 'password',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.env.ref('edu_mang_auth.group_erp_admin').id])],
        })

    def test_student_dashboard_auth(self):
        """Test student dashboard access when logged in."""
        self.authenticate('ws_student', 'password')
        resp = self.url_open('/student/dashboard')
        self.assertEqual(resp.status_code, 200)

    def test_admin_dashboard_auth(self):
        """Test admin dashboard access when logged in."""
        self.authenticate('ws_admin', 'password')
        resp = self.url_open('/admin/dashboard')
        self.assertEqual(resp.status_code, 200)
