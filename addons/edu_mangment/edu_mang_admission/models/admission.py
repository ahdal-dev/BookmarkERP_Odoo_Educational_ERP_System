import logging
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SchoolAdmission(models.Model):
    _name = 'school.admission'
    _description = 'School Admission Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Applicant Name',
        required=True,
        tracking=True
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True
    )
    
    phone = fields.Char(
        string='Phone Number',
        required=True,
        tracking=True
    )
    
    national_id = fields.Char(
        string='National ID',
        required=True,
        tracking=True
    )
    
    address = fields.Text(
        string='Address',
        tracking=True
    )
    
    previous_school = fields.Char(
        string='Previous School',
        tracking=True
    )
    
    gpa = fields.Float(
        string='GPA',
        digits=(3, 2),
        tracking=True
    )
    
    program_id = fields.Many2one(
        'school.program',
        string='Program',
        required=True,
        tracking=True
    )
    
    transcript_document = fields.Binary(
        string='Transcript/Documents',
        attachment=True
    )
    
    transcript_filename = fields.Char(
        string='Filename'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)
    
    reference = fields.Char(
        string='Reference',
        readonly=True,
        copy=False
    )
    
    application_date = fields.Datetime(
        string='Application Date',
        readonly=True
    )
    
    notes = fields.Text(
        string='Notes'
    )

    # ── Account & mailbox provisioning fields ──────────────────────────────
    generated_login_email = fields.Char(
        string='Login Email',
        readonly=True,
        copy=False,
        tracking=True,
    )
    mailbox_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], string='Mailbox Status', readonly=True, copy=False, tracking=True)
    mailbox_external_id = fields.Char(
        string='Mailbox External ID',
        readonly=True,
        copy=False,
    )
    mailbox_error_message = fields.Text(
        string='Mailbox Error',
        readonly=True,
        copy=False,
    )
    mailbox_created_at = fields.Datetime(
        string='Mailbox Provisioned At',
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', False) == False:
                vals['reference'] = self.env['ir.sequence'].next_by_code('school.admission') or 'New'
        return super(SchoolAdmission, self).create(vals_list)
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError('Please enter a valid email address.')
    
    @api.constrains('gpa')
    def _check_gpa(self):
        for record in self:
            if record.gpa and (record.gpa < 0 or record.gpa > 4.0):
                raise ValidationError('GPA must be between 0.0 and 4.0')
    
    def action_submit(self):
        for record in self:
            record.write({
                'state': 'submitted',
                'application_date': fields.Datetime.now()
            })
        return True
    
    def action_under_review(self):
        self.write({'state': 'under_review'})
        return True
    
    def action_accept(self):
        """Accept admission(s), provision a portal user and mailbox, then send welcome email.

        The operation is idempotent: re-calling on an already-accepted record that
        has a ``generated_login_email`` is a no-op (no duplicate user/mailbox).
        If mailbox provisioning fails the record is still accepted and the error
        is recorded in ``mailbox_error_message``; acceptance is never rolled back
        due to a provisioning failure.

        Configurable system parameters
        --------------------------------
        edu_mang_admission.mailbox_domain   – login email domain   (default: school.edu)
        edu_mang_admission.mailbox_provider – 'none' | 'http'      (default: none)
        edu_mang_admission.api_base_url     – REST endpoint base URL
        edu_mang_admission.api_token        – bearer token (never logged)
        """
        ICP = self.env['ir.config_parameter'].sudo()
        domain = ICP.get_param('edu_mang_admission.mailbox_domain') or 'school.edu'
        portal_group = self.env.ref('base.group_portal')

        for record in self:
            # ── Idempotency guard ──────────────────────────────────────────
            # Skip provisioning if already accepted with a login email assigned.
            if record.state == 'accepted' and record.generated_login_email:
                continue

            # 1. Set state
            record.write({'state': 'accepted'})

            # 2. Generate deterministic login email
            #    Use the sequence reference (e.g. ADM00001) as local-part;
            #    fall back to the numeric id when reference is missing.
            local_raw = (record.reference or str(record.id)).lower()
            local_part = re.sub(r'[^a-z0-9._-]', '', local_raw) or str(record.id)
            login_email = '%s@%s' % (local_part, domain)

            # 3. Create or reuse portal user (idempotent by login)
            existing_user = self.env['res.users'].sudo().search(
                [('login', '=', login_email)], limit=1
            )
            if not existing_user:
                # no_reset_password suppresses Odoo's auto-invitation email;
                # our custom acceptance email below handles communication.
                # In Odoo 19 the field is 'group_ids' (not 'groups_id').
                # (6, 0, [...]) replaces all groups, ensuring the user only
                # belongs to the portal group (not the default internal group).
                self.env['res.users'].sudo().with_context(no_reset_password=True).create({
                    'name': record.name,
                    'login': login_email,
                    'email': record.email,
                    'group_ids': [(6, 0, [portal_group.id])],
                })

            # 4. Provision mailbox via configured provider
            result = record._provision_mailbox(login_email, record.name)

            # 5. Persist provisioning outcome
            vals = {
                'generated_login_email': login_email,
                'mailbox_status': result['status'],
                'mailbox_error_message': result.get('error_message') or False,
                'mailbox_external_id': result.get('external_id') or False,
            }
            if result['status'] == 'success':
                vals['mailbox_created_at'] = fields.Datetime.now()
            record.write(vals)

            # 6. Chatter note (internal)
            if result['status'] == 'success':
                record.message_post(
                    body='Admission accepted. Login email: <b>%s</b>. '
                         'Mailbox provisioned successfully.' % login_email,
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )
            else:
                record.message_post(
                    body='Admission accepted. Login email: <b>%s</b>. '
                         'Mailbox provisioning <b>%s</b>: %s' % (
                             login_email,
                             result['status'],
                             result.get('error_message') or 'No details',
                         ),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )

            # 7. Send acceptance welcome email to applicant's personal email
            template = self.env.ref(
                'edu_mang_admission.email_template_admission_accepted',
                raise_if_not_found=False,
            )
            if template:
                try:
                    template.send_mail(record.id, force_send=True)
                except Exception as exc:
                    _logger.error(
                        'Failed to send acceptance email for admission %s: %s',
                        record.reference, exc, exc_info=True,
                    )

        return True
    
    def action_reject(self):
        """Reject admission(s) and send rejection notification email."""
        for record in self:
            record.write({'state': 'rejected'})

            # Send rejection notification email
            template = self.env.ref(
                'edu_mang_admission.email_template_admission_rejected',
                raise_if_not_found=False,
            )
            if template:
                try:
                    template.send_mail(record.id, force_send=True)
                except Exception as exc:
                    _logger.error(
                        'Failed to send rejection email for admission %s: %s',
                        record.reference, exc, exc_info=True,
                    )

        return True
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        return True

    # ── Mailbox provisioning service ───────────────────────────────────────

    def _provision_mailbox(self, login_email, display_name):
        """Provision a mailbox for *login_email* via the configured provider.

        Returns a normalised result dict::

            {
                'status':        'success' | 'failed' | 'pending',
                'external_id':   str | False,
                'error_message': str | False,
            }

        Provider is selected via system parameter
        ``edu_mang_admission.mailbox_provider``.

        Recognised values:

        * ``none`` (default) – no external mailbox; always reports success.
        * ``http`` – generic HTTP REST adapter (see :meth:`_provision_mailbox_http`).
        """
        provider = (
            self.env['ir.config_parameter']
            .sudo()
            .get_param('edu_mang_admission.mailbox_provider') or 'none'
        )
        if provider == 'none':
            return {'status': 'success', 'external_id': False, 'error_message': False}
        if provider == 'http':
            return self._provision_mailbox_http(login_email, display_name)
        return {
            'status': 'failed',
            'external_id': False,
            'error_message': 'Unknown mailbox provider: %s' % provider,
        }

    def _provision_mailbox_http(self, login_email, display_name):
        """Generic HTTP REST adapter for mailbox provisioning.

        Reads configuration from system parameters:

        * ``edu_mang_admission.api_base_url`` – REST API base URL
        * ``edu_mang_admission.api_token``    – bearer token (**never** logged)

        The adapter posts to ``{api_base_url}/mailboxes`` with JSON body::

            {"email": "<login_email>", "display_name": "<display_name>"}

        A 200 or 201 response is treated as success.  5xx responses are
        retried up to 2 additional times; 4xx errors abort immediately.
        """
        try:
            import requests
            from requests.exceptions import Timeout, RequestException
        except ImportError:
            return {
                'status': 'failed',
                'external_id': False,
                'error_message': "Python 'requests' library is not available.",
            }

        ICP = self.env['ir.config_parameter'].sudo()
        api_base_url = (ICP.get_param('edu_mang_admission.api_base_url') or '').rstrip('/')
        api_token = ICP.get_param('edu_mang_admission.api_token') or ''

        if not api_base_url:
            return {
                'status': 'failed',
                'external_id': False,
                'error_message': 'System parameter edu_mang_admission.api_base_url is not set.',
            }

        url = '%s/mailboxes' % api_base_url
        headers = {'Content-Type': 'application/json'}
        if api_token:
            # Token is used in the header but intentionally never logged.
            headers['Authorization'] = 'Bearer %s' % api_token

        payload = {'email': login_email, 'display_name': display_name}
        MAX_RETRIES = 2
        TIMEOUT = 10
        last_error = 'Unknown error'

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
            except Timeout:
                last_error = 'Request timed out (attempt %d/%d)' % (attempt + 1, MAX_RETRIES + 1)
                continue
            except RequestException as exc:
                last_error = 'Network error: %s' % str(exc)
                continue

            if response.status_code in (200, 201):
                try:
                    data = response.json()
                except ValueError:
                    data = {}
                return {
                    'status': 'success',
                    'external_id': str(data.get('id', '')) or False,
                    'error_message': False,
                }

            # Parse error body safely (never log the token)
            try:
                err_body = response.json()
                last_error = (
                    err_body.get('message')
                    or err_body.get('error')
                    or 'HTTP %d' % response.status_code
                )
            except ValueError:
                last_error = 'HTTP %d' % response.status_code

            if response.status_code < 500:
                # Client-side error (4xx) – retrying will not help.
                break

        return {'status': 'failed', 'external_id': False, 'error_message': last_error}


class SchoolProgram(models.Model):
    _name = 'school.program'
    _description = 'School Academic Program'
    _order = 'name'

    name = fields.Char(
        string='Program Name',
        required=True
    )
    
    code = fields.Char(
        string='Program Code'
    )
    
    description = fields.Text(
        string='Description'
    )
    
    duration = fields.Integer(
        string='Duration (Years)'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    admission_ids = fields.One2many(
        'school.admission',
        'program_id',
        string='Admissions'
    )
    
    admission_count = fields.Integer(
        string='Applications',
        compute='_compute_admission_count'
    )
    
    @api.depends('admission_ids')
    def _compute_admission_count(self):
        for record in self:
            record.admission_count = len(record.admission_ids)
