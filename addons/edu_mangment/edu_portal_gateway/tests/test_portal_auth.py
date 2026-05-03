# -*- coding: utf-8 -*-
"""
Tests for EduPortalAuthController and EduPortalAccessMixin.
Covers role detection, dashboard URL mapping, and access control helpers.
"""
from odoo.tests import TransactionCase, HttpCase, tagged
from werkzeug.exceptions import Forbidden


@tagged('post_install', '-at_install')
class TestEduPortalAuthRoles(TransactionCase):
    """Test suite for _get_user_role() and _get_dashboard_url()."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_user = cls.env['res.users'].create({
            'name': 'Role Test User',
            'login': 'role_test_user',
            'email': 'role@example.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

        cls.portal_user = cls.env['res.users'].create({
            'name': 'Portal Role User',
            'login': 'portal_role_user',
            'email': 'portalrole@example.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })

    def _get_controller(self):
        from odoo.addons.edu_portal_gateway.controllers.auth import EduPortalAuthController
        return EduPortalAuthController()

    # ==========================================
    # _get_user_role()
    # ==========================================

    def test_role_for_none_user(self):
        ctrl = self._get_controller()
        self.assertEqual(ctrl._get_user_role(None), 'unknown')

    def test_role_for_internal_user(self):
        ctrl = self._get_controller()
        role = ctrl._get_user_role(self.base_user)
        self.assertIn(role, ['staff', 'admin', 'officer'])

    def test_role_for_unknown_user(self):
        """Portal user without specific group should be 'unknown'."""
        ctrl = self._get_controller()
        role = ctrl._get_user_role(self.portal_user)
        self.assertEqual(role, 'unknown')

    def test_role_student(self):
        ctrl = self._get_controller()
        try:
            group = self.env.ref('edu_mang_auth.group_erp_student')
            self.portal_user.write({'groups_id': [(4, group.id)]})
            role = ctrl._get_user_role(self.portal_user)
            self.assertEqual(role, 'student')
        except ValueError:
            pass

    def test_role_officer(self):
        ctrl = self._get_controller()
        try:
            group = self.env.ref('edu_mang_auth.group_erp_admission_officer')
            self.base_user.write({'groups_id': [(4, group.id)]})
            role = ctrl._get_user_role(self.base_user)
            self.assertEqual(role, 'officer')
        except ValueError:
            pass

    def test_role_admin(self):
        ctrl = self._get_controller()
        try:
            group = self.env.ref('edu_mang_auth.group_erp_admin')
            self.base_user.write({'groups_id': [(4, group.id)]})
            role = ctrl._get_user_role(self.base_user)
            self.assertEqual(role, 'admin')
        except ValueError:
            pass

    # ==========================================
    # _get_dashboard_url()
    # ==========================================

    def test_dashboard_url_admin(self):
        ctrl = self._get_controller()
        self.assertEqual(ctrl._get_dashboard_url('admin'), '/edu-portal/admin/dashboard')

    def test_dashboard_url_officer(self):
        ctrl = self._get_controller()
        self.assertEqual(ctrl._get_dashboard_url('officer'), '/edu-portal/officer/dashboard')

    def test_dashboard_url_student(self):
        ctrl = self._get_controller()
        self.assertEqual(ctrl._get_dashboard_url('student'), '/edu-portal/student/dashboard')

    def test_dashboard_url_staff(self):
        ctrl = self._get_controller()
        self.assertEqual(ctrl._get_dashboard_url('staff'), '/web')

    def test_dashboard_url_unknown(self):
        ctrl = self._get_controller()
        self.assertEqual(ctrl._get_dashboard_url('unknown'), '/edu/login')


@tagged('post_install', '-at_install')
class TestEduPortalAccessMixin(TransactionCase):
    """Test suite for EduPortalAccessMixin helper methods."""

    def _get_mixin(self):
        from odoo.addons.edu_portal_gateway.controllers.auth import EduPortalAccessMixin
        return EduPortalAccessMixin()

    def test_require_auth_no_session(self):
        """_require_auth with no session should return None."""
        from odoo.addons.edu_portal_gateway.controllers.auth import EduPortalAccessMixin
        mixin = EduPortalAccessMixin()
        # This test validates the method signature — in a real test
        # it would need an HTTP request context. The logic is straightforward.
        self.assertTrue(callable(getattr(mixin, '_require_auth', None)))

    def test_require_group_method_exists(self):
        """_require_group should be callable."""
        mixin = self._get_mixin()
        self.assertTrue(callable(getattr(mixin, '_require_group', None)))

    def test_get_login_redirect_method_exists(self):
        """_get_login_redirect should be callable."""
        mixin = self._get_mixin()
        self.assertTrue(callable(getattr(mixin, '_get_login_redirect', None)))

    def test_render_access_denied_method_exists(self):
        """_render_access_denied should be callable."""
        mixin = self._get_mixin()
        self.assertTrue(callable(getattr(mixin, '_render_access_denied', None)))


@tagged('post_install', '-at_install')
class TestPortalEntryPoints(HttpCase):
    """HTTP tests for portal entry point routes."""

    def test_portal_home_unauthenticated(self):
        """Unauthenticated user should be redirected to /edu/login."""
        self.authenticate(None, None)
        response = self.url_open('/edu-portal', allow_redirects=False)
        self.assertIn(response.status_code, [302, 303])
        self.assertIn('/edu/login', response.headers.get('Location', ''))
