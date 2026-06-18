import base64
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SUPPORTED_FILETYPES = ('pdf', 'txt', 'docx', 'csv')


class ChatbotRagDocument(models.Model):
    _name = 'chatbot.rag.document'
    _description = 'Chatbot RAG Document'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Title', required=True, tracking=True)
    attachment = fields.Binary(string='File', attachment=True, required=True)
    filename = fields.Char(string='Filename')
    filetype = fields.Char(string='File Type', compute='_compute_filetype', store=True)

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('synced', 'Synced'),
            ('failed', 'Failed'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    rag_document_id = fields.Char(string='Backend Document ID', readonly=True, copy=False)
    chunk_count = fields.Integer(string='Chunks', readonly=True, copy=False)
    sync_date = fields.Datetime(string='Last Synced', readonly=True, copy=False)
    last_error = fields.Text(string='Last Error', readonly=True, copy=False)

    @api.depends('filename')
    def _compute_filetype(self):
        for doc in self:
            if doc.filename and '.' in doc.filename:
                doc.filetype = doc.filename.rsplit('.', 1)[-1].lower()
            else:
                doc.filetype = False

    # ------------------------------------------------------------------
    # Backend configuration helpers
    # ------------------------------------------------------------------
    def _get_backend_config(self):
        """Return (backend_url, org_id, user_id), validating they are set."""
        params = self.env['ir.config_parameter'].sudo()
        backend_url = (params.get_param('custom_chatbot_admin.backend_url') or '').rstrip('/')
        org_id = params.get_param('custom_chatbot_admin.rag_org_id') or ''
        user_id = params.get_param('custom_chatbot_admin.rag_user_id') or ''
        missing = []
        if not backend_url:
            missing.append(_('Chatbot Backend URL'))
        if not org_id:
            missing.append(_('RAG Organization ID'))
        if not user_id:
            missing.append(_('RAG Service User ID'))
        if missing:
            raise UserError(
                _('Missing chatbot configuration: %s.\nSet it in Settings → Chatbot.')
                % ', '.join(missing)
            )
        return backend_url, org_id, user_id

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_sync(self):
        """Push each document's file to the backend ingestion pipeline (/upload)."""
        import requests

        backend_url, org_id, user_id = self._get_backend_config()
        for doc in self:
            if not doc.attachment:
                raise UserError(_('Document "%s" has no file to sync.') % doc.name)
            if doc.filetype not in SUPPORTED_FILETYPES:
                raise UserError(
                    _('Unsupported file type "%s" for "%s". Allowed: %s.')
                    % (doc.filetype or '?', doc.name, ', '.join(SUPPORTED_FILETYPES))
                )

            file_bytes = base64.b64decode(doc.attachment)
            files = {'file': (doc.filename or doc.name, file_bytes)}
            data = {'org_id': org_id, 'user_id': user_id}
            try:
                resp = requests.post(
                    f"{backend_url}/upload", data=data, files=files, timeout=120
                )
            except Exception as exc:  # noqa: BLE001
                doc.write({'state': 'failed', 'last_error': str(exc)})
                _logger.warning("custom_chatbot_admin: sync failed for %s (%s)", doc.name, exc)
                raise UserError(
                    _('Could not reach the chatbot backend at %s.\n\n%s') % (backend_url, exc)
                )

            if resp.status_code == 409:
                doc.write({
                    'state': 'failed',
                    'last_error': _('Duplicate document: identical content already exists for this organization.'),
                })
                raise UserError(
                    _('"%s" is a duplicate of a document already in the backend.') % doc.name
                )
            if resp.status_code != 200:
                detail = self._extract_detail(resp)
                doc.write({'state': 'failed', 'last_error': detail})
                raise UserError(_('Backend error (%s): %s') % (resp.status_code, detail))

            result = resp.json()
            doc.write({
                'state': 'synced',
                'rag_document_id': str(result.get('document_id') or ''),
                'chunk_count': int(result.get('chunks') or 0),
                'sync_date': fields.Datetime.now(),
                'last_error': False,
            })
        return True

    def action_delete_from_backend(self):
        """Remove the synced document from the backend without deleting the Odoo record."""
        self._delete_backend_records()
        for doc in self:
            doc.write({
                'state': 'draft',
                'rag_document_id': False,
                'chunk_count': 0,
                'sync_date': False,
            })
        return True

    def _delete_backend_records(self):
        """Best-effort delete of the backend documents for the current recordset."""
        import requests

        params = self.env['ir.config_parameter'].sudo()
        backend_url = (params.get_param('custom_chatbot_admin.backend_url') or '').rstrip('/')
        user_id = params.get_param('custom_chatbot_admin.rag_user_id') or ''
        if not backend_url or not user_id:
            return
        for doc in self:
            if not doc.rag_document_id:
                continue
            try:
                resp = requests.delete(
                    f"{backend_url}/documents/{doc.rag_document_id}",
                    params={'user_id': user_id},
                    timeout=30,
                )
                # 404 = already gone; treat as success.
                if resp.status_code not in (200, 404):
                    detail = self._extract_detail(resp)
                    raise UserError(
                        _('Backend refused to delete "%s" (%s): %s')
                        % (doc.name, resp.status_code, detail)
                    )
            except UserError:
                raise
            except Exception as exc:  # noqa: BLE001
                _logger.warning(
                    "custom_chatbot_admin: backend delete failed for %s (%s)", doc.name, exc
                )
                raise UserError(
                    _('Could not reach the chatbot backend to delete "%s".\n\n%s')
                    % (doc.name, exc)
                )

    def unlink(self):
        """Remove backend copies before deleting the Odoo records."""
        self._delete_backend_records()
        return super().unlink()

    @staticmethod
    def _extract_detail(resp):
        try:
            data = resp.json()
            return data.get('detail') or data.get('message') or resp.text
        except Exception:  # noqa: BLE001
            return resp.text
