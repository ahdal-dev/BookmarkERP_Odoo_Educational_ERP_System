# -*- coding: utf-8 -*-
"""
Tests for OfficerPortalController.
Covers admission pipeline, petition review, student records, and course management.
"""
from odoo.tests import HttpCase, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestOfficerPortalRoutes(HttpCase):
    """HTTP tests for officer portal routes."""

    def test_officer_dashboard_unauthenticated_redirects(self):
        """Unauthenticated access to officer dashboard should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/officer/dashboard', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_officer_admissions_unauthenticated_redirects(self):
        """Unauthenticated access to admissions should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/officer/admissions', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_officer_admissions_kanban_unauthenticated_redirects(self):
        """Unauthenticated access to kanban should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/officer/admissions/kanban', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_officer_petitions_unauthenticated_redirects(self):
        """Unauthenticated access to petition review should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/officer/petitions', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_officer_students_unauthenticated_redirects(self):
        """Unauthenticated access to students should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/officer/students', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_officer_courses_unauthenticated_redirects(self):
        """Unauthenticated access to courses should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/officer/courses', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])

    def test_officer_course_create_form_unauthenticated(self):
        """Unauthenticated access to course creation form should redirect."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal/officer/courses/new', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303, 403])


@tagged('post_install', '-at_install')
class TestOfficerPortalControllerUnit(TransactionCase):
    """Unit tests for OfficerPortalController class."""

    def test_officer_group_constant(self):
        from odoo.addons.edu_portal_gateway.controllers.officer_portal import OfficerPortalController
        ctrl = OfficerPortalController()
        self.assertEqual(ctrl.OFFICER_GROUP, 'edu_mang_auth.group_erp_admission_officer')

    def test_items_per_page_constant(self):
        from odoo.addons.edu_portal_gateway.controllers.officer_portal import OfficerPortalController
        ctrl = OfficerPortalController()
        self.assertEqual(ctrl.ITEMS_PER_PAGE, 20)
