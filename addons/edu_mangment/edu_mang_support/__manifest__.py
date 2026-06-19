{
    'name': 'Education Support Tickets',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Support tickets and live-chat threads for the help desk',
    'description': """
        Support Tickets
        ===============
        A simple support.ticket model (with a mail.thread conversation) backing
        the support technician's live queue, chat sessions, and ticket list in
        the decoupled React frontend.
    """,
    'author': 'Bookmark Academic ERP',
    'depends': ['base', 'mail', 'edu_mang_auth'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
