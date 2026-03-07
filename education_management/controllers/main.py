import base64
import requests
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class EducationOCRController(http.Controller):
    
    @http.route('/education/ocr/process', type='jsonrpc', auth='user', methods=['POST'])
    def process_id_document(self, image_data, **kwargs):
        """
        Process ID document using OCR microservice
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            dict: Extracted data from ID document
        """
        try:
            # OCR service URL (adjust if needed)
            ocr_service_url = 'http://localhost:5000/ocr'
            
            # Decode base64 image
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Prepare file for upload
            files = {
                'file': ('id_document.jpg', image_bytes, 'image/jpeg')
            }
            
            # Send request to OCR service
            response = requests.post(ocr_service_url, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ocr_data = result.get('result', {})
                
                # Map OCR results to student fields
                extracted_data = {
                    'success': True,
                    'data': {
                        'national_id': ocr_data.get('nid', '') or ocr_data.get('back_nid', ''),
                        'name': ocr_data.get('name', ''),
                        'address': ocr_data.get('address', ''),
                    },
                    'raw_data': ocr_data
                }
                
                return extracted_data
            else:
                error_msg = result.get('error', 'Unknown error') if 'result' in locals() else 'OCR service returned error'
                _logger.error(f"OCR service error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to connect to OCR service: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to connect to OCR service: {str(e)}'
            }
        except Exception as e:
            _logger.error(f"Error processing ID document: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing document: {str(e)}'
            }
