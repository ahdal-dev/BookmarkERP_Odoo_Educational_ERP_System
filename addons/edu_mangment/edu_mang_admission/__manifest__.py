{
    'name': 'Admission Portal',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Online admission application portal for prospective students',
    'description': 'Admission Portal Module - Online admission applications with document upload, program selection, and status tracking',
    'author': 'Educational ERP Team',
    'website': 'https://www.TEAM.com',
    'depends': ['base', 'web', 'website', 'theme_web_openeducat', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/admission_views.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'edu_mang_admission/static/src/js/process_ocr.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
