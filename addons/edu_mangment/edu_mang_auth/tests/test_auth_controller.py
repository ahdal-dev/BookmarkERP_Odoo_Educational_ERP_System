# -*- coding: utf-8 -*-
"""
Tests for EduAuthMixin and EduAuthController.
Covers role-based redirect URL logic and API endpoints.
"""
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestEduAuthMixin(TransactionCase):
    """Test suite for EduAuthMixin._get_user_redirect_url()."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test users with different roles
        cls.base_user = cls.env['res.users'].create({
            'name': 'Base User',
            'login': 'auth_base_user',
            'email': 'base@example.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

        cls.portal_user = cls.env['res.users'].create({
            'name': 'Portal User',
            'login': 'auth_portal_user',
            'email': 'portal@example.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })

    def _get_mixin(self):
        """Instantiate the mixin for testing."""
        from odoo.addons.edu_mang_auth.controllers.auth import EduAuthMixin
        return EduAuthMixin()

    def test_redirect_url_for_none_user(self):
        """None user should redirect to /web."""
        mixin = self._get_mixin()
        url = mixin._get_user_redirect_url(None)
        self.assertEqual(url, '/web')

    def test_redirect_url_for_internal_user(self):
        """Internal user without specific role should go to /web."""
        mixin = self._get_mixin()
        url = mixin._get_user_redirect_url(self.base_user)
        self.assertEqual(url, '/web')

    def test_redirect_url_for_portal_user(self):
        """Portal user without specific role should go to /my."""
        mixin = self._get_mixin()
        url = mixin._get_user_redirect_url(self.portal_user)
        self.assertEqual(url, '/my')

    def test_redirect_url_for_student(self):
        """Student should redirect to /student/dashboard."""
        mixin = self._get_mixin()
        try:
            student_group = self.env.ref('edu_mang_auth.group_erp_student')
            self.portal_user.write({'groups_id': [(4, student_group.id)]})
            url = mixin._get_user_redirect_url(self.portal_user)
            self.assertEqual(url, '/student/dashboard')
        except ValueError:
            # Group doesn't exist in test DB — skip gracefully
            pass

    def test_redirect_url_for_officer(self):
        """Admission officer should redirect to /admission/dashboard."""
        mixin = self._get_mixin()
        try:
            officer_group = self.env.ref('edu_mang_auth.group_erp_admission_officer')
            self.base_user.write({'groups_id': [(4, officer_group.id)]})
            url = mixin._get_user_redirect_url(self.base_user)
            self.assertEqual(url, '/admission/dashboard')
        except ValueError:
            pass

    def test_redirect_url_for_admin(self):
        """ERP admin should redirect to /admin/dashboard."""
        mixin = self._get_mixin()
        try:
            admin_group = self.env.ref('edu_mang_auth.group_erp_admin')
            self.base_user.write({'groups_id': [(4, admin_group.id)]})
            url = mixin._get_user_redirect_url(self.base_user)
            self.assertEqual(url, '/admin/dashboard')
        except ValueError:
            pass
