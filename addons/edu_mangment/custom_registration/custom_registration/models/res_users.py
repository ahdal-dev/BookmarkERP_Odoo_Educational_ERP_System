# -*- coding: utf-8 -*-
"""
Extension of res.users for registration management.

Adds hold status functionality to prevent flagged students from registering.
"""
from odoo import models, fields, api


class ResUsers(models.Model):
    """
    Extend res.users with registration-related fields.
    """
    _inherit = 'res.users'

    is_on_hold = fields.Boolean(
        string='Registration Hold',
        default=False,
        help='If enabled, student cannot register for courses until hold is removed.'
    )
    hold_reason = fields.Text(
        string='Hold Reason',
        help='Reason for placing the student on hold'
    )
    hold_date = fields.Date(
        string='Hold Date',
        help='Date when the hold was placed'
    )
    hold_placed_by = fields.Many2one(
        'res.users',
        string='Hold Placed By',
        help='Administrator who placed the hold'
    )
    cart_ids = fields.One2many(
        'education.cart',
        'student_id',
        string='Cart Items'
    )
    registration_ids = fields.One2many(
        'education.registration',
        'student_id',
        string='Registrations'
    )

    def action_place_hold(self, reason=None):
        """Place registration hold on the user."""
        self.ensure_one()
        self.write({
            'is_on_hold': True,
            'hold_reason': reason,
            'hold_date': fields.Date.today(),
            'hold_placed_by': self.env.user.id,
        })
        return True

    def action_remove_hold(self):
        """Remove registration hold from the user."""
        self.ensure_one()
        self.write({
            'is_on_hold': False,
            'hold_reason': False,
            'hold_date': False,
            'hold_placed_by': False,
        })
        return True

    def action_toggle_hold(self):
        """Toggle the hold status."""
        self.ensure_one()
        if self.is_on_hold:
            return self.action_remove_hold()
        else:
            return self.action_place_hold()

    @property
    def SELF_READABLE_FIELDS(self):
        """Allow users to read their own hold status."""
        return super().SELF_READABLE_FIELDS + [
            'is_on_hold', 'hold_reason', 'hold_date',
            'cart_ids', 'registration_ids'
        ]
