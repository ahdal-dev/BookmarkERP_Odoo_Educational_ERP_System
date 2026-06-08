{
    'name': 'Educational ERP Portal Gateway',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Secure portal gateway for Educational ERP',
    'description': """
Educational ERP Portal Gateway
==============================

    """,
    'author': 'Edu management ERP Team',
    'website': '',
    'depends': [
        'base',
        'web',
        'mail',
        'edu_mang_auth',
        'edu_mang_admission',
        'edu_mang_petition',
        'custom_registration',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/menus.xml',
        'views/assets.xml',
        'views/templates/portal_layout.xml',
        'views/templates/login_template.xml',
        'views/templates/student_templates.xml',
        'views/templates/officer_templates.xml',
        'views/templates/admin_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'edu_portal_gateway/static/src/css/portal.css',
            'edu_portal_gateway/static/src/js/portal.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
