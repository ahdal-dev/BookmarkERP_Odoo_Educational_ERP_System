from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
from werkzeug.exceptions import Forbidden
import logging

_logger = logging.getLogger(__name__)


class DashboardController(http.Controller):
    """
    Controller for role-based dashboard routing with access control.
    """

    def _check_access(self, required_group):
        """
        Verify that the current user belongs to the required group.

        Args:
            required_group: The XML ID of the required group (e.g., 'edu_mang_auth.group_erp_student')

        Returns:
            The user record if authorized

        Raises:
            AccessDenied: If user is not logged in
            Forbidden: If user doesn't have the required group
        """
        if not request.session.uid:
            _logger.warning("Unauthorized access attempt - No session")
            raise AccessDenied("Please log in to access this page.")

        user = request.env['res.users'].sudo().browse(request.session.uid)

        if not user.exists():
            _logger.warning(f"Invalid user session: {request.session.uid}")
            raise AccessDenied("Invalid session. Please log in again.")

        if not user.has_group(required_group):
            _logger.warning(
                f"Access denied for user {user.login} to group {required_group}"
            )
            raise Forbidden(
                description="You do not have permission to access this page."
            )

        return user

    def _get_access_denied_response(self, message="Access Denied"):
        """
        Return a standardized access denied response.
        """
        return request.render('edu_mang_auth.access_denied_page', {
            'error_message': message,
        })


    @http.route('/student/dashboard', type='http', auth='user', website=True)
    def student_dashboard(self, **kw):
        """
        Student Dashboard - Main portal for students.

        Access restricted to users with group_erp_student.
        Displays quick links to petitions, course registration, etc.
        """
        try:
            user = self._check_access('edu_mang_auth.group_erp_student')
        except Forbidden:
            return self._get_access_denied_response(
                "You must be a registered student to access this dashboard."
            )
        except AccessDenied:
            return request.redirect('/edu/login?error=session_expired')

        # Prepare dashboard data
        values = {
            'user': user,
            'page_name': 'Student Dashboard',
            'student_name': user.partner_id.name or user.name,
            'student_email': user.partner_id.email or user.login,
            # Placeholder for future integration
            'pending_petitions': 0,
            'registered_courses': 0,
            'upcoming_exams': 0,
            'announcements': [],
        }

        return request.render('edu_mang_auth.student_dashboard', values)

    @http.route('/student/petitions', type='http', auth='user', website=True)
    def student_petitions(self, **kw):
        """
        Student Petitions Page - Placeholder for future petition system.
        """
        try:
            user = self._check_access('edu_mang_auth.group_erp_student')
        except (Forbidden, AccessDenied):
            return request.redirect('/edu/login')

        values = {
            'user': user,
            'page_name': 'My Petitions',
            'petitions': [],  # Placeholder
        }

        return request.render('edu_mang_auth.student_petitions', values)

    @http.route('/student/registration', type='http', auth='user', website=True)
    def student_registration(self, **kw):
        """
        Course Registration Page - Placeholder for future registration system.
        """
        try:
            user = self._check_access('edu_mang_auth.group_erp_student')
        except (Forbidden, AccessDenied):
            return request.redirect('/edu/login')

        values = {
            'user': user,
            'page_name': 'Course Registration',
            'available_courses': [],  # Placeholder
            'registered_courses': [],  # Placeholder
        }

        return request.render('edu_mang_auth.student_registration', values)


    @http.route('/admission/dashboard', type='http', auth='user', website=True)
    def admission_dashboard(self, **kw):
        """
        Admission Officer Dashboard - Portal for admission management.

        Access restricted to users with group_erp_admission_officer.
        """
        try:
            user = self._check_access('edu_mang_auth.group_erp_admission_officer')
        except Forbidden:
            return self._get_access_denied_response(
                "You must be an Admission Officer to access this dashboard."
            )
        except AccessDenied:
            return request.redirect('/edu/login?error=session_expired')

        # Get admission statistics (placeholder - integrate with admission module)
        try:
            admission_model = request.env['school.admission'].sudo()
            pending_count = admission_model.search_count([('state', '=', 'submitted')])
            review_count = admission_model.search_count([('state', '=', 'under_review')])
            accepted_count = admission_model.search_count([('state', '=', 'accepted')])
            rejected_count = admission_model.search_count([('state', '=', 'rejected')])
        except Exception:
            # Model might not exist yet
            pending_count = review_count = accepted_count = rejected_count = 0

        values = {
            'user': user,
            'page_name': 'Admission Dashboard',
            'pending_applications': pending_count,
            'under_review': review_count,
            'accepted': accepted_count,
            'rejected': rejected_count,
        }

        return request.render('edu_mang_auth.admission_dashboard', values)

    # =========================================
    # ADMIN DASHBOARD
    # =========================================

    @http.route('/admin/dashboard', type='http', auth='user', website=True)
    def admin_dashboard(self, **kw):
        """
        Admin Dashboard - Central administration portal.

        Access restricted to users with group_erp_admin.
        Provides quick access to system management and statistics.
        """
        try:
            user = self._check_access('edu_mang_auth.group_erp_admin')
        except Forbidden:
            return self._get_access_denied_response(
                "You must be an ERP Administrator to access this dashboard."
            )
        except AccessDenied:
            return request.redirect('/edu/login?error=session_expired')

        # System statistics
        user_model = request.env['res.users'].sudo()

        total_users = user_model.search_count([('active', '=', True)])
        student_count = user_model.search_count([
            ('group_ids', 'in', request.env.ref('edu_mang_auth.group_erp_student').id),
            ('active', '=', True)
        ])
        staff_count = user_model.search_count([
            ('group_ids', 'in', request.env.ref('base.group_user').id),
            ('active', '=', True)
        ])

        values = {
            'user': user,
            'page_name': 'Admin Dashboard',
            'total_users': total_users,
            'total_students': student_count,
            'total_staff': staff_count,
            'backend_url': '/web',
        }

        return request.render('edu_mang_auth.admin_dashboard', values)

    # =========================================
    # ACCESS DENIED PAGE
    # =========================================

    @http.route('/edu/access-denied', type='http', auth='public', website=True)
    def access_denied_page(self, **kw):
        """
        Generic access denied page.
        """
        return request.render('edu_mang_auth.access_denied_page', {
            'error_message': kw.get('message', 'You do not have permission to access this resource.'),
        })
