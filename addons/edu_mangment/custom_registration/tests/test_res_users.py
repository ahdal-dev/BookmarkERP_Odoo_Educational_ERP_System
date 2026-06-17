# -*- coding: utf-8 -*-
"""
Tests for res.users hold management extension.
"""
from odoo.tests import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestResUsersHold(TransactionCase):
    """Test suite for res.users hold status management."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = cls.env['res.users'].create({
            'name': 'Hold Test User',
            'login': 'hold_test_user',
            'email': 'hold@example.com',
        })

    def test_initial_hold_status(self):
        """New user should not be on hold by default."""
        self.assertFalse(self.test_user.is_on_hold)
        self.assertFalse(self.test_user.hold_reason)
        self.assertFalse(self.test_user.hold_date)
        self.assertFalse(self.test_user.hold_placed_by)

    def test_place_hold(self):
        """action_place_hold should set hold fields."""
        self.test_user.action_place_hold(reason='Outstanding fees')

        self.assertTrue(self.test_user.is_on_hold)
        self.assertEqual(self.test_user.hold_reason, 'Outstanding fees')
        self.assertEqual(self.test_user.hold_date, fields.Date.today())
        self.assertEqual(self.test_user.hold_placed_by.id, self.env.user.id)

    def test_place_hold_without_reason(self):
        """action_place_hold without reason should still set hold."""
        self.test_user.action_place_hold()

        self.assertTrue(self.test_user.is_on_hold)
        self.assertFalse(self.test_user.hold_reason)

    def test_remove_hold(self):
        """action_remove_hold should clear all hold fields."""
        self.test_user.action_place_hold(reason='Test reason')
        self.test_user.action_remove_hold()

        self.assertFalse(self.test_user.is_on_hold)
        self.assertFalse(self.test_user.hold_reason)
        self.assertFalse(self.test_user.hold_date)
        self.assertFalse(self.test_user.hold_placed_by)

    def test_toggle_hold_on(self):
        """action_toggle_hold should place hold when not on hold."""
        self.assertFalse(self.test_user.is_on_hold)
        result = self.test_user.action_toggle_hold()

        self.assertTrue(self.test_user.is_on_hold)
        self.assertTrue(result)

    def test_toggle_hold_off(self):
        """action_toggle_hold should remove hold when already on hold."""
        self.test_user.action_place_hold()
        self.assertTrue(self.test_user.is_on_hold)

        result = self.test_user.action_toggle_hold()

        self.assertFalse(self.test_user.is_on_hold)
        self.assertTrue(result)

    def test_place_hold_returns_true(self):
        """action_place_hold should return True."""
        result = self.test_user.action_place_hold()
        self.assertTrue(result)

    def test_remove_hold_returns_true(self):
        """action_remove_hold should return True."""
        self.test_user.action_place_hold()
        result = self.test_user.action_remove_hold()
        self.assertTrue(result)

    def test_self_readable_fields(self):
        """SELF_READABLE_FIELDS should include hold and registration fields."""
        readable = self.test_user.SELF_READABLE_FIELDS
        self.assertIn('is_on_hold', readable)
        self.assertIn('hold_reason', readable)
        self.assertIn('hold_date', readable)
        self.assertIn('cart_ids', readable)
        self.assertIn('registration_ids', readable)
