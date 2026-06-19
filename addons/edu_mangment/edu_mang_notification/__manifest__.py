{
    'name': 'Education In-App Notifications',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'First-class in-app notifications for the decoupled ERP frontend',
    'description': """
        In-App Notifications
        =====================
        Adds an ``edu.notification`` model that powers the centralized
        Notifications hub in the React frontend. Workflow hooks create
        notifications when petitions, registrations, and admissions change
        state. Exposed to the frontend via the FastAPI gateway.
    """,
    'author': 'Bookmark Academic ERP',
    'depends': [
        'base',
        'edu_mang_petition',
        'custom_registration',
        'edu_mang_admission',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/notification_security.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
