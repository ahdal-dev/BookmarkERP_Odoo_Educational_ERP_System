import logging

_logger = logging.getLogger(__name__)

# Default configuration applied on install. Keys mirror the FastAPI backend's
# environment variables so the Odoo settings stay aligned with the service.
DEFAULT_PARAMS = {
    'custom_chatbot_admin.backend_url': 'http://localhost:8000',
    'custom_chatbot_admin.llm_model': 'gemini-1.5-flash',
    'custom_chatbot_admin.rag_top_k': '40',
    'custom_chatbot_admin.rag_llm_snippets': '8',
}


def post_init_hook(env):
    """Set up default chatbot configuration and probe the backend connection.

    Runs once after the module is installed. It seeds sensible defaults (only
    for parameters that are not already set) and attempts a best-effort health
    check against the configured backend. A backend that is offline must not
    block the install, so the probe is wrapped in a broad try/except.
    """
    params = env['ir.config_parameter'].sudo()
    for key, value in DEFAULT_PARAMS.items():
        if not params.get_param(key):
            params.set_param(key, value)

    backend_url = (params.get_param('custom_chatbot_admin.backend_url') or '').rstrip('/')
    if not backend_url:
        return

    try:
        import requests
        resp = requests.get(f"{backend_url}/health", timeout=5)
        if resp.status_code == 200:
            _logger.info("custom_chatbot_admin: backend reachable at %s", backend_url)
        else:
            _logger.warning(
                "custom_chatbot_admin: backend /health returned %s", resp.status_code
            )
    except Exception as exc:  # noqa: BLE001 - install must not fail on a down backend
        _logger.warning(
            "custom_chatbot_admin: could not reach backend at %s (%s)", backend_url, exc
        )
