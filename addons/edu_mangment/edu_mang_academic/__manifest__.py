{
    'name': 'Education Academic Records & Registration Tiers',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Course grades, cumulative GPA / seniority, and registration tiers',
    'description': """
        Academic Records & Registration Tiers
        ======================================
        - Adds a final grade to each course registration and derives grade points.
        - Computes cumulative GPA, earned credits, class year (by credits), and
          academic standing on res.users.
        - Adds an education.registration.tier model (seniority-based windows)
          used by the registrar ruleset.
    """,
    'author': 'Bookmark Academic ERP',
    'depends': ['base', 'custom_registration', 'edu_mang_auth'],
    'data': [
        'security/ir.model.access.csv',
        'data/registration_tier_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
