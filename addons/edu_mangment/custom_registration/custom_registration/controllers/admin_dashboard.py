# -*- coding: utf-8 -*-
"""
Admin Dashboard Controller for System Management.

Provides web routes for administrators to manage user holds and roles.
"""
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AdminDashboardController(http.Controller):
    """
    Controller for admin system management dashboard.
    
    All routes require the group_erp_admin role.
    """

    def _check_admin_access(self):
        """Verify the user has admin access rights."""
        if not request.env.user.has_group('edu_mang_auth.group_erp_admin'):
            raise AccessError(_('Access denied. Administrator role required.'))
        return True

    @http.route('/admin/system_management', type='http', auth='user', website=True)
    def admin_dashboard(self, search_query=None, filter_type=None, **kwargs):
        """
        Main admin system management dashboard.
        
        Displays user management tools including hold status and role management.
        """
        self._check_admin_access()
        
        Users = request.env['res.users'].sudo()
        
        # Get users based on filter
        domain = [('active', '=', True)]
        
        if search_query:
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', search_query))
            domain.append(('login', 'ilike', search_query))
            domain.append(('email', 'ilike', search_query))
        
        if filter_type == 'on_hold':
            domain.append(('is_on_hold', '=', True))
        elif filter_type == 'students':
            student_group = request.env.ref('edu_mang_auth.group_erp_student')
            domain.append(('groups_id', 'in', [student_group.id]))
        elif filter_type == 'officers':
            officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
            domain.append(('groups_id', 'in', [officer_group.id]))
        
        users = Users.search(domain, limit=100, order='name')
        
        # Get statistics
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        
        stats = {
            'total_students': Users.search_count([('groups_id', 'in', [student_group.id])]),
            'total_officers': Users.search_count([('groups_id', 'in', [officer_group.id])]),
            'students_on_hold': Users.search_count([
                ('groups_id', 'in', [student_group.id]),
                ('is_on_hold', '=', True)
            ]),
        }
        
        values = {
            'users': users,
            'search_query': search_query or '',
            'filter_type': filter_type or 'all',
            'stats': stats,
            'student_group': student_group,
            'officer_group': officer_group,
            'page_title': 'System Management',
        }
        
        return request.render('custom_registration.admin_dashboard_template', values)

    # ==================== Hold Status Management ====================

    @http.route('/admin/user/<int:user_id>/toggle_hold', type='http', auth='user', website=True, methods=['POST'])
    def toggle_user_hold(self, user_id, reason=None, **kwargs):
        """Toggle the hold status for a user."""
        self._check_admin_access()
        
        try:
            Users = request.env['res.users'].sudo()
            user = Users.browse(user_id)
            
            if not user.exists():
                return request.redirect('/admin/system_management?error=user_not_found')
            
            if user.is_on_hold:
                user.action_remove_hold()
                message = 'hold_removed'
            else:
                user.action_place_hold(reason=reason)
                message = 'hold_placed'
            
            _logger.info(
                'Admin %s toggled hold for user %s (now: %s)',
                request.env.user.name, user.name, 'on hold' if user.is_on_hold else 'not on hold'
            )
            
            return request.redirect(f'/admin/system_management?message={message}')
            
        except Exception as e:
            _logger.error('Error toggling user hold: %s', str(e))
            return request.redirect('/admin/system_management?error=' + str(e))

    @http.route('/admin/user/<int:user_id>/place_hold', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def place_user_hold(self, user_id, **kwargs):
        """Place a hold on a user with a reason."""
        self._check_admin_access()
        
        Users = request.env['res.users'].sudo()
        user = Users.browse(user_id)
        
        if not user.exists():
            return request.redirect('/admin/system_management?error=user_not_found')
        
        if request.httprequest.method == 'POST':
            reason = kwargs.get('reason', '')
            user.action_place_hold(reason=reason)
            
            _logger.info(
                'Admin %s placed hold on user %s with reason: %s',
                request.env.user.name, user.name, reason
            )
            
            return request.redirect('/admin/system_management?message=hold_placed')
        
        # GET request - show form
        return request.render('custom_registration.admin_hold_form_template', {
            'user': user,
            'page_title': f'Place Hold - {user.name}',
        })

    @http.route('/admin/user/<int:user_id>/remove_hold', type='http', auth='user', website=True, methods=['POST'])
    def remove_user_hold(self, user_id, **kwargs):
        """Remove hold from a user."""
        self._check_admin_access()
        
        try:
            Users = request.env['res.users'].sudo()
            user = Users.browse(user_id)
            
            if not user.exists():
                return request.redirect('/admin/system_management?error=user_not_found')
            
            user.action_remove_hold()
            
            _logger.info('Admin %s removed hold from user %s', request.env.user.name, user.name)
            
            return request.redirect('/admin/system_management?message=hold_removed')
            
        except Exception as e:
            _logger.error('Error removing user hold: %s', str(e))
            return request.redirect('/admin/system_management?error=' + str(e))

    # ==================== Role Management ====================

    @http.route('/admin/user/<int:user_id>/revoke_officer', type='http', auth='user', website=True, methods=['POST'])
    def revoke_officer_role(self, user_id, **kwargs):
        """Revoke the admission officer role from a user."""
        self._check_admin_access()
        
        try:
            Users = request.env['res.users'].sudo()
            user = Users.browse(user_id)
            
            if not user.exists():
                return request.redirect('/admin/system_management?error=user_not_found')
            
            officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
            
            if officer_group not in user.groups_id:
                return request.redirect('/admin/system_management?error=user_not_officer')
            
            # Remove the officer group
            user.write({
                'groups_id': [(3, officer_group.id)]
            })
            
            _logger.info(
                'Admin %s revoked officer role from user %s',
                request.env.user.name, user.name
            )
            
            return request.redirect('/admin/system_management?message=officer_role_revoked')
            
        except Exception as e:
            _logger.error('Error revoking officer role: %s', str(e))
            return request.redirect('/admin/system_management?error=' + str(e))

    @http.route('/admin/user/<int:user_id>/grant_officer', type='http', auth='user', website=True, methods=['POST'])
    def grant_officer_role(self, user_id, **kwargs):
        """Grant the admission officer role to a user."""
        self._check_admin_access()
        
        try:
            Users = request.env['res.users'].sudo()
            user = Users.browse(user_id)
            
            if not user.exists():
                return request.redirect('/admin/system_management?error=user_not_found')
            
            officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
            
            if officer_group in user.groups_id:
                return request.redirect('/admin/system_management?error=already_officer')
            
            # Add the officer group
            user.write({
                'groups_id': [(4, officer_group.id)]
            })
            
            _logger.info(
                'Admin %s granted officer role to user %s',
                request.env.user.name, user.name
            )
            
            return request.redirect('/admin/system_management?message=officer_role_granted')
            
        except Exception as e:
            _logger.error('Error granting officer role: %s', str(e))
            return request.redirect('/admin/system_management?error=' + str(e))

    @http.route('/admin/user/<int:user_id>/details', type='http', auth='user', website=True)
    def user_details(self, user_id, **kwargs):
        """View detailed user information."""
        self._check_admin_access()
        
        Users = request.env['res.users'].sudo()
        user = Users.browse(user_id)
        
        if not user.exists():
            return request.redirect('/admin/system_management?error=user_not_found')
        
        # Get user's groups
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        admin_group = request.env.ref('edu_mang_auth.group_erp_admin')
        
        # Get user's registrations
        Registration = request.env['education.registration'].sudo()
        registrations = Registration.search([('student_id', '=', user_id)])
        
        values = {
            'target_user': user,
            'is_student': student_group in user.groups_id,
            'is_officer': officer_group in user.groups_id,
            'is_admin': admin_group in user.groups_id,
            'registrations': registrations,
            'page_title': f'User Details - {user.name}',
        }
        
        return request.render('custom_registration.admin_user_details_template', values)

    # ==================== API Endpoints ====================

    @http.route('/admin/api/users/search', type='jsonrpc', auth='user')
    def api_search_users(self, query, filter_type=None, **kwargs):
        """API endpoint to search users."""
        self._check_admin_access()
        
        Users = request.env['res.users'].sudo()
        
        domain = [
            ('active', '=', True),
            '|', '|',
            ('name', 'ilike', query),
            ('login', 'ilike', query),
            ('email', 'ilike', query)
        ]
        
        if filter_type == 'on_hold':
            domain.append(('is_on_hold', '=', True))
        
        users = Users.search(domain, limit=50)
        
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        
        return [{
            'id': u.id,
            'name': u.name,
            'email': u.email or u.login,
            'is_on_hold': u.is_on_hold,
            'is_student': student_group in u.groups_id,
            'is_officer': officer_group in u.groups_id,
        } for u in users]

    @http.route('/admin/api/stats', type='jsonrpc', auth='user')
    def api_get_stats(self, **kwargs):
        """API endpoint to get system statistics."""
        self._check_admin_access()
        
        Users = request.env['res.users'].sudo()
        Registration = request.env['education.registration'].sudo()
        Course = request.env['education.course'].sudo()
        
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        officer_group = request.env.ref('edu_mang_auth.group_erp_admission_officer')
        
        return {
            'total_students': Users.search_count([('groups_id', 'in', [student_group.id])]),
            'total_officers': Users.search_count([('groups_id', 'in', [officer_group.id])]),
            'students_on_hold': Users.search_count([
                ('groups_id', 'in', [student_group.id]),
                ('is_on_hold', '=', True)
            ]),
            'total_courses': Course.search_count([('active', '=', True)]),
            'total_registrations': Registration.search_count([('state', '=', 'enrolled')]),
        }
