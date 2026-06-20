{
    'name': 'Education Data Retention & Purge',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Automated retention policies that archive, anonymize, or delete obsolete records',
    'description': """
Data Minimization — Automated Purge of Obsolete Records
========================================================
Defines configurable ``data.retention.policy`` rules (per record type) and a
daily scheduled action that, for each active policy, finds records older than
the retention window and either archives, anonymizes (PII replaced with hashed
placeholders), or deletes them. Every purge run is written to ``audit.log`` with
event type ``data_retention_purge``.
""",
    'author': 'Bookmark Academic ERP',
    'depends': [
        'base',
        'edu_mang_audit',
        'custom_registration',
        'edu_mang_admission',
        'edu_mang_petition',
        'edu_mang_support',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
