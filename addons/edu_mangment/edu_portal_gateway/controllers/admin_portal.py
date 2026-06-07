# -*- coding: utf-8 -*-
"""
Admin Portal Controller

Implements administrator-facing portal features:
- User management dashboard (US 02.03)
- System rules configuration (US 01.10)
- Registration time-slot management (US 04.05)
- Audit and reporting

Access restricted to users with ERP admin group membership.
"""

import logging
from datetime import datetime, timedelta
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from werkzeug.exceptions import Forbidden, NotFound

from .auth import EduPortalAccessMixin

_logger = logging.getLogger(__name__)


class AdminPortalController(http.Controller, EduPortalAccessMixin):
    """
    Controller for administrator portal views.
    
    Provides high-level system management interfaces including:
    - User role management
    - System configuration
    - Registration windows
    - Analytics and reporting
    """
    
    ADMIN_GROUP = 'edu_mang_auth.group_erp_admin'
    ITEMS_PER_PAGE = 25
    
    # =========================================================================
    # Dashboard
    # =========================================================================
    
    @http.route('/edu-portal/admin/dashboard', type='http', auth='user', website=True)
    def admin_dashboard(self, **kw):
        """
        Admin dashboard with system overview and quick actions.
        """
        user = self._require_group(self.ADMIN_GROUP)
        if not user:
            return self._get_login_redirect('session_expired')
        
        Users = request.env['res.users'].sudo()
        
        # User statistics
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        admin_group = request.env.ref('edu_mang_auth.group_erp_admin')
        
        user_stats = {
            'total': Users.search_count([('active', '=', True)]),
            'students': Users.search_count([('group_ids', 'in', [student_group.id]), ('active', '=', True)]),
            'officers': Users.search_count([('group_ids', 'in', [officer_group.id]), ('active', '=', True)]),
            'admins': Users.search_count([('group_ids', 'in', [admin_group.id]), ('active', '=', True)]),
            'on_hold': Users.search_count([('is_on_hold', '=', True)]) if hasattr(Users, 'is_on_hold') else 0,
        }
        
        # Admission statistics
        Admission = request.env['school.admission'].sudo()
        admission_stats = {
            'total': Admission.search_count([]),
            'pending': Admission.search_count([('state', 'in', ['submitted', 'under_review'])]),
            'accepted': Admission.search_count([('state', '=', 'accepted')]),
            'rejected': Admission.search_count([('state', '=', 'rejected')]),
        }
        
        # Registration statistics
        Registration = request.env['education.registration'].sudo()
        Course = request.env['education.course'].sudo()
        
        registration_stats = {
            'total_enrolled': Registration.search_count([('state', '=', 'enrolled')]),
            'total_courses': Course.search_count([('active', '=', True)]),
            'open_registration': Course.search_count([('registration_open', '=', True)]),
        }
        
        # Petition statistics
        Petition = request.env['student.petition'].sudo()
        petition_stats = {
            'pending': Petition.search_count([('state', 'in', ['submitted', 'under_review'])]),
            'total': Petition.search_count([]),
        }
        
        values = {
            'page_name': 'Admin Dashboard',
            'user': user,
            'user_stats': user_stats,
            'admission_stats': admission_stats,
            'registration_stats': registration_stats,
            'petition_stats': petition_stats,
            'backend_url': '/web',
        }
        
        return request.render('edu_portal_gateway.admin_dashboard', values)
    
    # =========================================================================
    # User Management (US 02.03)
    # =========================================================================
    
    @http.route('/edu-portal/admin/users', type='http', auth='user', website=True)
    def admin_users_list(self, page=1, role=None, search=None, status=None, **kw):
        """
        User management interface with filtering.
        """
        user = self._require_group(self.ADMIN_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Users = request.env['res.users'].sudo()
        
        # Build domain
        domain = []
        
        if status == 'active':
            domain.append(('active', '=', True))
        elif status == 'inactive':
            domain.append(('active', '=', False))
        
        if role:
            if role == 'student':
                group = request.env.ref('edu_mang_auth.group_erp_student')
            elif role == 'officer':
                group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
            elif role == 'admin':
                group = request.env.ref('edu_mang_auth.group_erp_admin')
            else:
                group = None
            
            if group:
                domain.append(('group_ids', 'in', [group.id]))
        
        if search:
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', search))
            domain.append(('login', 'ilike', search))
            domain.append(('email', 'ilike', search))
        
        # Pagination
        page = int(page) or 1
        total = Users.search_count(domain)
        offset = (page - 1) * self.ITEMS_PER_PAGE
        
        users = Users.search(
            domain,
            limit=self.ITEMS_PER_PAGE,
            offset=offset,
            order='name'
        )
        
        # Role counts for filters
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        admin_group = request.env.ref('edu_mang_auth.group_erp_admin')
        
        role_counts = {
            'all': Users.search_count([]),
            'student': Users.search_count([('group_ids', 'in', [student_group.id])]),
            'officer': Users.search_count([('group_ids', 'in', [officer_group.id])]),
            'admin': Users.search_count([('group_ids', 'in', [admin_group.id])]),
        }
        
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        # Get groups for role assignment
        available_groups = [
            {'id': student_group.id, 'name': 'Student', 'xml_id': 'edu_mang_auth.group_erp_student'},
            {'id': officer_group.id, 'name': 'Admission Officer', 'xml_id': 'edu_mang_auth.group_erp_admission_officer'},
            {'id': admin_group.id, 'name': 'Administrator', 'xml_id': 'edu_mang_auth.group_erp_admin'},
        ]
        
        values = {
            'page_name': 'User Management',
            'user': user,
            'users': users,
            'available_groups': available_groups,
            'role_counts': role_counts,
            'current_role': role or 'all',
            'current_status': status or 'all',
            'search': search or '',
            'page': page,
            'total_pages': total_pages,
            'total': total,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.admin_users_list', values)
    
    @http.route('/edu-portal/admin/users/<int:user_id>', type='http', auth='user', website=True)
    def admin_user_detail(self, user_id, **kw):
        """
        View and edit user details.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        Users = request.env['res.users'].sudo()
        target_user = Users.browse(user_id)
        
        if not target_user.exists():
            raise NotFound('User not found.')
        
        # Get available groups
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        admin_group = request.env.ref('edu_mang_auth.group_erp_admin')
        
        available_groups = [
            {'id': student_group.id, 'name': 'Student', 'selected': student_group in target_user.group_ids},
            {'id': officer_group.id, 'name': 'Admission Officer', 'selected': officer_group in target_user.group_ids},
            {'id': admin_group.id, 'name': 'Administrator', 'selected': admin_group in target_user.group_ids},
        ]
        
        values = {
            'page_name': f'User: {target_user.name}',
            'user': admin,
            'target_user': target_user,
            'available_groups': available_groups,
            'is_on_hold': getattr(target_user, 'is_on_hold', False),
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.admin_user_detail', values)
    
    @http.route('/edu-portal/admin/users/<int:user_id>/update', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def admin_user_update(self, user_id, **kw):
        """
        Update user details and role assignments.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        Users = request.env['res.users'].sudo()
        target_user = Users.browse(user_id)
        
        if not target_user.exists():
            return request.redirect('/edu-portal/admin/users?error=User not found')
        
        try:
            # Update basic info
            vals = {}
            
            if kw.get('name'):
                vals['name'] = kw.get('name').strip()
            
            if kw.get('email'):
                vals['email'] = kw.get('email').strip()
            
            if 'active' in kw:
                vals['active'] = kw.get('active') == 'on'
            
            if 'is_on_hold' in kw:
                vals['is_on_hold'] = kw.get('is_on_hold') == 'on'
            
            # Update group memberships
            group_ids = request.httprequest.form.getlist('group_ids')
            if group_ids:
                # Convert to integers and set groups
                group_ids = [int(g) for g in group_ids if g.isdigit()]
                
                # Get ERP-specific groups to manage
                student_group = request.env.ref('edu_mang_auth.group_erp_student')
                officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
                admin_group = request.env.ref('edu_mang_auth.group_erp_admin')
                erp_groups = [student_group.id, officer_group.id, admin_group.id]
                
                # Remove current ERP groups and add selected ones
                current_groups = set(target_user.group_ids.ids)
                current_groups -= set(erp_groups)  # Remove ERP groups
                current_groups |= set(g for g in group_ids if g in erp_groups)  # Add selected
                
                vals['group_ids'] = [(6, 0, list(current_groups))]
            
            if vals:
                target_user.write(vals)
                _logger.info(
                    'User updated: %s by admin %s',
                    target_user.login, admin.login
                )
            
            return request.redirect(f'/edu-portal/admin/users/{user_id}?success=User updated successfully')
            
        except Exception as e:
            _logger.error('User update failed: %s', str(e))
            return request.redirect(f'/edu-portal/admin/users/{user_id}?error={str(e)}')
    
    @http.route('/edu-portal/admin/users/create', type='http', auth='user', website=True)
    def admin_user_create_form(self, **kw):
        """
        Display new user creation form.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        # Get available groups
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        admin_group = request.env.ref('edu_mang_auth.group_erp_admin')
        
        available_groups = [
            {'id': student_group.id, 'name': 'Student'},
            {'id': officer_group.id, 'name': 'Admission Officer'},
            {'id': admin_group.id, 'name': 'Administrator'},
        ]
        
        values = {
            'page_name': 'Create User',
            'user': admin,
            'available_groups': available_groups,
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.admin_user_create', values)
    
    @http.route('/edu-portal/admin/users/create/submit', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def admin_user_create_submit(self, **kw):
        """
        Create a new user.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        try:
            Users = request.env['res.users'].sudo()
            
            name = kw.get('name', '').strip()
            login = kw.get('login', '').strip()
            email = kw.get('email', '').strip()
            
            if not name or not login:
                raise ValidationError('Name and login are required.')
            
            # Check if login exists
            if Users.search([('login', '=', login)], limit=1):
                raise ValidationError('Login already exists.')
            
            # Get selected groups
            group_ids = request.httprequest.form.getlist('group_ids')
            group_ids = [int(g) for g in group_ids if g.isdigit()]
            
            # Create user
            new_user = Users.with_context(no_reset_password=True).create({
                'name': name,
                'login': login,
                'email': email or login,
                'group_ids': [(6, 0, group_ids)] if group_ids else [],
            })
            
            _logger.info(
                'User created: %s by admin %s',
                new_user.login, admin.login
            )
            
            return request.redirect(f'/edu-portal/admin/users/{new_user.id}?success=User created successfully')
            
        except ValidationError as e:
            return request.redirect(f'/edu-portal/admin/users/create?error={str(e)}')
        except Exception as e:
            _logger.error('User creation failed: %s', str(e))
            return request.redirect(f'/edu-portal/admin/users/create?error=Failed to create user')
    
    # =========================================================================
    # System Configuration (US 01.10)
    # =========================================================================
    
    @http.route('/edu-portal/admin/settings', type='http', auth='user', website=True)
    def admin_settings(self, **kw):
        """
        System configuration interface.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        ICP = request.env['ir.config_parameter'].sudo()
        
        # Load current settings
        settings = {
            'mailbox_domain': ICP.get_param('edu_mang_admission.mailbox_domain', 'school.edu'),
            'mailbox_provider': ICP.get_param('edu_mang_admission.mailbox_provider', 'none'),
            'api_base_url': ICP.get_param('edu_mang_admission.api_base_url', ''),
            'min_gpa_requirement': ICP.get_param('edu_portal.min_gpa_requirement', '3.0'),
            'max_credits_per_semester': ICP.get_param('edu_portal.max_credits_per_semester', '18'),
            'add_drop_period_days': ICP.get_param('edu_portal.add_drop_period_days', '14'),
        }
        
        values = {
            'page_name': 'System Settings',
            'user': admin,
            'settings': settings,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.admin_settings', values)
    
    @http.route('/edu-portal/admin/settings/save', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def admin_settings_save(self, **kw):
        """
        Save system configuration.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        try:
            ICP = request.env['ir.config_parameter'].sudo()
            
            # Save settings
            if 'mailbox_domain' in kw:
                ICP.set_param('edu_mang_admission.mailbox_domain', kw.get('mailbox_domain'))
            
            if 'mailbox_provider' in kw:
                ICP.set_param('edu_mang_admission.mailbox_provider', kw.get('mailbox_provider'))
            
            if 'api_base_url' in kw:
                ICP.set_param('edu_mang_admission.api_base_url', kw.get('api_base_url'))
            
            if 'min_gpa_requirement' in kw:
                ICP.set_param('edu_portal.min_gpa_requirement', kw.get('min_gpa_requirement'))
            
            if 'max_credits_per_semester' in kw:
                ICP.set_param('edu_portal.max_credits_per_semester', kw.get('max_credits_per_semester'))
            
            if 'add_drop_period_days' in kw:
                ICP.set_param('edu_portal.add_drop_period_days', kw.get('add_drop_period_days'))
            
            _logger.info('System settings updated by admin %s', admin.login)
            
            return request.redirect('/edu-portal/admin/settings?success=Settings saved successfully')
            
        except Exception as e:
            _logger.error('Settings save failed: %s', str(e))
            return request.redirect(f'/edu-portal/admin/settings?error={str(e)}')
    
    # =========================================================================
    # Registration Windows (US 04.05)
    # =========================================================================
    
    @http.route('/edu-portal/admin/registration-windows', type='http', auth='user', website=True)
    def admin_registration_windows(self, **kw):
        """
        Manage priority-based registration time windows.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        # Check if RegistrationWindow model exists, otherwise use course-level settings
        try:
            Window = request.env['education.registration.window'].sudo()
            windows = Window.search([], order='start_datetime')
            model_exists = True
        except KeyError:
            windows = []
            model_exists = False
        
        # Get courses with registration settings
        Course = request.env['education.course'].sudo()
        courses_with_dates = Course.search([
            ('registration_start', '!=', False)
        ], order='registration_start')
        
        values = {
            'page_name': 'Registration Windows',
            'user': admin,
            'windows': windows,
            'model_exists': model_exists,
            'courses_with_dates': courses_with_dates,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.admin_registration_windows', values)
    
    @http.route('/edu-portal/admin/courses', type='http', auth='user', website=True)
    def admin_courses_list(self, page=1, search=None, semester=None, **kw):
        """
        Course management interface.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        
        # Build domain
        domain = []
        
        if search:
            domain.append('|')
            domain.append(('name', 'ilike', search))
            domain.append(('code', 'ilike', search))
        
        if semester:
            domain.append(('semester', '=', semester))
        
        # Pagination
        page = int(page) or 1
        total = Course.search_count(domain)
        offset = (page - 1) * self.ITEMS_PER_PAGE
        
        courses = Course.search(
            domain,
            limit=self.ITEMS_PER_PAGE,
            offset=offset,
            order='code, name'
        )
        
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        values = {
            'page_name': 'Course Management',
            'user': admin,
            'courses': courses,
            'search': search or '',
            'semester': semester or '',
            'page': page,
            'total_pages': total_pages,
            'total': total,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.admin_courses_list', values)
    
    @http.route('/edu-portal/admin/courses/<int:course_id>/toggle-registration', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def admin_course_toggle_registration(self, course_id, **kw):
        """
        Toggle course registration status.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        course = Course.browse(course_id)
        
        if not course.exists():
            return request.redirect('/edu-portal/admin/courses?error=Course not found')
        
        try:
            if course.registration_open:
                course.action_close_registration()
                message = 'Registration closed'
            else:
                course.action_open_registration()
                message = 'Registration opened'
            
            _logger.info(
                'Course registration toggled: %s by admin %s',
                course.code, admin.login
            )
            
            return request.redirect(f'/edu-portal/admin/courses?success={message} for {course.code}')
            
        except Exception as e:
            return request.redirect(f'/edu-portal/admin/courses?error={str(e)}')
    
    # =========================================================================
    # Reports & Analytics
    # =========================================================================
    
    @http.route('/edu-portal/admin/reports', type='http', auth='user', website=True)
    def admin_reports(self, **kw):
        """
        Admin reports and analytics dashboard.
        """
        admin = self._require_group(self.ADMIN_GROUP)
        if not admin:
            return self._get_login_redirect()
        
        # Generate summary statistics
        Admission = request.env['school.admission'].sudo()
        Registration = request.env['education.registration'].sudo()
        Petition = request.env['student.petition'].sudo()
        
        # Admissions by program
        Program = request.env['school.program'].sudo()
        programs = Program.search([])
        admission_by_program = []
        for prog in programs:
            count = Admission.search_count([('program_id', '=', prog.id)])
            if count > 0:
                admission_by_program.append({
                    'name': prog.name,
                    'count': count,
                })
        
        # Recent activity (last 30 days)
        thirty_days_ago = fields.Datetime.now() - timedelta(days=30)
        recent_stats = {
            'admissions': Admission.search_count([('create_date', '>=', thirty_days_ago)]),
            'registrations': Registration.search_count([('registration_date', '>=', thirty_days_ago)]),
            'petitions': Petition.search_count([('create_date', '>=', thirty_days_ago)]),
        }
        
        values = {
            'page_name': 'Reports & Analytics',
            'user': admin,
            'admission_by_program': admission_by_program,
            'recent_stats': recent_stats,
        }
        
        return request.render('edu_portal_gateway.admin_reports', values)
