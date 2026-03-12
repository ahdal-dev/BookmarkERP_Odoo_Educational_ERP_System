{
    'name': 'Student Petition System',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Manage student petitions for overloads and special requests',
    'description': """
        Student Petition Management System
        ==================================
        This module allows students to submit petitions for various requests
        such as course overload, special accommodations, etc. Administrators
        can manage petition types and approve/reject submissions.
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
    'security/petition_security.xml',
    'security/ir.model.access.csv',
    'views/petition_type_views.xml',
    'views/petition_views.xml',
    'views/menus.xml',
],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}