{
    'name': 'Education Management System',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'license': 'LGPL-3',
    'summary': 'Manage educational institutions, students, and courses',
    'description': """
        A comprehensive education management system for Odoo that allows you to:
        - Manage students, teachers, and courses
        - Track enrollments and grades
        - Handle academic sessions and semesters
        - Generate reports and analytics
    """,
    'author': 'Your Name',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/student_views.xml',
        'views/student_admission_views.xml',
        'views/teacher_views.xml',
        'views/course_views.xml',
        'views/enrollment_views.xml',
        'views/education_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'education_management/static/src/js/student_ocr_widget.js',
            'education_management/static/src/js/student_admission_form.js',
            'education_management/static/src/xml/student_ocr_templates.xml',
        ],
    },
    'demo': [
        'demo/education_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
