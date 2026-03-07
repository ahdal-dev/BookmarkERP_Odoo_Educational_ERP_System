from odoo import http, fields
from odoo.http import request
import base64
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class AdmissionController(http.Controller):
    
    @http.route('/petetion/apply', type='http', auth='public', website=True, sitemap=True)
    def petetion_apply(self, **kwargs):
        try:
            petetions = request.env['petetion.petetion'].sudo().search([
                ('active', '=', True)
            ])
            
            values = {
                'petetions': petetions,
                'page_name': 'Submit A Petetion',
            }
            return request.render('petetion_system.apply_online_form', values)
        except Exception as e:
            _logger.error(f"Error rendering petetion form: {str(e)}")
            return request.render('website.404')
    
    @http.route('/petetion/submit', type='http', auth='public', methods=['POST'], 
                csrf=False)
    def petetion_submit(self, **kwargs):
        try:
            name = request.params.get('name', '').strip()
            email = request.params.get('email', '').strip()
            phone = request.params.get('phone', '').strip()
            # national_id = request.params.get('national_id', '').strip()
            # previous_school = request.params.get('previous_school', '').strip()
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
            if not program_id:
                errors.append('Program selection is required')
            
            if errors:
                petetions = request.env['petetion.petetion'].sudo().search([
                    ('active', '=', True)
                ])
                form_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'gpa': gpa,
                    'program_id': program_id,
                    'notes': notes,
                }
                return request.render('petetion_system.apply_online_form', {
                    'petetions': petetions,
                    'errors': errors,
                    'form_data': form_data,
                }, status=400)
            
            transcript_document = False
            transcript_filename = False
            
            # if 'transcript_document' in request.httprequest.files:
            #     file = request.httprequest.files['transcript_document']
            #     if file and file.filename:
            #         transcript_document = base64.b64encode(file.read())
            #         transcript_filename = file.filename
            
            try:
                gpa = float(gpa) if gpa else 0.0
            except (ValueError, TypeError):
                gpa = 0.0
            
            petetion_vals = {
                'name': name,
                'email': email,
                'phone': phone,
                'gpa': gpa,
                'program_id': int(program_id),
                'transcript_document': transcript_document,
                'transcript_filename': transcript_filename,
                'notes': notes,
                'state': 'submitted',
                'application_date': datetime.now(),
            }
            
            petetion = request.env['petetion.petetion'].sudo().create(petetion_vals)
            _logger.info(f"Petetion application created: {petetion.reference} for {name}")
            return request.redirect(f'/petetion/thank_you?ref={petetion.reference}')
        except Exception as e:
            _logger.error(f"Error submitting petetion: {str(e)}", exc_info=True)
            return request.redirect('/petetion/apply?error=submission')
    
    @http.route('/petetion/thank_you', type='http', auth='public', website=True)
    def petetion_thank_you(self, **kwargs):
        reference = kwargs.get('ref', 'N/A')
        values = {
            'reference': reference,
            'page_name': 'Petetion Submitted',
        }
        return request.render('petetion_system.petetion_success', values)
    
    @http.route('/petetion/check_status', type='http', auth='public', website=True, sitemap=True)
    def check_petetion_status(self, **kwargs):
        reference = kwargs.get('reference', '').strip()
        petetion = False
        error = False
        
        if reference:
            petetion = request.env['petetion.petetion'].sudo().search([
                ('reference', '=', reference)
            ], limit=1)
            
            if not petetion:
                error = 'Application not found. Please check your reference number.'
        
        values = {
            'petetion': petetion,
            'error': error,
            'reference': reference,
            'page_name': 'Check Application Status',
        }
        return request.render('petetion_system.check_status_form', values)
