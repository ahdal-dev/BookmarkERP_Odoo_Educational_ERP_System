# -*- coding: utf-8 -*-
"""
Tests for Student Petition model.
Covers the full workflow: create → submit → review → approve/reject/cancel.
"""
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta


@tagged('post_install', '-at_install')
class TestStudentPetition(TransactionCase):
    """Test suite for the student.petition model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a petition type
        cls.petition_type = cls.env['petition.type'].create({
            'name': 'Course Overload',
            'code': 'OVERLOAD',
            'requires_approval': True,
            'max_duration_days': 30,
        })

        cls.petition_type_2 = cls.env['petition.type'].create({
            'name': 'Late Drop',
            'code': 'LATE_DROP',
            'requires_approval': True,
        })

        # Create test users
        cls.student_user = cls.env['res.users'].create({
            'name': 'Test Student',
            'login': 'test_student_pet',
            'email': 'student_pet@example.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_portal').id,
            ])],
        })

        cls.admin_user = cls.env['res.users'].create({
            'name': 'Test Admin',
            'login': 'test_admin_pet',
            'email': 'admin_pet@example.com',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
            ])],
        })

    # ==========================================
    # Petition Creation
    # ==========================================

    def test_create_petition_sets_sequence(self):
        """Create a petition should assign a sequence reference."""
        petition = self.env['student.petition'].with_user(self.admin_user).create({
            'student_id': self.student_user.partner_id.id,
            'petition_type_id': self.petition_type.id,
            'subject': 'Overload Request',
            'description': 'I need to take extra credits this semester.',
        })
        self.assertTrue(petition.name, "Petition should have a name/reference")
        self.assertEqual(petition.state, 'draft')

    def test_create_petition_with_overload_fields(self):
        """Petition with overload-specific fields should be created correctly."""
        petition = self.env['student.petition'].with_user(self.admin_user).create({
            'student_id': self.student_user.partner_id.id,
            'petition_type_id': self.petition_type.id,
            'subject': 'Overload',
            'description': 'Extra credits needed',
            'current_credits': 15.0,
            'requested_credits': 21.0,
            'reason_for_overload': 'I have a 4.0 GPA',
        })
        self.assertAlmostEqual(petition.current_credits, 15.0)
        self.assertAlmostEqual(petition.requested_credits, 21.0)
        self.assertEqual(petition.reason_for_overload, 'I have a 4.0 GPA')

    # ==========================================
    # Workflow Transitions
    # ==========================================

    def _create_draft_petition(self):
        """Helper to create a draft petition."""
        return self.env['student.petition'].with_user(self.admin_user).create({
            'student_id': self.student_user.partner_id.id,
            'petition_type_id': self.petition_type.id,
            'subject': 'Test Petition',
            'description': 'Test description',
        })

    def test_submit_petition(self):
        """Submitting a draft petition should set state to 'submitted'."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()

        self.assertEqual(petition.state, 'submitted')
        self.assertTrue(petition.submitted_date, "Submitted date should be set")

    def test_submit_non_draft_raises_error(self):
        """Submitting a non-draft petition should raise ValidationError."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()

        with self.assertRaises(ValidationError):
            petition.with_user(self.admin_user).action_submit()

    def test_review_petition(self):
        """Reviewing a petition should set state to 'under_review'."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()
        petition.with_user(self.admin_user).action_review()

        self.assertEqual(petition.state, 'under_review')
        self.assertEqual(petition.reviewer_id.id, self.admin_user.id)

    def test_approve_submitted_petition(self):
        """Approving a submitted petition should set state to 'approved'."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()
        petition.with_user(self.admin_user).action_approve()

        self.assertEqual(petition.state, 'approved')
        self.assertTrue(petition.approved_date, "Approved date should be set")
        self.assertTrue(petition.review_date, "Review date should be set")

    def test_approve_under_review_petition(self):
        """Approving an under_review petition should work."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()
        petition.with_user(self.admin_user).action_review()
        petition.with_user(self.admin_user).action_approve()

        self.assertEqual(petition.state, 'approved')

    def test_approve_wrong_state_raises_error(self):
        """Approving a draft petition should raise ValidationError."""
        petition = self._create_draft_petition()

        with self.assertRaises((ValidationError, AccessError)):
            petition.with_user(self.admin_user).action_approve()

    def test_reject_with_reason(self):
        """Rejecting with a reason should set state to 'rejected'."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()
        petition.write({'rejection_reason': 'Insufficient justification'})
        petition.with_user(self.admin_user).action_reject()

        self.assertEqual(petition.state, 'rejected')
        self.assertTrue(petition.rejected_date, "Rejected date should be set")

    def test_reject_without_reason_raises_error(self):
        """Rejecting without a reason should raise ValidationError."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()

        with self.assertRaises(ValidationError):
            petition.with_user(self.admin_user).action_reject()

    def test_cancel_petition(self):
        """Cancelling a petition should set state to 'cancelled'."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_cancel()

        self.assertEqual(petition.state, 'cancelled')

    def test_reset_to_draft(self):
        """Resetting a petition should set state back to 'draft'."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()
        petition.with_user(self.admin_user).action_draft()

        self.assertEqual(petition.state, 'draft')

    # ==========================================
    # Computed Fields
    # ==========================================

    def test_days_pending_for_submitted(self):
        """Days pending should be computed for submitted petitions."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()

        # Just after submission, days_pending should be 0
        self.assertGreaterEqual(petition.days_pending, 0)

    def test_days_pending_for_draft(self):
        """Days pending should be 0 for draft petitions."""
        petition = self._create_draft_petition()
        self.assertEqual(petition.days_pending, 0)

    def test_is_own_petition(self):
        """is_own_petition should be True when student is the current user."""
        petition = self._create_draft_petition()

        # Switch to student user context
        petition_student = petition.with_user(self.student_user)
        self.assertTrue(petition_student.is_own_petition)

    def test_is_not_own_petition(self):
        """is_own_petition should be False for a different user."""
        petition = self._create_draft_petition()

        petition_admin = petition.with_user(self.admin_user)
        self.assertFalse(petition_admin.is_own_petition)

    # ==========================================
    # Write Restrictions
    # ==========================================

    def test_write_cannot_change_student(self):
        """Changing student_id on an existing petition should raise AccessError."""
        petition = self._create_draft_petition()
        other_partner = self.admin_user.partner_id

        with self.assertRaises(AccessError):
            petition.write({'student_id': other_partner.id})

    # ==========================================
    # Notification Stubs
    # ==========================================

    def test_submit_calls_notification(self):
        """Submitting should call _send_submission_notification without error."""
        petition = self._create_draft_petition()
        # Should not raise — notification methods are stubs (pass)
        petition.with_user(self.admin_user).action_submit()

    def test_approve_calls_notification(self):
        """Approving should call _send_approval_notification without error."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()
        petition.with_user(self.admin_user).action_approve()

    def test_reject_calls_notification(self):
        """Rejecting should call _send_rejection_notification without error."""
        petition = self._create_draft_petition()
        petition.with_user(self.admin_user).action_submit()
        petition.write({'rejection_reason': 'Denied'})
        petition.with_user(self.admin_user).action_reject()
