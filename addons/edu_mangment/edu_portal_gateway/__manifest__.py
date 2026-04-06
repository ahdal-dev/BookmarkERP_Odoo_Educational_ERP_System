{
    'name': 'Educational ERP Portal Gateway',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Secure portal gateway for Educational ERP',
    'description': """
Educational ERP Portal Gateway
==============================

A dedicated, secure Portal Module that is entirely decoupled from the standard 
Odoo website module to ensure privacy and role-specific access.

Key Features:
-------------
* **Structural Separation**: Secure portal at /edu-portal/ separate from public website
* **Unified Authentication**: Custom login with role-based dashboard routing
* **Student Portal**: Petition management, course registration, academic data
* **Officer/Professor Portal**: Admission pipeline, petition review workflows
* **Admin Dashboard**: User management, system rules, registration time-slots
* **Data Privacy**: Record rules ensuring users only see authorized data

User Stories Implemented:
-------------------------
* US 02.01: Role-specific dashboard access upon login
* US 03.01: Student petition submission
* US 03.02: Petition status tracking
* US 03.06: Automated petition routing
* US 04.05: Priority-based registration time-slots
* US 01.07: Admission officer backend/portal visibility
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
