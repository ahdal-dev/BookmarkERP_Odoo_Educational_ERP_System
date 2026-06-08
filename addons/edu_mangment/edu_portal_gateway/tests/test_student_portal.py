# -*- coding: utf-8 -*-
"""
Tests for StudentPortalController.
Uses HttpCase to test routes that require authentication and rendering.
"""
from odoo.tests import HttpCase, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestStudentPortalRoutes(HttpCase):
    """HTTP tests for student portal routes."""

    def setUp(self):
        super().setUp()
        # Create test data
        self.petition_type = self.env['petition.type'].create({
            'name': 'Test Type SP',
            'code': 'SP_TEST',
        })

    def test_student_dashboard_unauthenticated_redirects(self):
        """Unauthenticated access to student dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/student/dashboard', allow_redirects=False)
        # Should redirect to login (303 or 302)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_student_petitions_unauthenticated_redirects(self):
        """Unauthenticated access to petitions should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/student/petitions', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_student_courses_unauthenticated_redirects(self):
        """Unauthenticated access to courses should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/student/courses', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_student_cart_unauthenticated_redirects(self):
        """Unauthenticated access to cart should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/student/cart', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_student_registrations_unauthenticated_redirects(self):
        """Unauthenticated access to registrations should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/student/registrations', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_petition_new_form_unauthenticated_redirects(self):
        """Unauthenticated access to new petition form should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/student/petitions/new', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])


@tagged('post_install', '-at_install')
class TestStudentPortalControllerUnit(TransactionCase):
    """Unit tests for StudentPortalController class."""

    def test_student_group_constant(self):
        """STUDENT_GROUP should be correct."""
        from odoo.addons.edu_portal_gateway.controllers.student_portal import StudentPortalController
        ctrl = StudentPortalController()
        self.assertEqual(ctrl.STUDENT_GROUP, 'edu_mang_auth.group_erp_student')

    def test_items_per_page_constant(self):
        """ITEMS_PER_PAGE should be 12."""
        from odoo.addons.edu_portal_gateway.controllers.student_portal import StudentPortalController
        ctrl = StudentPortalController()
        self.assertEqual(ctrl.ITEMS_PER_PAGE, 12)
