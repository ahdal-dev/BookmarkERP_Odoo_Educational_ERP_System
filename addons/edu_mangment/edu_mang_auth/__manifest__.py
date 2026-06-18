{
    'name': 'Educational ERP Authentication & Authorization',
    'version': '1.1.0',
    'category': 'Education',
    'summary': 'Pure authentication with role-based access control for Educational ERP',
    'description': """
Educational ERP Authentication & Authorization Module
======================================================

This module provides PURE authentication without website dependencies:
- Custom user groups: ERP Admin, Student, Admission Officer
- Role-based routing logic (determines redirect URLs)
- Security rules and access control
- JSON API endpoints for authentication

This is the core authentication module. The student-facing portal UI
is provided by the React frontend (bookmark-frontend).

Key Features:
- User groups with role-based permissions
- Record rules for data access control
- Session check API endpoint
- Role detection and redirect URL determination
    """,
    'author': 'Educational ERP Team',
    'website': 'https://www.TEAM.com',
    'depends': ['base', 'web', 'portal', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/auth_views.xml',
        'data/demo_users.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
