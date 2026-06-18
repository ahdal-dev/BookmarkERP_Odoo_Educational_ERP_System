{
    'name': 'Custom Chatbot Admin',
    'version': '19.0.1.0',
    'category': 'Education',
    'summary': 'Manage the RAG + agentic chatbot backend from Odoo',
    'description': """
Custom Chatbot Admin
====================

Management layer for the decoupled RAG + agentic chatbot service
(services/RAG-Chatbot/Backend). This module lets designated administrators:

- Configure the chatbot backend connection, LLM settings, RAG parameters and
  system-prompt override from the Odoo Settings UI, and push them live to the
  FastAPI backend.
- Upload knowledge-base documents (PDF/TXT/DOCX/CSV), sync them to the backend
  ingestion pipeline (chunking + pgvector embedding), and delete outdated ones.

The chatbot's /ask endpoint, RAG pipeline and agent tools live in the FastAPI
service; this module only manages configuration and documents.
    """,
    'author': 'Educational ERP Team',
    'website': 'https://www.TEAM.com',
    'depends': ['base', 'mail', 'edu_mang_auth'],
    'external_dependencies': {'python': ['requests']},
    'data': [
        'security/chatbot_security.xml',
        'security/ir.model.access.csv',
        'views/chatbot_rag_document_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
