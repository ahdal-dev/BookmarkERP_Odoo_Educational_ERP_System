import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Connection to the FastAPI chatbot backend
    chatbot_backend_url = fields.Char(
        string='Chatbot Backend URL',
        config_parameter='custom_chatbot_admin.backend_url',
        help='Base URL of the FastAPI chatbot service, e.g. http://localhost:8000',
    )
    chatbot_admin_token = fields.Char(
        string='Backend Admin Token',
        config_parameter='custom_chatbot_admin.admin_token',
        help='Shared secret sent to the backend /admin/config endpoint to '
             'authorize configuration pushes (matches CHATBOT_ADMIN_TOKEN).',
    )

    # Target tenant in the RAG backend (its own Postgres UUIDs, not Odoo ids)
    chatbot_rag_org_id = fields.Char(
        string='RAG Organization ID',
        config_parameter='custom_chatbot_admin.rag_org_id',
        help='UUID of the organization in the RAG backend that synced documents '
             'are pushed to.',
    )
    chatbot_rag_user_id = fields.Char(
        string='RAG Service User ID',
        config_parameter='custom_chatbot_admin.rag_user_id',
        help='UUID of an admin user in the RAG backend used to authorize uploads '
             'and deletions.',
    )

    # LLM + RAG tuning (mirrors the backend environment variables)
    chatbot_llm_api_key = fields.Char(
        string='LLM API Key',
        config_parameter='custom_chatbot_admin.llm_api_key',
        help='LLM provider API key (maps to GEMINI_API_KEY on the backend).',
    )
    chatbot_llm_model = fields.Char(
        string='LLM Model',
        config_parameter='custom_chatbot_admin.llm_model',
        help='LLM model name (maps to GEMINI_MODEL on the backend).',
    )
    chatbot_rag_top_k = fields.Integer(
        string='RAG Top K',
        config_parameter='custom_chatbot_admin.rag_top_k',
        help='Number of chunks retrieved by the pgvector similarity search '
             '(maps to RAG_TOP_K).',
    )
    chatbot_rag_llm_snippets = fields.Integer(
        string='RAG LLM Snippets',
        config_parameter='custom_chatbot_admin.rag_llm_snippets',
        help='Number of top retrieved chunks passed to the LLM as context '
             '(maps to RAG_LLM_SNIPPETS).',
    )
    chatbot_system_prompt = fields.Char(
        string='System Prompt Override',
        config_parameter='custom_chatbot_admin.system_prompt',
        help='Optional override for the agent system prompt. Leave empty to keep '
             'the backend default.',
    )

    def action_push_config_to_backend(self):
        """Push the current chatbot configuration to the FastAPI backend.

        Sends the LLM/RAG settings to the backend /admin/config endpoint so they
        take effect on the running service without a restart.
        """
        self.ensure_one()
        # Persist any unsaved changes first so we read consistent param values.
        self.set_values()

        params = self.env['ir.config_parameter'].sudo()
        backend_url = (params.get_param('custom_chatbot_admin.backend_url') or '').rstrip('/')
        token = params.get_param('custom_chatbot_admin.admin_token') or ''
        if not backend_url:
            raise UserError(_('Please set the Chatbot Backend URL before pushing configuration.'))

        payload = {
            'token': token,
            'llm_api_key': params.get_param('custom_chatbot_admin.llm_api_key') or '',
            'llm_model': params.get_param('custom_chatbot_admin.llm_model') or '',
            'rag_top_k': int(params.get_param('custom_chatbot_admin.rag_top_k') or 0),
            'rag_llm_snippets': int(params.get_param('custom_chatbot_admin.rag_llm_snippets') or 0),
            'system_prompt': params.get_param('custom_chatbot_admin.system_prompt') or '',
        }

        try:
            import requests
            resp = requests.post(f"{backend_url}/admin/config", json=payload, timeout=10)
        except Exception as exc:  # noqa: BLE001 - surface a clean message to the user
            _logger.warning("custom_chatbot_admin: config push failed (%s)", exc)
            raise UserError(
                _('Could not reach the chatbot backend at %s.\n\n%s') % (backend_url, exc)
            )

        if resp.status_code == 401:
            raise UserError(_('Backend rejected the admin token (401). Check the Backend Admin Token.'))
        if resp.status_code != 200:
            detail = self._extract_detail(resp)
            raise UserError(_('Backend returned an error (%s): %s') % (resp.status_code, detail))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Configuration pushed'),
                'message': _('The chatbot backend configuration was updated successfully.'),
                'type': 'success',
                'sticky': False,
            },
        }

    @staticmethod
    def _extract_detail(resp):
        """Return a clean error message from a backend HTTP response."""
        try:
            data = resp.json()
            return data.get('detail') or data.get('message') or resp.text
        except Exception:  # noqa: BLE001
            return resp.text
