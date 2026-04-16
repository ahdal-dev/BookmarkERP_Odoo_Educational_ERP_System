{
    'name': 'Custom Registration Management',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Course Registration Management for Educational ERP',
    'description': """
Registration Management Module for Educational ERP System
==========================================================

This module provides:
- Course catalog management
- Student wishlist/cart functionality  
- Real-time seat validation for registrations
- Role-based dashboards (Student, Officer, Admin)
- Add/Drop period management
- Student hold status management

Key Features:
- Students can browse courses, add to wishlist, and register
- Officers can manage courses and override student registrations
- Admins can manage user holds and officer roles
    """,
    'author': 'Educational ERP Team',
    'website': 'https://www.TEAM.com',
    'depends': ['base', 'web', 'website', 'edu_mang_auth'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/student_templates.xml',
        'views/officer_templates.xml',
        'views/admin_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_registration/static/src/css/registration.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
