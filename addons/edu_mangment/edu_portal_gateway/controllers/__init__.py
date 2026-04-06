# -*- coding: utf-8 -*-
"""
Portal Gateway Controllers

This package contains all HTTP controllers for the edu_portal_gateway module:
- auth: Authentication and session management
- student_portal: Student dashboard, petitions, registration
- officer_portal: Admission officer and professor views
- admin_portal: Administrator dashboard and configuration
"""

from . import auth
from . import student_portal
from . import officer_portal
from . import admin_portal
