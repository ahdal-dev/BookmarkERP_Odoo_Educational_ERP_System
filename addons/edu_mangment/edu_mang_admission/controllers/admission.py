from odoo import http, fields
from odoo.http import request
import base64
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class AdmissionController(http.Controller):
    
    @http.route('/admission/apply', type='http', auth='public', website=True, sitemap=True)
    def admission_apply(self, **kwargs):
        try:
            programs = request.env['school.program'].sudo().search([
                ('active', '=', True)
            ])
            
            values = {
                'programs': programs,
                'page_name': 'Apply for Admission',
            }
            return request.render('edu_mang_admission.apply_online_form', values)
        except Exception as e:
            _logger.error(f"Error rendering admission form: {str(e)}")
            return request.render('website.404')
    
    @http.route('/admission/submit', type='http', auth='public', methods=['POST'], 
                website=True, csrf=False)
    def admission_submit(self, **kwargs):
        try:
            name = request.params.get('name', '').strip()
            email = request.params.get('email', '').strip()
            phone = request.params.get('phone', '').strip()
            national_id = request.params.get('national_id', '').strip()
            address = request.params.get('address', '').strip()
            previous_school = request.params.get('previous_school', '').strip()
            gpa = request.params.get('gpa', 0.0)
            program_id = request.params.get('program_id')
            notes = request.params.get('notes', '').strip()
            
            errors = []
            if not name:
                errors.append('Name is required')
            if not email:
                errors.append('Email is required')
            if not phone:
                errors.append('Phone number is required')
            if not national_id:
                errors.append('National ID is required')
            if not program_id:
                errors.append('Program selection is required')
            
            if errors:
                programs = request.env['school.program'].sudo().search([
                    ('active', '=', True)
                ])
                form_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'national_id': national_id,
                    'address': address,
                    'previous_school': previous_school,
                    'gpa': gpa,
                    'program_id': program_id,
                    'notes': notes,
                }
                return request.render('edu_mang_admission.apply_online_form', {
                    'programs': programs,
                    'errors': errors,
                    'form_data': form_data,
                }, status=400)
            
            transcript_document = False
            transcript_filename = False

            if 'transcript_document' in request.httprequest.files:
                file = request.httprequest.files['transcript_document']
                if file and file.filename:
                    _ALLOWED_MIME = {'image/jpeg', 'image/png', 'application/pdf'}
                    _MAX_SIZE = 10 * 1024 * 1024  # 10 MB
                    content_type = file.content_type or ''
                    if content_type not in _ALLOWED_MIME:
                        return request.redirect(
                            '/admission/apply?error=invalid_file_type'
                        )
                    raw = file.read()
                    if len(raw) > _MAX_SIZE:
                        return request.redirect(
                            '/admission/apply?error=file_too_large'
                        )
                    transcript_document = base64.b64encode(raw)
                    transcript_filename = file.filename
            
            try:
                gpa = float(gpa) if gpa else 0.0
            except (ValueError, TypeError):
                gpa = 0.0
            
            admission_vals = {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'national_id': national_id,
                'previous_school': previous_school,
                'gpa': gpa,
                'program_id': int(program_id),
                'transcript_document': transcript_document,
                'transcript_filename': transcript_filename,
                'notes': notes,
                'state': 'submitted',
                'application_date': datetime.now(),
            }
            
            admission = request.env['school.admission'].sudo().create(admission_vals)
            template = request.env.ref('edu_mang_admission.email_template_admission_success').sudo()

            try:
                mail_id = template.send_mail(admission.id, force_send=True)
                _logger.info(f"Mail sent with ID: {mail_id}")
            except Exception as e:
                _logger.error(f"Failed to send mail: {str(e)}", exc_info=True)
            return request.redirect(f'/admission/thank_you?ref={admission.reference}')
        except Exception as e:
            _logger.error(f"Error submitting admission: {str(e)}", exc_info=True)
            return request.redirect('/admission/apply?error=submission')
    
    @http.route('/admission/thank_you', type='http', auth='public', website=True)
    def admission_thank_you(self, **kwargs):
        reference = kwargs.get('ref', 'N/A')
        values = {
            'reference': reference,
            'page_name': 'Application Submitted',
        }
        return request.render('edu_mang_admission.admission_success', values)
    
    @http.route('/admission/check_status', type='http', auth='public', website=True, sitemap=True)
    def check_admission_status(self, **kwargs):
        reference = kwargs.get('reference', '').strip()
        admission = False
        error = False
        
        if reference:
            admission = request.env['school.admission'].sudo().search([
                ('reference', '=', reference)
            ], limit=1)
            
            if not admission:
                error = 'Application not found. Please check your reference number.'
        
        values = {
            'admission': admission,
            'error': error,
            'reference': reference,
            'page_name': 'Check Application Status',
        }
        return request.render('edu_mang_admission.check_status_form', values)
