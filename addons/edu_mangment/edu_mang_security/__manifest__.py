{
    'name': 'Education Strong Authentication',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'TOTP MFA fields, password policy history/expiry, and service-account credential rotation',
    'description': """
Strong Authentication
======================
* Adds MFA fields (``mfa_enabled``, encrypted ``mfa_secret``, hashed
  ``mfa_backup_codes``) and password-policy fields (``password_history``,
  ``password_changed_at``) to ``res.users``.
* Adds a ``service.account`` model with an encrypted ``api_key`` and a daily
  ``ir.cron`` that rotates keys past their rotation interval, logging each
  rotation to ``audit.log`` and notifying admins.
* Provides a symmetric field-encryption helper (Fernet) shared with the FastAPI
  gateway via the ``FIELD_ENCRYPTION_KEY`` env var / ``security.field_encryption_key``
  config parameter.
""",
    'author': 'Bookmark Academic ERP',
    'depends': [
        'base',
        'edu_mang_auth',
        'edu_mang_audit',
        'edu_mang_notification',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
