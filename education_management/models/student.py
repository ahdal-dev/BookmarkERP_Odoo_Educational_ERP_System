from odoo import models, fields, api
import base64
import requests
import logging

_logger = logging.getLogger(__name__)

class Student(models.Model):
    _name = 'education.student'
    _description = 'Student Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Full Name', required=True, tracking=True)
    student_id = fields.Char(string='Student ID', required=True, copy=False, readonly=True,
                             default=lambda self: self._generate_student_id())
    national_id = fields.Char(string='National ID Number', tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    address = fields.Text(string='Address', tracking=True)
    
    # ID Document Upload for OCR
    id_document = fields.Binary(string='ID Document', attachment=True)
    id_document_filename = fields.Char(string='ID Document Filename')

    # Academic Information
    enrollment_date = fields.Date(string='Enrollment Date', default=fields.Date.today())
    current_semester = fields.Char(string='Current Semester')
    gpa = fields.Float(string='GPA', digits=(3, 2))

    # Relations
    course_ids = fields.Many2many('education.course', string='Enrolled Courses')

    # Status
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _generate_student_id(self):
        # Generate a unique student ID
        last_student = self.search([], order='student_id desc', limit=1)
        if last_student:
            last_id = int(last_student.student_id[3:])  # Remove 'STU' prefix
            new_id = last_id + 1
        else:
            new_id = 1001
        return f'STU{new_id:04d}'
    
    @api.onchange('id_document')
    def _onchange_id_document(self):
        """Process ID document using OCR when uploaded"""
        if self.id_document:
            try:
                # OCR service URL
                ocr_service_url = 'http://localhost:5000/ocr'
                
                # Decode base64 image
                image_bytes = base64.b64decode(self.id_document)
                
                # Prepare file for upload
                files = {
                    'file': ('id_document.jpg', image_bytes, 'image/jpeg')
                }
                
                # Send request to OCR service
                response = requests.post(ocr_service_url, files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    ocr_data = result.get('result', {})
                    
                    # Auto-fill fields with OCR data
                    if ocr_data.get('nid') or ocr_data.get('back_nid'):
                        self.national_id = ocr_data.get('nid', '') or ocr_data.get('back_nid', '')
                    
                    if ocr_data.get('name'):
                        self.name = ocr_data.get('name', '')
                    
                    if ocr_data.get('address'):
                        self.address = ocr_data.get('address', '')
                    
                    return {
                        'warning': {
                            'title': 'OCR Success',
                            'message': 'ID document processed successfully! Fields have been auto-filled.',
                        }
                    }
                else:
                    error_msg = result.get('error', 'Unknown error') if 'result' in locals() else 'OCR service error'
                    _logger.warning(f"OCR processing failed: {error_msg}")
                    return {
                        'warning': {
                            'title': 'OCR Warning',
                            'message': f'OCR processing failed: {error_msg}. Please fill fields manually.',
                        }
                    }
                    
            except requests.exceptions.RequestException as e:
                _logger.error(f"Failed to connect to OCR service: {str(e)}")
                return {
                    'warning': {
                        'title': 'OCR Service Unavailable',
                        'message': 'Could not connect to OCR service. Please fill fields manually.',
                    }
                }
            except Exception as e:
                _logger.error(f"Error processing ID document: {str(e)}")
                return {
                    'warning': {
                        'title': 'OCR Error',
                        'message': f'Error processing document: {str(e)}. Please fill fields manually.',
                    }
                }

    def name_get(self):
        return [(student.id, f'{student.student_id} - {student.name}') for student in self]
