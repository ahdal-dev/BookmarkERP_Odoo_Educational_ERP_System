{
    'name': 'Education Audit Log',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Persisted security/audit events for the admin audit log',
    'description': """
        Audit Log
        =========
        An audit.log model that persists key security events (login, role and
        configuration changes, data exports) written best-effort by the API
        gateway, surfaced in the admin Audit Log page.
    """,
    'author': 'Bookmark Academic ERP',
    'depends': ['base', 'edu_mang_auth'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
