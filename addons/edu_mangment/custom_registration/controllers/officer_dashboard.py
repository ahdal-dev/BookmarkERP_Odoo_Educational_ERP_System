# -*- coding: utf-8 -*-
"""
Admission Officer Dashboard Controller for Registration Management.

Provides web routes for officers to manage courses and student registrations.
"""
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class OfficerDashboardController(http.Controller):
    """
    Controller for admission officer registration management dashboard.
    
    All routes require the group_erp_admission_officer role.
    """

    def _check_officer_access(self):
        """Verify the user has admission officer access rights."""
        if not request.env.user.has_group('edu_mang_auth.group_erp_admission_officer'):
            raise AccessError(_('Access denied. Admission Officer role required.'))
        return True

    @http.route('/officer/registration_management', type='http', auth='user', website=True)
    def officer_dashboard(self, search_student=None, **kwargs):
        """
        Main admission officer dashboard.
        
        Displays course management and student registration tools.
        """
        self._check_officer_access()
        
        # Get all courses
        Course = request.env['education.course'].sudo()
        courses = Course.search([], order='code')
        
        # Search for students if requested
        students = []
        selected_student = None
        student_registrations = []
        
        if search_student:
            Users = request.env['res.users'].sudo()
            students = Users.search([
                '|', '|',
                ('name', 'ilike', search_student),
                ('login', 'ilike', search_student),
                ('email', 'ilike', search_student)
            ], limit=50)
        
        student_id = kwargs.get('student_id')
        if student_id:
            try:
                student_id = int(student_id)
                selected_student = request.env['res.users'].sudo().browse(student_id)
                if selected_student.exists():
                    Registration = request.env['education.registration'].sudo()
                    student_registrations = Registration.search([
                        ('student_id', '=', student_id)
                    ], order='state, registration_date desc')
            except (ValueError, TypeError):
                pass
        
        values = {
            'courses': courses,
            'students': students,
            'search_student': search_student or '',
            'selected_student': selected_student,
            'student_registrations': student_registrations,
            'page_title': 'Registration Management',
        }
        
        return request.render('custom_registration.officer_dashboard_template', values)

    # ==================== Course Management ====================

    @http.route('/officer/course/create', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def create_course(self, **kwargs):
        """Create a new course."""
        self._check_officer_access()
        
        if request.httprequest.method == 'POST':
            try:
                Course = request.env['education.course'].sudo()
                
                course_data = {
                    'name': kwargs.get('name'),
                    'code': kwargs.get('code'),
                    'description': kwargs.get('description'),
                    'total_seats': int(kwargs.get('total_seats', 30)),
                    'schedule': kwargs.get('schedule'),
                    'instructor': kwargs.get('instructor'),
                    'credits': int(kwargs.get('credits', 3)),
                    'registration_open': kwargs.get('registration_open') == 'on',
                }
                
                if kwargs.get('add_drop_deadline'):
                    course_data['add_drop_deadline'] = kwargs.get('add_drop_deadline')
                
                Course.create(course_data)
                
                return request.redirect('/officer/registration_management?message=course_created')
                
            except Exception as e:
                _logger.error('Error creating course: %s', str(e))
                return request.redirect('/officer/registration_management?error=' + str(e))
        
        # GET request - show form
        return request.render('custom_registration.officer_course_form_template', {
            'page_title': 'Create New Course',
            'course': None,
            'action': 'create',
        })

    @http.route('/officer/course/edit/<int:course_id>', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def edit_course(self, course_id, **kwargs):
        """Edit an existing course."""
        self._check_officer_access()
        
        Course = request.env['education.course'].sudo()
        course = Course.browse(course_id)
        
        if not course.exists():
            return request.redirect('/officer/registration_management?error=course_not_found')
        
        if request.httprequest.method == 'POST':
            try:
                course_data = {
                    'name': kwargs.get('name'),
                    'code': kwargs.get('code'),
                    'description': kwargs.get('description'),
                    'total_seats': int(kwargs.get('total_seats', 30)),
                    'schedule': kwargs.get('schedule'),
                    'instructor': kwargs.get('instructor'),
                    'credits': int(kwargs.get('credits', 3)),
                    'registration_open': kwargs.get('registration_open') == 'on',
                    'active': kwargs.get('active') == 'on',
                }
                
                if kwargs.get('add_drop_deadline'):
                    course_data['add_drop_deadline'] = kwargs.get('add_drop_deadline')
                else:
                    course_data['add_drop_deadline'] = False
                
                course.write(course_data)
                
                return request.redirect('/officer/registration_management?message=course_updated')
                
            except Exception as e:
                _logger.error('Error updating course: %s', str(e))
                return request.redirect(f'/officer/course/edit/{course_id}?error=' + str(e))
        
        # GET request - show form
        return request.render('custom_registration.officer_course_form_template', {
            'page_title': 'Edit Course',
            'course': course,
            'action': 'edit',
        })

    @http.route('/officer/course/archive/<int:course_id>', type='http', auth='user', website=True, methods=['POST'])
    def archive_course(self, course_id, **kwargs):
        """Archive a course."""
        self._check_officer_access()
        
        try:
            Course = request.env['education.course'].sudo()
            course = Course.browse(course_id)
            
            if course.exists():
                course.action_archive()
                return request.redirect('/officer/registration_management?message=course_archived')
            else:
                return request.redirect('/officer/registration_management?error=course_not_found')
                
        except Exception as e:
            _logger.error('Error archiving course: %s', str(e))
            return request.redirect('/officer/registration_management?error=' + str(e))

    @http.route('/officer/course/unarchive/<int:course_id>', type='http', auth='user', website=True, methods=['POST'])
    def unarchive_course(self, course_id, **kwargs):
        """Unarchive a course."""
        self._check_officer_access()
        
        try:
            Course = request.env['education.course'].sudo().with_context(active_test=False)
            course = Course.browse(course_id)
            
            if course.exists():
                course.action_unarchive()
                return request.redirect('/officer/registration_management?message=course_unarchived')
            else:
                return request.redirect('/officer/registration_management?error=course_not_found')
                
        except Exception as e:
            _logger.error('Error unarchiving course: %s', str(e))
            return request.redirect('/officer/registration_management?error=' + str(e))

    @http.route('/officer/course/toggle_registration/<int:course_id>', type='http', auth='user', website=True, methods=['POST'])
    def toggle_course_registration(self, course_id, **kwargs):
        """Toggle registration open/closed for a course."""
        self._check_officer_access()
        
        try:
            Course = request.env['education.course'].sudo()
            course = Course.browse(course_id)
            
            if course.exists():
                if course.registration_open:
                    course.action_close_registration()
                    message = 'registration_closed'
                else:
                    course.action_open_registration()
                    message = 'registration_opened'
                return request.redirect(f'/officer/registration_management?message={message}')
            else:
                return request.redirect('/officer/registration_management?error=course_not_found')
                
        except Exception as e:
            _logger.error('Error toggling course registration: %s', str(e))
            return request.redirect('/officer/registration_management?error=' + str(e))

    # ==================== Student Registration Management ====================

    @http.route('/officer/student/<int:student_id>/add_course', type='http', auth='user', website=True, methods=['POST'])
    def officer_add_course(self, student_id, course_id, **kwargs):
        """
        Add a course to a student's schedule (officer override).
        
        Bypasses normal restrictions like hold status and add/drop deadlines.
        """
        self._check_officer_access()
        
        try:
            course_id = int(course_id)
            Registration = request.env['education.registration'].sudo()
            
            # Check if already enrolled
            existing = Registration.search([
                ('student_id', '=', student_id),
                ('course_id', '=', course_id),
                ('state', '=', 'enrolled')
            ], limit=1)
            
            if existing:
                return request.redirect(
                    f'/officer/registration_management?student_id={student_id}&error=already_enrolled'
                )
            
            # Create registration with officer override
            Registration.create({
                'student_id': student_id,
                'course_id': course_id,
                'is_officer_override': True,
            })
            
            _logger.info(
                'Officer %s added course %s to student %s',
                request.env.user.name, course_id, student_id
            )
            
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&message=course_added'
            )
            
        except ValidationError as e:
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&error={e.args[0]}'
            )
        except Exception as e:
            _logger.error('Error adding course for student: %s', str(e))
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&error={str(e)}'
            )

    @http.route('/officer/student/<int:student_id>/drop_course', type='http', auth='user', website=True, methods=['POST'])
    def officer_drop_course(self, student_id, registration_id, **kwargs):
        """
        Drop a course from a student's schedule (officer override).
        
        Bypasses add/drop deadline restrictions.
        """
        self._check_officer_access()
        
        try:
            registration_id = int(registration_id)
            Registration = request.env['education.registration'].sudo()
            
            registration = Registration.browse(registration_id)
            
            if not registration.exists() or registration.student_id.id != student_id:
                return request.redirect(
                    f'/officer/registration_management?student_id={student_id}&error=registration_not_found'
                )
            
            registration.action_drop(is_officer_override=True)
            
            _logger.info(
                'Officer %s dropped course %s for student %s',
                request.env.user.name, registration.course_id.code, student_id
            )
            
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&message=course_dropped'
            )
            
        except Exception as e:
            _logger.error('Error dropping course for student: %s', str(e))
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&error={str(e)}'
            )

    @http.route('/officer/student/<int:student_id>/reenroll', type='http', auth='user', website=True, methods=['POST'])
    def officer_reenroll_course(self, student_id, registration_id, **kwargs):
        """Re-enroll a student in a dropped course."""
        self._check_officer_access()
        
        try:
            registration_id = int(registration_id)
            Registration = request.env['education.registration'].sudo()
            
            registration = Registration.browse(registration_id)
            
            if not registration.exists() or registration.student_id.id != student_id:
                return request.redirect(
                    f'/officer/registration_management?student_id={student_id}&error=registration_not_found'
                )
            
            registration.action_reenroll()
            
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&message=course_reenrolled'
            )
            
        except ValidationError as e:
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&error={e.args[0]}'
            )
        except Exception as e:
            _logger.error('Error re-enrolling student: %s', str(e))
            return request.redirect(
                f'/officer/registration_management?student_id={student_id}&error={str(e)}'
            )

    # ==================== API Endpoints ====================

    @http.route('/officer/api/students/search', type='jsonrpc', auth='user')
    def api_search_students(self, query, **kwargs):
        """API endpoint to search students."""
        self._check_officer_access()
        
        Users = request.env['res.users'].sudo()
        students = Users.search([
            '|', '|',
            ('name', 'ilike', query),
            ('login', 'ilike', query),
            ('email', 'ilike', query)
        ], limit=20)
        
        return [{
            'id': s.id,
            'name': s.name,
            'email': s.email or s.login,
            'is_on_hold': s.is_on_hold,
        } for s in students]

    @http.route('/officer/api/courses', type='jsonrpc', auth='user')
    def api_get_all_courses(self, include_archived=False, **kwargs):
        """API endpoint to get all courses."""
        self._check_officer_access()
        
        Course = request.env['education.course'].sudo()
        if include_archived:
            Course = Course.with_context(active_test=False)
        
        courses = Course.search([])
        
        return [{
            'id': c.id,
            'code': c.code,
            'name': c.name,
            'total_seats': c.total_seats,
            'available_seats': c.available_seats,
            'registration_open': c.registration_open,
            'active': c.active,
        } for c in courses]
