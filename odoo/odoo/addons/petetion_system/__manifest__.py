{
    'name': 'Petetion System',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Online petition application portal for students and staff',
    'description': 'Petition System Module - Online petition applications with document upload, category selection, and status tracking',
    'author': 'Educational ERP Team',
    'website': 'https://www.TEAM.com',
    'depends': ['base', 'web', 'website', 'theme_web_openeducat'],
    'data': [
        'security/ir.model.access.csv',
        'views/petetion_views.xml',
        'views/website_templates.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'admission_portal/static/src/js/process_ocr.js',
    #     ],
    # },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
