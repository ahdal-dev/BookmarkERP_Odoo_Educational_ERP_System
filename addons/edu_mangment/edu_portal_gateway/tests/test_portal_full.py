# -*- coding: utf-8 -*-
"""
Full integration tests for Portal Gateway.
Authenticates as different roles to cover controller logic.
"""
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestPortalGatewayFull(HttpCase):
    """Test suite for portal gateway with authenticated sessions."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create groups if they don't exist (safety)
        cls.student_group = cls.env.ref('edu_mang_auth.group_erp_student')
        cls.officer_group = cls.env.ref('edu_mang_auth.group_erp_admission_officer')
        cls.admin_group = cls.env.ref('edu_mang_auth.group_erp_admin')

        # Create Student User
        cls.student_user = cls.env['res.users'].create({
            'name': 'Portal Student',
            'login': 'p_student',
            'email': 'p_student@example.com',
            'password': 'password',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id, cls.student_group.id])],
        })

        # Create Officer User
        cls.officer_user = cls.env['res.users'].create({
            'name': 'Portal Officer',
            'login': 'p_officer',
            'email': 'p_officer@example.com',
            'password': 'password',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.officer_group.id])],
        })

        # Create Admin User
        cls.admin_user = cls.env['res.users'].create({
            'name': 'Portal Admin',
            'login': 'p_admin',
            'email': 'p_admin@example.com',
            'password': 'password',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.admin_group.id])],
        })

    # ==========================================
    # Student Portal
    # ==========================================

    def test_student_flow(self):
        """Test student dashboard and list pages."""
        self.authenticate('p_student', 'password')
        
        # Dashboard
        resp = self.url_open('/edu-portal/student/dashboard')
        self.assertEqual(resp.status_code, 200)
        
        # Petitions
        resp = self.url_open('/edu-portal/student/petitions')
        self.assertEqual(resp.status_code, 200)
        
        # Courses
        resp = self.url_open('/edu-portal/student/courses')
        self.assertEqual(resp.status_code, 200)
        
        # Cart
        resp = self.url_open('/edu-portal/student/cart')
        self.assertEqual(resp.status_code, 200)
        
        # Registrations
        resp = self.url_open('/edu-portal/student/registrations')
        self.assertEqual(resp.status_code, 200)

    # ==========================================
    # Officer Portal
    # ==========================================

    def test_officer_flow(self):
        """Test officer dashboard and admission pages."""
        self.authenticate('p_officer', 'password')
        
        # Dashboard
        resp = self.url_open('/edu-portal/officer/dashboard')
        self.assertEqual(resp.status_code, 200)
        
        # Admissions
        resp = self.url_open('/edu-portal/officer/admissions')
        self.assertEqual(resp.status_code, 200)
        
        # Petitions
        resp = self.url_open('/edu-portal/officer/petitions')
        self.assertEqual(resp.status_code, 200)
        
        # Students
        resp = self.url_open('/edu-portal/officer/students')
        self.assertEqual(resp.status_code, 200)

    # ==========================================
    # Admin Portal
    # ==========================================

    def test_admin_flow(self):
        """Test admin dashboard and management pages."""
        self.authenticate('p_admin', 'password')
        
        # Dashboard
        resp = self.url_open('/edu-portal/admin/dashboard')
        self.assertEqual(resp.status_code, 200)
        
        # Users
        resp = self.url_open('/edu-portal/admin/users')
        self.assertEqual(resp.status_code, 200)
        
        # Settings
        resp = self.url_open('/edu-portal/admin/settings')
        self.assertEqual(resp.status_code, 200)
        
        # Reports
        resp = self.url_open('/edu-portal/admin/reports')
        self.assertEqual(resp.status_code, 200)
