# -*- coding: utf-8 -*-
"""
Tests for Petition Type model.
"""
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


@tagged('post_install', '-at_install')
class TestPetitionType(TransactionCase):
    """Test suite for petition.type model."""

    def test_create_petition_type(self):
        """Creating a petition type with required fields should succeed."""
        ptype = self.env['petition.type'].create({
            'name': 'Grade Appeal',
            'code': 'GRADE_APPEAL',
        })
        self.assertEqual(ptype.name, 'Grade Appeal')
        self.assertEqual(ptype.code, 'GRADE_APPEAL')
        self.assertTrue(ptype.active, "Default active should be True")
        self.assertTrue(ptype.requires_approval, "Default requires_approval should be True")

    def test_default_sequence(self):
        """Default sequence should be 10."""
        ptype = self.env['petition.type'].create({
            'name': 'Test Seq',
            'code': 'SEQ_TEST',
        })
        self.assertEqual(ptype.sequence, 10)

    def test_unique_code_constraint(self):
        """Duplicate codes should violate the SQL constraint."""
        self.env['petition.type'].create({
            'name': 'Type A',
            'code': 'UNIQUE_CODE',
        })

        with self.assertRaises(IntegrityError):
            self.env.cr.execute("SAVEPOINT test_unique")
            self.env['petition.type'].create({
                'name': 'Type B',
                'code': 'UNIQUE_CODE',
            })

    def test_optional_fields(self):
        """Optional fields should accept values properly."""
        ptype = self.env['petition.type'].create({
            'name': 'Credit Overload',
            'code': 'CREDIT_OL',
            'description': 'Request to take more than the maximum credits',
            'sequence': 5,
            'active': False,
            'requires_approval': False,
            'max_duration_days': 60,
        })
        self.assertEqual(ptype.description, 'Request to take more than the maximum credits')
        self.assertEqual(ptype.sequence, 5)
        self.assertFalse(ptype.active)
        self.assertFalse(ptype.requires_approval)
        self.assertEqual(ptype.max_duration_days, 60)
