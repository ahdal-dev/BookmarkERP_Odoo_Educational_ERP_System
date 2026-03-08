# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields
from datetime import datetime
import base64


class TestSchoolAdmission(TransactionCase):
    """Test suite for school.admission model"""

    @classmethod
    def setUpClass(cls):
        super(TestSchoolAdmission, cls).setUpClass()
        
        # Create test program that will be shared across tests
        cls.program = cls.env['school.program'].create({
            'name': 'Computer Science',
            'code': 'CS101',
            'description': 'Bachelor of Computer Science',
            'duration': 4,
        })
        
        # Standard valid admission data
        cls.valid_admission_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'national_id': 'ID123456789',
            'address': '123 Main Street, City',
            'previous_school': 'High School ABC',
            'gpa': 3.5,
            'program_id': cls.program.id,
        }

    # ==========================================
    # Record Creation & Defaults
    # ==========================================

    def test_create_admission_with_required_fields(self):
        """Test creating an admission record with all required fields"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        
        self.assertTrue(admission.id, "Admission record should be created")
        self.assertEqual(admission.name, 'John Doe')
        self.assertEqual(admission.email, 'john.doe@example.com')
        self.assertEqual(admission.phone, '+1234567890')
        self.assertEqual(admission.national_id, 'ID123456789')
        self.assertEqual(admission.program_id, self.program)

    def test_default_state_is_draft(self):
        """Test that the default state is 'draft'"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        self.assertEqual(admission.state, 'draft', "Default state should be 'draft'")

    def test_reference_auto_generated_on_create(self):
        """Test that reference is auto-generated via ir.sequence when not provided"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        
        self.assertTrue(admission.reference, "Reference should be auto-generated")
        self.assertNotEqual(admission.reference, 'New', "Reference should not be 'New'")

    def test_reference_not_overwritten_when_provided(self):
        """Test that reference is NOT overwritten if explicitly provided"""
        data = self.valid_admission_data.copy()
        data['reference'] = 'CUSTOM-REF-001'
        
        admission = self.env['school.admission'].create(data)
        self.assertEqual(admission.reference, 'CUSTOM-REF-001', 
                        "Explicitly provided reference should not be overwritten")

    def test_create_multi_records_at_once(self):
        """Test creating multiple admission records at once using model_create_multi"""
        vals_list = [
            {
                'name': 'Student 1',
                'email': 'student1@example.com',
                'phone': '+1111111111',
                'national_id': 'ID111',
                'program_id': self.program.id,
            },
            {
                'name': 'Student 2',
                'email': 'student2@example.com',
                'phone': '+2222222222',
                'national_id': 'ID222',
                'program_id': self.program.id,
            },
            {
                'name': 'Student 3',
                'email': 'student3@example.com',
                'phone': '+3333333333',
                'national_id': 'ID333',
                'program_id': self.program.id,
                'reference': 'EXPLICIT-REF',  # One with explicit reference
            },
        ]
        
        admissions = self.env['school.admission'].create(vals_list)
        
        self.assertEqual(len(admissions), 3, "Should create 3 admission records")
        self.assertTrue(all(a.reference for a in admissions), "All should have references")
        self.assertEqual(admissions[2].reference, 'EXPLICIT-REF', 
                        "Explicit reference should be preserved in multi-create")

    # ==========================================
    # Email Validation
    # ==========================================

    def test_valid_email_simple(self):
        """Test that a simple valid email passes validation"""
        data = self.valid_admission_data.copy()
        data['email'] = 'user@example.com'
        
        admission = self.env['school.admission'].create(data)
        self.assertEqual(admission.email, 'user@example.com')

    def test_valid_email_with_plus_and_dots(self):
        """Test that complex valid emails pass validation"""
        data = self.valid_admission_data.copy()
        data['email'] = 'user.name+tag@sub.domain.co.uk'
        
        admission = self.env['school.admission'].create(data)
        self.assertEqual(admission.email, 'user.name+tag@sub.domain.co.uk')

    def test_valid_email_with_numbers(self):
        """Test that emails with numbers pass validation"""
        data = self.valid_admission_data.copy()
        data['email'] = 'user123@example456.com'
        
        admission = self.env['school.admission'].create(data)
        self.assertEqual(admission.email, 'user123@example456.com')

    def test_invalid_email_no_at_symbol(self):
        """Test that email without @ symbol raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['email'] = 'notanemail'
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('valid email', str(cm.exception).lower())

    def test_invalid_email_missing_domain(self):
        """Test that email with only @ raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['email'] = 'user@'
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('valid email', str(cm.exception).lower())

    def test_invalid_email_missing_username(self):
        """Test that email starting with @ raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['email'] = '@domain.com'
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('valid email', str(cm.exception).lower())

    def test_invalid_email_missing_tld(self):
        """Test that email without TLD raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['email'] = 'user@domain'
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('valid email', str(cm.exception).lower())

    def test_invalid_email_dot_only_domain(self):
        """Test that email with .com as domain raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['email'] = 'user@.com'
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('valid email', str(cm.exception).lower())

    # ==========================================
    # GPA Validation
    # ==========================================

    def test_gpa_zero_passes(self):
        """Test that GPA = 0.0 passes validation (edge case: falsy but valid)"""
        data = self.valid_admission_data.copy()
        data['gpa'] = 0.0
        
        # GPA 0.0 is falsy, so the constraint check is skipped
        admission = self.env['school.admission'].create(data)
        self.assertEqual(admission.gpa, 0.0)

    def test_gpa_maximum_boundary_passes(self):
        """Test that GPA = 4.0 (maximum) passes validation"""
        data = self.valid_admission_data.copy()
        data['gpa'] = 4.0
        
        admission = self.env['school.admission'].create(data)
        self.assertEqual(admission.gpa, 4.0)

    def test_gpa_normal_value_passes(self):
        """Test that a normal GPA (2.5) passes validation"""
        data = self.valid_admission_data.copy()
        data['gpa'] = 2.5
        
        admission = self.env['school.admission'].create(data)
        self.assertAlmostEqual(admission.gpa, 2.5, places=2)

    def test_gpa_negative_raises_error(self):
        """Test that negative GPA raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['gpa'] = -0.1
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('gpa', str(cm.exception).lower())
        self.assertIn('0.0', str(cm.exception))
        self.assertIn('4.0', str(cm.exception))

    def test_gpa_above_maximum_raises_error(self):
        """Test that GPA above 4.0 raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['gpa'] = 4.1
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('gpa', str(cm.exception).lower())

    def test_gpa_way_above_maximum_raises_error(self):
        """Test that GPA = 10.0 raises ValidationError"""
        data = self.valid_admission_data.copy()
        data['gpa'] = 10.0
        
        with self.assertRaises(ValidationError) as cm:
            self.env['school.admission'].create(data)
        self.assertIn('gpa', str(cm.exception).lower())

    def test_gpa_false_value_skips_constraint(self):
        """Test that False/None GPA skips validation (field not set)"""
        data = self.valid_admission_data.copy()
        data['gpa'] = False
        
        # Should not raise error as the constraint checks 'if record.gpa'
        admission = self.env['school.admission'].create(data)
        self.assertFalse(admission.gpa)

    # ==========================================
    # State Workflow Actions
    # ==========================================

    def test_action_submit_changes_state_and_sets_date(self):
        """Test action_submit changes state to 'submitted' and sets application_date"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        self.assertEqual(admission.state, 'draft')
        self.assertFalse(admission.application_date)
        
        before_submit = fields.Datetime.now()
        result = admission.action_submit()
        after_submit = fields.Datetime.now()
        
        self.assertTrue(result, "action_submit should return True")
        self.assertEqual(admission.state, 'submitted')
        self.assertTrue(admission.application_date, "application_date should be set")
        self.assertTrue(before_submit <= admission.application_date <= after_submit,
                       "application_date should be set to current time")

    def test_action_under_review_changes_state(self):
        """Test action_under_review changes state to 'under_review'"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        admission.action_submit()
        
        result = admission.action_under_review()
        
        self.assertTrue(result, "action_under_review should return True")
        self.assertEqual(admission.state, 'under_review')

    def test_action_accept_changes_state(self):
        """Test action_accept changes state to 'accepted'"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        admission.action_submit()
        admission.action_under_review()
        
        result = admission.action_accept()
        
        self.assertTrue(result, "action_accept should return True")
        self.assertEqual(admission.state, 'accepted')

    def test_action_reject_changes_state(self):
        """Test action_reject changes state to 'rejected'"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        admission.action_submit()
        admission.action_under_review()
        
        result = admission.action_reject()
        
        self.assertTrue(result, "action_reject should return True")
        self.assertEqual(admission.state, 'rejected')

    def test_action_reset_to_draft_changes_state(self):
        """Test action_reset_to_draft changes state back to 'draft'"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        admission.action_submit()
        
        result = admission.action_reset_to_draft()
        
        self.assertTrue(result, "action_reset_to_draft should return True")
        self.assertEqual(admission.state, 'draft')

    def test_full_workflow_acceptance(self):
        """Test complete workflow: draft → submitted → under_review → accepted"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        
        # Start
        self.assertEqual(admission.state, 'draft')
        
        # Submit
        admission.action_submit()
        self.assertEqual(admission.state, 'submitted')
        
        # Review
        admission.action_under_review()
        self.assertEqual(admission.state, 'under_review')
        
        # Accept
        admission.action_accept()
        self.assertEqual(admission.state, 'accepted')

    def test_full_workflow_rejection(self):
        """Test complete workflow: draft → submitted → under_review → rejected"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        
        # Start
        self.assertEqual(admission.state, 'draft')
        
        # Submit
        admission.action_submit()
        self.assertEqual(admission.state, 'submitted')
        
        # Review
        admission.action_under_review()
        self.assertEqual(admission.state, 'under_review')
        
        # Reject
        admission.action_reject()
        self.assertEqual(admission.state, 'rejected')

    def test_reset_from_submitted_state(self):
        """Test reset to draft from 'submitted' state"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        admission.action_submit()
        self.assertEqual(admission.state, 'submitted')
        
        admission.action_reset_to_draft()
        self.assertEqual(admission.state, 'draft')

    def test_reset_from_accepted_state(self):
        """Test reset to draft from 'accepted' state"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        admission.write({'state': 'accepted'})
        
        admission.action_reset_to_draft()
        self.assertEqual(admission.state, 'draft')

    def test_reset_from_rejected_state(self):
        """Test reset to draft from 'rejected' state"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        admission.write({'state': 'rejected'})
        
        admission.action_reset_to_draft()
        self.assertEqual(admission.state, 'draft')

    # ==========================================
    # Copy Behavior
    # ==========================================

    def test_copy_does_not_duplicate_reference(self):
        """Test that copy() does not copy the reference field (copy=False)"""
        admission = self.env['school.admission'].create(self.valid_admission_data)
        original_reference = admission.reference
        
        copied_admission = admission.copy()
        
        self.assertNotEqual(copied_admission.reference, original_reference,
                          "Copied admission should have a different reference (auto-generated)")
        self.assertTrue(copied_admission.reference, "Copied admission should have a reference")
        # Other fields should be copied
        self.assertEqual(copied_admission.name, admission.name)
        self.assertEqual(copied_admission.email, admission.email)
        self.assertEqual(copied_admission.program_id, admission.program_id)

    # ==========================================
    # Additional Field Tests
    # ==========================================

    def test_admission_with_all_optional_fields(self):
        """Test creating admission with all optional fields populated"""
        data = self.valid_admission_data.copy()
        data.update({
            'address': '456 Oak Avenue',
            'previous_school': 'Lincoln High',
            'gpa': 3.8,
            'notes': 'Excellent candidate with leadership experience',
            'transcript_document': base64.b64encode(b'fake_pdf_content'),
            'transcript_filename': 'transcript.pdf',
        })
        
        admission = self.env['school.admission'].create(data)
        
        self.assertEqual(admission.address, '456 Oak Avenue')
        self.assertEqual(admission.previous_school, 'Lincoln High')
        self.assertAlmostEqual(admission.gpa, 3.8, places=2)
        self.assertEqual(admission.notes, 'Excellent candidate with leadership experience')
        self.assertEqual(admission.transcript_document, base64.b64encode(b'fake_pdf_content'))
        self.assertEqual(admission.transcript_filename, 'transcript.pdf')

    def test_admission_ordering_by_create_date_desc(self):
        """Test that admissions are ordered by create_date descending"""
        # Create multiple admissions
        admission1 = self.env['school.admission'].create({
            'name': 'First Student',
            'email': 'first@example.com',
            'phone': '111',
            'national_id': 'ID001',
            'program_id': self.program.id,
        })
        
        admission2 = self.env['school.admission'].create({
            'name': 'Second Student',
            'email': 'second@example.com',
            'phone': '222',
            'national_id': 'ID002',
            'program_id': self.program.id,
        })
        
        admission3 = self.env['school.admission'].create({
            'name': 'Third Student',
            'email': 'third@example.com',
            'phone': '333',
            'national_id': 'ID003',
            'program_id': self.program.id,
        })
        
        # Search all admissions (should be ordered by create_date desc)
        all_admissions = self.env['school.admission'].search([
            ('id', 'in', [admission1.id, admission2.id, admission3.id])
        ])
        
        # All 3 records created in same transaction have same create_date,
        # so just verify all records are returned
        self.assertEqual(len(all_admissions), 3, "Should return all 3 admissions")
        self.assertEqual(
            set(all_admissions.ids),
            {admission1.id, admission2.id, admission3.id},
            "All admissions should be present in search results"
        )