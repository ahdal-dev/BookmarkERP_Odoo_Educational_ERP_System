# -*- coding: utf-8 -*-

from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase


class TestAdmissionAcceptanceFlow(TransactionCase):
    """Tests for the enhanced action_accept flow: user provisioning,
    mailbox provisioning, idempotency, and field tracking."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.program = cls.env['school.program'].create({
            'name': 'Computer Science',
            'code': 'CS',
            'duration': 4,
        })
        cls.base_data = {
            'name': 'Jane Smith',
            'email': 'jane.smith@personal.example.com',
            'phone': '+1234567890',
            'national_id': 'NAT999TEST',
            'program_id': cls.program.id,
        }

    # ── helpers ───────────────────────────────────────────────────────────

    def _make_under_review(self, extra=None):
        data = dict(self.base_data, **(extra or {}))
        admission = self.env['school.admission'].create(data)
        admission.action_submit()
        admission.action_under_review()
        return admission

    def _success_result(self, ext_id='ext-001'):
        return {'status': 'success', 'external_id': ext_id, 'error_message': False}

    def _failed_result(self, msg='Provider error'):
        return {'status': 'failed', 'external_id': False, 'error_message': msg}

    # ── state & login email ───────────────────────────────────────────────

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_accept_sets_state_accepted(self, mock_prov):
        mock_prov.return_value = self._success_result()
        admission = self._make_under_review()
        admission.action_accept()
        self.assertEqual(admission.state, 'accepted')

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_accept_generates_login_email(self, mock_prov):
        mock_prov.return_value = self._success_result()
        admission = self._make_under_review()
        admission.action_accept()
        self.assertTrue(admission.generated_login_email, 'Login email should be set')
        self.assertIn('@', admission.generated_login_email)

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_login_email_uses_reference_and_configured_domain(self, mock_prov):
        mock_prov.return_value = self._success_result()
        self.env['ir.config_parameter'].sudo().set_param(
            'edu_mang_admission.mailbox_domain', 'testschool.example.edu'
        )
        admission = self._make_under_review()
        admission.action_accept()
        self.assertTrue(
            admission.generated_login_email.endswith('@testschool.example.edu'),
            'Login email domain should use the configured system parameter.',
        )
        # Local part should be derived from reference (lowercased, sanitised)
        expected_local = admission.reference.lower()
        self.assertEqual(
            admission.generated_login_email,
            '%s@testschool.example.edu' % expected_local,
        )

    # ── mailbox status fields ─────────────────────────────────────────────

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_mailbox_success_populates_fields(self, mock_prov):
        mock_prov.return_value = self._success_result('ext-abc')
        admission = self._make_under_review()
        admission.action_accept()
        self.assertEqual(admission.mailbox_status, 'success')
        self.assertEqual(admission.mailbox_external_id, 'ext-abc')
        self.assertTrue(admission.mailbox_created_at, 'mailbox_created_at should be set')
        self.assertFalse(admission.mailbox_error_message)

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_mailbox_failure_does_not_crash_and_records_error(self, mock_prov):
        mock_prov.return_value = self._failed_result('Connection timeout')
        admission = self._make_under_review()
        # Must NOT raise; acceptance must still succeed
        result = admission.action_accept()
        self.assertTrue(result)
        self.assertEqual(admission.state, 'accepted')
        self.assertEqual(admission.mailbox_status, 'failed')
        self.assertEqual(admission.mailbox_error_message, 'Connection timeout')
        self.assertFalse(admission.mailbox_created_at)

    # ── portal user creation ──────────────────────────────────────────────

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_accept_creates_portal_user(self, mock_prov):
        mock_prov.return_value = self._success_result()
        admission = self._make_under_review()
        admission.action_accept()
        login_email = admission.generated_login_email
        user = self.env['res.users'].sudo().search(
            [('login', '=', login_email)], limit=1
        )
        self.assertTrue(user, 'A portal user should be created for the login email')
        portal_group = self.env.ref('base.group_portal')
        self.assertIn(portal_group, user.group_ids)

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_accept_user_email_set_to_personal_email(self, mock_prov):
        mock_prov.return_value = self._success_result()
        admission = self._make_under_review()
        admission.action_accept()
        login_email = admission.generated_login_email
        user = self.env['res.users'].sudo().search(
            [('login', '=', login_email)], limit=1
        )
        self.assertEqual(
            user.email, self.base_data['email'],
            'Portal user email should be the applicant personal email for password-reset delivery',
        )

    # ── idempotency ───────────────────────────────────────────────────────

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_accept_idempotent_does_not_duplicate_user(self, mock_prov):
        """Calling action_accept twice on an already-accepted record must not
        create a second portal user or re-provision the mailbox."""
        mock_prov.return_value = self._success_result()
        admission = self._make_under_review()
        admission.action_accept()
        login_email = admission.generated_login_email
        call_count_after_first = mock_prov.call_count

        # Force state back to simulate a UI re-click or programmatic retry
        admission.write({'state': 'accepted'})  # already accepted
        admission.action_accept()               # idempotency guard should skip

        users = self.env['res.users'].sudo().search([('login', '=', login_email)])
        self.assertEqual(len(users), 1, 'Should NOT create a duplicate portal user')
        self.assertEqual(
            mock_prov.call_count, call_count_after_first,
            '_provision_mailbox should not be called again on an already-accepted record',
        )

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_accept_idempotent_only_when_login_email_set(self, mock_prov):
        """If state is already accepted but generated_login_email is empty
        (e.g. manual data fix), re-provisioning SHOULD run."""
        mock_prov.return_value = self._success_result()
        admission = self.env['school.admission'].create(self.base_data)
        # Simulate a record that was accepted without the new fields being set
        admission.write({'state': 'accepted', 'generated_login_email': False})
        admission.action_accept()
        self.assertTrue(admission.generated_login_email)
        self.assertTrue(mock_prov.called, '_provision_mailbox should run when login email is missing')

    # ── _provision_mailbox dispatcher ─────────────────────────────────────

    def test_provision_mailbox_none_provider_returns_success(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'edu_mang_admission.mailbox_provider', 'none'
        )
        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox('test@school.edu', 'Test User')
        self.assertEqual(result['status'], 'success')

    def test_provision_mailbox_unset_provider_defaults_to_none(self):
        # Ensure param is absent / empty
        self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'edu_mang_admission.mailbox_provider')]
        ).unlink()
        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox('test@school.edu', 'Test User')
        self.assertEqual(result['status'], 'success')

    def test_provision_mailbox_unknown_provider_returns_failed(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'edu_mang_admission.mailbox_provider', 'unknown_xyz'
        )
        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox('test@school.edu', 'Test User')
        self.assertEqual(result['status'], 'failed')
        self.assertIn('unknown', result['error_message'].lower())

    # ── HTTP adapter unit tests ───────────────────────────────────────────

    def _setup_http_params(self, url='https://mail.example.com/api', token='s3cr3t'):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('edu_mang_admission.mailbox_provider', 'http')
        ICP.set_param('edu_mang_admission.api_base_url', url)
        ICP.set_param('edu_mang_admission.api_token', token)

    @patch('requests.post')
    def test_http_adapter_success_201(self, mock_post):
        self._setup_http_params()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'mailbox-xyz-789'}
        mock_post.return_value = mock_response

        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox_http('test@school.edu', 'Test User')

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['external_id'], 'mailbox-xyz-789')
        self.assertFalse(result['error_message'])

    @patch('requests.post')
    def test_http_adapter_success_200_no_id(self, mock_post):
        """200 with no id in body still succeeds; external_id is False."""
        self._setup_http_params()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        mock_post.return_value = mock_response

        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox_http('test@school.edu', 'Test User')

        self.assertEqual(result['status'], 'success')
        self.assertFalse(result['external_id'])

    @patch('requests.post')
    def test_http_adapter_client_error_no_retry(self, mock_post):
        """4xx errors should NOT be retried (bad request, auth error, etc.)."""
        self._setup_http_params()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'message': 'Invalid email format'}
        mock_post.return_value = mock_response

        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox_http('bad-email', 'Test User')

        self.assertEqual(result['status'], 'failed')
        self.assertEqual(mock_post.call_count, 1, '4xx errors must not be retried')

    @patch('requests.post')
    def test_http_adapter_server_error_retries_three_times(self, mock_post):
        """5xx errors should be retried up to MAX_RETRIES (2 extra = 3 total)."""
        self._setup_http_params()
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.json.return_value = {'message': 'Service Unavailable'}
        mock_post.return_value = mock_response

        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox_http('test@school.edu', 'Test User')

        self.assertEqual(result['status'], 'failed')
        self.assertEqual(mock_post.call_count, 3, 'Should attempt 1 + 2 retries = 3 calls')

    @patch('requests.post')
    def test_http_adapter_timeout_retries(self, mock_post):
        """Timeouts should be retried; all retries exhausted → failed."""
        from requests.exceptions import Timeout
        self._setup_http_params()
        mock_post.side_effect = Timeout('read timeout')

        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox_http('test@school.edu', 'Test User')

        self.assertEqual(result['status'], 'failed')
        self.assertIn('timed out', result['error_message'].lower())
        self.assertEqual(mock_post.call_count, 3)

    def test_http_adapter_no_base_url_returns_failed(self):
        """Missing api_base_url should return failed immediately."""
        self.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'edu_mang_admission.api_base_url')]
        ).unlink()
        self.env['ir.config_parameter'].sudo().set_param(
            'edu_mang_admission.mailbox_provider', 'http'
        )
        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox_http('test@school.edu', 'Test User')
        self.assertEqual(result['status'], 'failed')
        self.assertIn('api_base_url', result['error_message'])

    @patch('requests.post')
    def test_http_adapter_non_json_response_body_handled(self, mock_post):
        """A 500 with a non-JSON body should not raise; error_message uses HTTP status."""
        self._setup_http_params()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError('no JSON')
        mock_post.return_value = mock_response

        admission = self.env['school.admission'].create(self.base_data)
        result = admission._provision_mailbox_http('test@school.edu', 'Test User')

        self.assertEqual(result['status'], 'failed')
        self.assertIn('500', result['error_message'])

    # ── return value ──────────────────────────────────────────────────────

    @patch(
        'odoo.addons.edu_mang_admission.models.admission.SchoolAdmission._provision_mailbox'
    )
    def test_action_accept_returns_true(self, mock_prov):
        mock_prov.return_value = self._success_result()
        admission = self._make_under_review()
        result = admission.action_accept()
        self.assertTrue(result)
