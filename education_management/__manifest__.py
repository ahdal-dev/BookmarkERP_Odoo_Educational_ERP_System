{
    'name': 'Education Management System',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Manage educational institutions, students, and courses',
    'description': """
        A comprehensive education management system for Odoo that allows you to:
        - Manage students, teachers, and courses
        - Track enrollments and grades
        - Handle academic sessions and semesters
        - Generate reports and analytics
    """,
    'author': 'Your Name',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/education_menu.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/course_views.xml',
        'views/enrollment_views.xml',
    ],
    'demo': [
        'demo/education_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
