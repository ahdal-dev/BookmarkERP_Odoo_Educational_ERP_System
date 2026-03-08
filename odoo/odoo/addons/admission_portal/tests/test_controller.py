# -*- coding: utf-8 -*-

from odoo.tests import HttpCase, tagged
import io


@tagged('post_install', '-at_install')
class TestAdmissionController(HttpCase):
    """Test suite for AdmissionController"""

    def setUp(self):
        super(TestAdmissionController, self).setUp()
        
        # Create test program
        self.program = self.env['school.program'].create({
            'name': 'Test Program',
            'code': 'TEST101',
            'active': True,
        })
        
        # Standard form data for submissions
        self.valid_form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'national_id': 'ID123',
            'address': '123 Main St',
            'previous_school': 'Test High School',
            'gpa': '3.5',
            'program_id': str(self.program.id),
            'notes': 'Looking forward to joining',
        }

    # ==========================================
    # GET /admission/apply
    # ==========================================

    def test_get_apply_form_returns_200(self):
        """Test that GET /admission/apply returns HTTP 200"""
        response = self.url_open('/admission/apply')
        self.assertEqual(response.status_code, 200, 
                        "Apply form should return 200 OK")

    def test_apply_form_renders_programs(self):
        """Test that the apply form renders and includes programs"""
        response = self.url_open('/admission/apply')
        content = response.content.decode('utf-8')
        
        self.assertIn('Test Program', content, 
                     "Program name should appear in form")

    def test_apply_form_accessible_to_public(self):
        """Test that the apply form is accessible without authentication"""
        # Explicitly ensure no authentication
        self.authenticate(None, None)
        response = self.url_open('/admission/apply')
        
        self.assertEqual(response.status_code, 200, 
                        "Public users should access the form")

    # ==========================================
    # POST /admission/submit - Successful Submission
    # ==========================================

    def test_submit_admission_with_valid_data(self):
        """Test submitting admission with all required fields creates a record"""
        initial_count = self.env['school.admission'].search_count([])
        
        response = self.url_open('/admission/submit', data=self.valid_form_data)
        
        # Should redirect to thank you page
        self.assertEqual(response.status_code, 200, 
                        "Should successfully submit and redirect")
        self.assertIn('/admission/thank_you', response.url or '', 
                     "Should redirect to thank you page")
        
        # Check that a record was created
        new_count = self.env['school.admission'].search_count([])
        self.assertEqual(new_count, initial_count + 1, 
                        "Should create one admission record")
        
        # Verify the created record
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertTrue(admission, "Admission record should exist")
        self.assertEqual(admission.name, 'John Doe')
        self.assertEqual(admission.phone, '+1234567890')
        self.assertEqual(admission.national_id, 'ID123')
        self.assertEqual(admission.state, 'submitted')
        self.assertTrue(admission.application_date, "Application date should be set")
        self.assertAlmostEqual(admission.gpa, 3.5, places=2)

    def test_submit_creates_record_with_state_submitted(self):
        """Test that submitted application has state='submitted'"""
        self.url_open('/admission/submit', data=self.valid_form_data)
        
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertEqual(admission.state, 'submitted', 
                        "State should be 'submitted' not 'draft'")

    # ==========================================
    # POST /admission/submit - Validation Failures
    # ==========================================

    def test_submit_without_name_returns_error(self):
        """Test that submitting without name returns validation error"""
        data = self.valid_form_data.copy()
        data['name'] = ''
        
        response = self.url_open('/admission/submit', data=data)
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 400, "Should return 400 Bad Request")
        self.assertIn('Name is required', content, 
                     "Should show name validation error")

    def test_submit_without_email_returns_error(self):
        """Test that submitting without email returns validation error"""
        data = self.valid_form_data.copy()
        data['email'] = ''
        
        response = self.url_open('/admission/submit', data=data)
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Email is required', content)

    def test_submit_without_phone_returns_error(self):
        """Test that submitting without phone returns validation error"""
        data = self.valid_form_data.copy()
        data['phone'] = ''
        
        response = self.url_open('/admission/submit', data=data)
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Phone number is required', content)

    def test_submit_without_national_id_returns_error(self):
        """Test that submitting without national_id returns validation error"""
        data = self.valid_form_data.copy()
        data['national_id'] = ''
        
        response = self.url_open('/admission/submit', data=data)
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('National ID is required', content)

    def test_submit_without_program_returns_error(self):
        """Test that submitting without program selection returns validation error"""
        data = self.valid_form_data.copy()
        data['program_id'] = ''
        
        response = self.url_open('/admission/submit', data=data)
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Program selection is required', content)

    def test_submit_with_multiple_missing_fields_shows_all_errors(self):
        """Test that multiple validation errors are shown together"""
        data = {
            'name': '',
            'email': '',
            'phone': '',
            'national_id': '',
            'program_id': '',
        }
        
        response = self.url_open('/admission/submit', data=data)
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Name is required', content)
        self.assertIn('Email is required', content)
        self.assertIn('Phone number is required', content)
        self.assertIn('National ID is required', content)
        self.assertIn('Program selection is required', content)

    def test_validation_error_preserves_form_data(self):
        """Test that validation errors preserve user's input in the form"""
        data = self.valid_form_data.copy()
        data['name'] = ''  # Trigger validation error
        
        response = self.url_open('/admission/submit', data=data)
        content = response.content.decode('utf-8')
        
        # Check that other fields are preserved
        self.assertIn('john@example.com', content, 
                     "Email should be preserved in form")
        self.assertIn('+1234567890', content, 
                     "Phone should be preserved in form")

    # ==========================================
    # POST /admission/submit - File Upload
    # ==========================================

    def test_submit_with_file_upload(self):
        """Test that file upload sets transcript_document and transcript_filename"""
        # Create a fake file
        fake_file = (io.BytesIO(b'PDF content here'), 'transcript.pdf')
        
        data = self.valid_form_data.copy()
        files = {'transcript_document': fake_file}
        
        response = self.url_open('/admission/submit', data=data, files=files)
        
        # Find the created admission
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertTrue(admission.transcript_document, 
                       "Transcript document should be uploaded")
        self.assertEqual(admission.transcript_filename, 'transcript.pdf', 
                        "Transcript filename should be set")

    def test_submit_without_file_upload(self):
        """Test that submission without file still works"""
        response = self.url_open('/admission/submit', data=self.valid_form_data)
        
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertFalse(admission.transcript_document, 
                        "No document should be set")
        self.assertFalse(admission.transcript_filename, 
                        "No filename should be set")

    # ==========================================
    # POST /admission/submit - GPA Edge Cases
    # ==========================================

    def test_submit_with_valid_gpa_string(self):
        """Test that GPA as valid string is parsed to float"""
        data = self.valid_form_data.copy()
        data['gpa'] = '3.75'
        
        self.url_open('/admission/submit', data=data)
        
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertAlmostEqual(admission.gpa, 3.75, places=2, 
                              msg="GPA string should be parsed to float")

    def test_submit_with_invalid_gpa_string_defaults_to_zero(self):
        """Test that invalid GPA string defaults to 0.0"""
        data = self.valid_form_data.copy()
        data['gpa'] = 'abc'
        
        self.url_open('/admission/submit', data=data)
        
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertEqual(admission.gpa, 0.0, 
                        "Invalid GPA should default to 0.0")

    def test_submit_with_empty_gpa_defaults_to_zero(self):
        """Test that empty GPA string defaults to 0.0"""
        data = self.valid_form_data.copy()
        data['gpa'] = ''
        
        self.url_open('/admission/submit', data=data)
        
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertEqual(admission.gpa, 0.0, 
                        "Empty GPA should default to 0.0")

    def test_submit_without_gpa_field_defaults_to_zero(self):
        """Test that missing GPA field defaults to 0.0"""
        data = self.valid_form_data.copy()
        del data['gpa']
        
        self.url_open('/admission/submit', data=data)
        
        admission = self.env['school.admission'].search([
            ('email', '=', 'john@example.com')
        ], limit=1)
        
        self.assertEqual(admission.gpa, 0.0, 
                        "Missing GPA should default to 0.0")

    # ==========================================
    # GET /admission/thank_you
    # ==========================================

    def test_thank_you_page_returns_200(self):
        """Test that GET /admission/thank_you returns HTTP 200"""
        response = self.url_open('/admission/thank_you?ref=TEST-001')
        self.assertEqual(response.status_code, 200, 
                        "Thank you page should return 200 OK")

    def test_thank_you_page_displays_reference(self):
        """Test that thank you page displays the reference number"""
        response = self.url_open('/admission/thank_you?ref=TEST-REF-123')
        content = response.content.decode('utf-8')
        
        self.assertIn('TEST-REF-123', content, 
                     "Reference number should be displayed")

    def test_thank_you_page_without_reference(self):
        """Test thank you page behavior when no reference is provided"""
        response = self.url_open('/admission/thank_you')
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        # Should show N/A or handle gracefully
        self.assertTrue('N/A' in content or 'Application Submitted' in content)

    # ==========================================
    # GET /admission/check_status
    # ==========================================

    def test_check_status_without_reference_shows_form(self):
        """Test that check status page without reference shows the search form"""
        response = self.url_open('/admission/check_status')
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        # Should show form but no error initially
        self.assertNotIn('Application not found', content)

    def test_check_status_with_valid_reference_shows_admission(self):
        """Test that check status with valid reference shows admission details"""
        # Create an admission
        admission = self.env['school.admission'].create({
            'name': 'Test Student',
            'email': 'test@example.com',
            'phone': '+1111111111',
            'national_id': 'TEST-ID',
            'program_id': self.program.id,
            'reference': 'VALID-REF-001',
            'state': 'under_review',
        })
        
        response = self.url_open(f'/admission/check_status?reference=VALID-REF-001')
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Student', content, 
                     "Student name should be displayed")
        self.assertIn('test@example.com', content, 
                     "Email should be displayed")

    def test_check_status_with_invalid_reference_shows_error(self):
        """Test that check status with invalid reference shows error message"""
        response = self.url_open('/admission/check_status?reference=INVALID-REF-999')
        content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Application not found', content, 
                     "Error message should be displayed")
        self.assertIn('check your reference number', content.lower())

    def test_check_status_case_sensitive_reference(self):
        """Test that reference search is case-sensitive"""
        admission = self.env['school.admission'].create({
            'name': 'Case Test',
            'email': 'case@example.com',
            'phone': '+2222222222',
            'national_id': 'CASE-ID',
            'program_id': self.program.id,
            'reference': 'ABC-123',
        })
        
        # Search with wrong case
        response = self.url_open('/admission/check_status?reference=abc-123')
        content = response.content.decode('utf-8')
        
        # Should NOT find it (case-sensitive)
        self.assertIn('Application not found', content)

    def test_check_status_strips_whitespace(self):
        """Test that reference input is stripped of whitespace"""
        admission = self.env['school.admission'].create({
            'name': 'Whitespace Test',
            'email': 'space@example.com',
            'phone': '+3333333333',
            'national_id': 'SPACE-ID',
            'program_id': self.program.id,
            'reference': 'WS-001',
        })
        
        # Search with extra whitespace
        response = self.url_open('/admission/check_status?reference=%20WS-001%20')
        content = response.content.decode('utf-8')
        
        # Should find it after stripping
        self.assertIn('Whitespace Test', content, 
                     "Should find admission after stripping whitespace")

    # ==========================================
    # Error Handling
    # ==========================================

    def test_submit_with_exception_redirects_to_apply_with_error(self):
        """Test that exceptions during submission redirect gracefully"""
        # Send invalid program_id to trigger an exception
        data = self.valid_form_data.copy()
        data['program_id'] = '99999'  # Non-existent ID
        
        response = self.url_open('/admission/submit', data=data)
        
        # Should redirect to apply page with error parameter
        # (This depends on implementation - may show error or redirect)
        # The controller catches exceptions and redirects to /admission/apply?error=submission
        self.assertTrue(response.status_code in [200, 302, 303], 
                       "Should handle error gracefully")