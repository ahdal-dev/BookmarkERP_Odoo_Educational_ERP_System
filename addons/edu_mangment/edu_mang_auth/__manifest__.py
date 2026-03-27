{
    'name': 'Educational ERP Authentication & Authorization',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'Custom authentication with role-based access control for Educational ERP',
    'description': """
Educational ERP Authentication & Authorization Module
======================================================

This module provides:
- Custom user groups: ERP Admin, Student, Admission Officer
- Role-based dashboard routing after login
- Custom login page template
- Secure dashboard access with group verification
- Student-friendly portal interface

Key Features:
- Automatic redirect based on user role after login
- Access control for dashboard routes
- Custom website login experience
- Responsive dashboard templates
    """,
    'author': 'Educational ERP Team',
    'website': 'https://www.TEAM.com',
    'depends': ['base', 'web', 'website', 'portal', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/demo_users.xml',
        'views/login_templates.xml',
        'views/dashboard_templates.xml',
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_frontend': [
            'edu_mang_auth/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
