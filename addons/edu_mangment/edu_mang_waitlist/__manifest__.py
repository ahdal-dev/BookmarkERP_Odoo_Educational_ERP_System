{
    'name': 'Education Waitlist Auto-Promotion',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Automatically enroll waitlisted students when a seat frees up',
    'description': """
        Waitlist Auto-Promotion
        =======================
        When an enrolled student drops a course, the oldest (FIFO) waitlisted
        student is automatically promoted into the freed seat and notified.
        A scheduled job sweeps for any missed promotions.
    """,
    'author': 'Bookmark Academic ERP',
    'depends': ['base', 'custom_registration', 'edu_mang_notification'],
    'data': [
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
