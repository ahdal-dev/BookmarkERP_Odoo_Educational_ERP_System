{
    'name': 'Educational ERP Website Portal',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'Website portal interface for Educational ERP',
    'description': """
Educational ERP Website Portal
==============================

This module provides the website/portal user interface for Educational ERP:
- Custom login page with responsive design
- Role-based dashboard templates (Student, Officer, Admin)
- Dashboard navigation with sidebar layout
- Access denied page templates

This module depends on edu_mang_auth for authentication logic and security groups.
The separation allows edu_mang_auth to be used standalone for API authentication
without requiring the website module.

Key Features:
- Custom styled login page at /edu/login
- Role-based dashboard routing after login
- Responsive sidebar navigation
- Student, Admission Officer, and Admin dashboards
    """,
    'author': 'Educational ERP Team',
    'website': 'https://www.TEAM.com',
    'depends': ['website', 'edu_mang_auth'],
    'data': [
        'views/login_templates.xml',
        'views/dashboard_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'edu_mang_website/static/src/css/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
