# -*- coding: utf-8 -*-
"""
Officer/Professor Portal Controller

Implements staff-facing portal features:
- Admission pipeline management (US 01.07, US 01.08)
- Document review with OCR data
- Petition review and approval workflow (US 03.03, US 03.04, US 03.05)
- Student record access

Access restricted to users with admission officer group membership.
"""

import logging
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from werkzeug.exceptions import Forbidden, NotFound

from .auth import EduPortalAccessMixin

_logger = logging.getLogger(__name__)


class OfficerPortalController(http.Controller, EduPortalAccessMixin):
    """
    Controller for admission officer and professor portal views.
    
    Provides interfaces for:
    - Admission application review
    - Petition approval/rejection
    - Student record management
    """
    
    OFFICER_GROUP = 'edu_mang_auth.group_erp_admission_officer'
    ITEMS_PER_PAGE = 20
    
    # =========================================================================
    # Dashboard
    # =========================================================================
    
    @http.route('/edu-portal/officer/dashboard', type='http', auth='user', website=True)
    def officer_dashboard(self, **kw):
        """
        Officer dashboard with admission and petition statistics.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect('session_expired')
        
        # Admission statistics
        Admission = request.env['school.admission'].sudo()
        admission_stats = {
            'submitted': Admission.search_count([('state', '=', 'submitted')]),
            'under_review': Admission.search_count([('state', '=', 'under_review')]),
            'accepted': Admission.search_count([('state', '=', 'accepted')]),
            'rejected': Admission.search_count([('state', '=', 'rejected')]),
            'total': Admission.search_count([]),
        }
        
        # Petition statistics
        Petition = request.env['student.petition'].sudo()
        petition_stats = {
            'submitted': Petition.search_count([('state', '=', 'submitted')]),
            'under_review': Petition.search_count([('state', '=', 'under_review')]),
            'pending_total': Petition.search_count([('state', 'in', ['submitted', 'under_review'])]),
        }
        
        # Recent activity
        recent_admissions = Admission.search([], limit=5, order='create_date desc')
        recent_petitions = Petition.search([], limit=5, order='create_date desc')
        
        values = {
            'page_name': 'Officer Dashboard',
            'user': user,
            'admission_stats': admission_stats,
            'petition_stats': petition_stats,
            'recent_admissions': recent_admissions,
            'recent_petitions': recent_petitions,
        }
        
        return request.render('edu_portal_gateway.officer_dashboard', values)
    
    # =========================================================================
    # Admission Pipeline (US 01.07, US 01.08)
    # =========================================================================
    
    @http.route('/edu-portal/officer/admissions', type='http', auth='user', website=True)
    def officer_admissions_list(self, page=1, state=None, program=None, search=None, **kw):
        """
        List admission applications with filtering.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Admission = request.env['school.admission'].sudo()
        Program = request.env['school.program'].sudo()
        
        # Build domain
        domain = []
        
        if state and state != 'all':
            domain.append(('state', '=', state))
        
        if program:
            domain.append(('program_id', '=', int(program)))
        
        if search:
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', search))
            domain.append(('email', 'ilike', search))
            domain.append(('reference', 'ilike', search))
        
        # Pagination
        page = int(page) or 1
        total = Admission.search_count(domain)
        offset = (page - 1) * self.ITEMS_PER_PAGE
        
        admissions = Admission.search(
            domain,
            limit=self.ITEMS_PER_PAGE,
            offset=offset,
            order='create_date desc'
        )
        
        # Status counts
        status_counts = {
            'all': Admission.search_count([]),
            'submitted': Admission.search_count([('state', '=', 'submitted')]),
            'under_review': Admission.search_count([('state', '=', 'under_review')]),
            'accepted': Admission.search_count([('state', '=', 'accepted')]),
            'rejected': Admission.search_count([('state', '=', 'rejected')]),
        }
        
        # Available programs for filter
        programs = Program.search([('active', '=', True)])
        
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        values = {
            'page_name': 'Admission Pipeline',
            'user': user,
            'admissions': admissions,
            'programs': programs,
            'current_state': state or 'all',
            'current_program': int(program) if program else None,
            'search': search or '',
            'status_counts': status_counts,
            'page': page,
            'total_pages': total_pages,
            'total': total,
        }
        
        return request.render('edu_portal_gateway.officer_admissions_list', values)
    
    @http.route('/edu-portal/officer/admissions/kanban', type='http', auth='user', website=True)
    def officer_admissions_kanban(self, **kw):
        """
        Kanban board view for admission pipeline.
        
        Groups applications by status for drag-and-drop workflow.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Admission = request.env['school.admission'].sudo()
        
        # Group by state
        columns = {
            'submitted': {
                'name': 'New Applications',
                'items': Admission.search([('state', '=', 'submitted')], order='create_date desc'),
            },
            'under_review': {
                'name': 'Under Review',
                'items': Admission.search([('state', '=', 'under_review')], order='create_date desc'),
            },
            'accepted': {
                'name': 'Accepted',
                'items': Admission.search([('state', '=', 'accepted')], order='create_date desc', limit=20),
            },
            'rejected': {
                'name': 'Rejected',
                'items': Admission.search([('state', '=', 'rejected')], order='create_date desc', limit=20),
            },
        }
        
        values = {
            'page_name': 'Admission Kanban',
            'user': user,
            'columns': columns,
        }
        
        return request.render('edu_portal_gateway.officer_admissions_kanban', values)
    
    @http.route('/edu-portal/officer/admissions/<int:admission_id>', type='http', auth='user', website=True)
    def officer_admission_detail(self, admission_id, **kw):
        """
        View admission application details with documents.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Admission = request.env['school.admission'].sudo()
        admission = Admission.browse(admission_id)
        
        if not admission.exists():
            raise NotFound('Application not found.')
        
        values = {
            'page_name': f'Application {admission.reference}',
            'user': user,
            'admission': admission,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.officer_admission_detail', values)
    
    @http.route('/edu-portal/officer/admissions/<int:admission_id>/action', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_admission_action(self, admission_id, action, **kw):
        """
        Process admission workflow actions (review, accept, reject).
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Admission = request.env['school.admission'].sudo()
        admission = Admission.browse(admission_id)
        
        if not admission.exists():
            return request.redirect('/edu-portal/officer/admissions?error=Application not found')
        
        try:
            if action == 'review':
                admission.action_under_review()
                message = 'Application moved to review.'
            elif action == 'accept':
                admission.action_accept()
                message = 'Application accepted. Student account created.'
            elif action == 'reject':
                admission.action_reject()
                message = 'Application rejected.'
            elif action == 'reset':
                admission.action_reset_to_draft()
                message = 'Application reset to draft.'
            else:
                return request.redirect(f'/edu-portal/officer/admissions/{admission_id}?error=Invalid action')
            
            _logger.info(
                'Admission action: %s on %s by %s',
                action, admission.reference, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/admissions/{admission_id}?success={message}')
            
        except (ValidationError, UserError) as e:
            return request.redirect(f'/edu-portal/officer/admissions/{admission_id}?error={str(e)}')
    
    # =========================================================================
    # Petition Review (US 03.03, US 03.04, US 03.05)
    # =========================================================================
    
    @http.route('/edu-portal/officer/petitions', type='http', auth='user', website=True)
    def officer_petitions_list(self, page=1, state=None, petition_type=None, urgency=None, **kw):
        """
        List petitions for review with filtering.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Petition = request.env['student.petition'].sudo()
        PetitionType = request.env['petition.type'].sudo()
        
        # Build domain - show only submitted and under_review by default
        domain = []
        
        if state and state != 'all':
            domain.append(('state', '=', state))
        else:
            domain.append(('state', 'in', ['submitted', 'under_review']))
        
        if petition_type:
            domain.append(('petition_type_id', '=', int(petition_type)))
        
        # Pagination
        page = int(page) or 1
        total = Petition.search_count(domain)
        offset = (page - 1) * self.ITEMS_PER_PAGE
        
        petitions = Petition.search(
            domain,
            limit=self.ITEMS_PER_PAGE,
            offset=offset,
            order='days_pending desc, create_date desc'
        )
        
        # Status counts
        status_counts = {
            'pending': Petition.search_count([('state', 'in', ['submitted', 'under_review'])]),
            'submitted': Petition.search_count([('state', '=', 'submitted')]),
            'under_review': Petition.search_count([('state', '=', 'under_review')]),
            'approved': Petition.search_count([('state', '=', 'approved')]),
            'rejected': Petition.search_count([('state', '=', 'rejected')]),
        }
        
        # Available petition types for filter
        petition_types = PetitionType.search([])
        
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        values = {
            'page_name': 'Petition Review',
            'user': user,
            'petitions': petitions,
            'petition_types': petition_types,
            'current_state': state or 'pending',
            'current_type': int(petition_type) if petition_type else None,
            'status_counts': status_counts,
            'page': page,
            'total_pages': total_pages,
            'total': total,
        }
        
        return request.render('edu_portal_gateway.officer_petitions_list', values)
    
    @http.route('/edu-portal/officer/petitions/<int:petition_id>', type='http', auth='user', website=True)
    def officer_petition_detail(self, petition_id, **kw):
        """
        View petition details for review/decision.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Petition = request.env['student.petition'].sudo()
        petition = Petition.browse(petition_id)
        
        if not petition.exists():
            raise NotFound('Petition not found.')
        
        # Get student's other petitions for context
        student_history = Petition.search([
            ('student_id', '=', petition.student_id.id),
            ('id', '!=', petition.id)
        ], limit=5, order='create_date desc')
        
        values = {
            'page_name': f'Petition {petition.name}',
            'user': user,
            'petition': petition,
            'student_history': student_history,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.officer_petition_detail', values)
    
    @http.route('/edu-portal/officer/petitions/<int:petition_id>/action', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_petition_action(self, petition_id, action, **kw):
        """
        Process petition workflow actions (review, approve, reject).
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Petition = request.env['student.petition'].sudo()
        petition = Petition.browse(petition_id)
        
        if not petition.exists():
            return request.redirect('/edu-portal/officer/petitions?error=Petition not found')
        
        try:
            if action == 'review':
                petition.write({
                    'state': 'under_review',
                    'reviewer_id': user.id
                })
                message = 'Petition marked for review.'
                
            elif action == 'approve':
                # Add reviewer comments if provided
                comments = kw.get('comments', '').strip()
                if comments:
                    petition.write({'comments': comments})
                petition.action_approve()
                message = 'Petition approved.'
                
            elif action == 'reject':
                # Rejection requires a reason
                rejection_reason = kw.get('rejection_reason', '').strip()
                if not rejection_reason:
                    return request.redirect(
                        f'/edu-portal/officer/petitions/{petition_id}?error=Please provide a rejection reason'
                    )
                petition.write({'rejection_reason': rejection_reason})
                petition.action_reject()
                message = 'Petition rejected.'
                
            else:
                return request.redirect(f'/edu-portal/officer/petitions/{petition_id}?error=Invalid action')
            
            _logger.info(
                'Petition action: %s on %s by %s',
                action, petition.name, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/petitions/{petition_id}?success={message}')
            
        except (ValidationError, UserError) as e:
            return request.redirect(f'/edu-portal/officer/petitions/{petition_id}?error={str(e)}')
    
    # =========================================================================
    # Student Records
    # =========================================================================
    
    @http.route('/edu-portal/officer/students', type='http', auth='user', website=True)
    def officer_students_list(self, page=1, search=None, **kw):
        """
        Browse student records.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Users = request.env['res.users'].sudo()
        student_group = request.env.ref('edu_mang_auth.group_erp_student')
        
        # Build domain - only students
        domain = [('group_ids', 'in', [student_group.id])]
        
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
        
        students = Users.search(
            domain,
            limit=self.ITEMS_PER_PAGE,
            offset=offset,
            order='name'
        )
        
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        values = {
            'page_name': 'Student Directory',
            'user': user,
            'students': students,
            'search': search or '',
            'page': page,
            'total_pages': total_pages,
            'total': total,
        }
        
        return request.render('edu_portal_gateway.officer_students_list', values)
    
    @http.route('/edu-portal/officer/students/<int:student_id>', type='http', auth='user', website=True)
    def officer_student_detail(self, student_id, **kw):
        """
        View student profile with academic records.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Users = request.env['res.users'].sudo()
        student = Users.browse(student_id)
        
        if not student.exists():
            raise NotFound('Student not found.')
        
        # Get student's registrations
        Registration = request.env['education.registration'].sudo()
        registrations = Registration.search([
            ('student_id', '=', student.id)
        ], order='registration_date desc')
        
        # Get student's petitions
        Petition = request.env['student.petition'].sudo()
        petitions = Petition.search([
            ('student_id', '=', student.partner_id.id)
        ], order='create_date desc', limit=10)
        
        values = {
            'page_name': f'Student: {student.name}',
            'user': user,
            'student': student,
            'registrations': registrations,
            'petitions': petitions,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.officer_student_detail', values)
    
    @http.route('/edu-portal/officer/students/<int:student_id>/toggle-hold', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_student_toggle_hold(self, student_id, **kw):
        """
        Toggle student hold status.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Users = request.env['res.users'].sudo()
        student = Users.browse(student_id)
        
        if not student.exists():
            return request.redirect('/edu-portal/officer/students?error=Student not found')
        
        try:
            current_hold = getattr(student, 'is_on_hold', False)
            student.write({'is_on_hold': not current_hold})
            
            status = 'removed' if current_hold else 'placed'
            _logger.info(
                'Student hold %s: %s by %s',
                status, student.login, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/students/{student_id}?success=Hold {status}')
            
        except Exception as e:
            return request.redirect(f'/edu-portal/officer/students/{student_id}?error={str(e)}')
    
    # =========================================================================
    # Course Management
    # =========================================================================
    
    @http.route('/edu-portal/officer/courses', type='http', auth='user', website=True)
    def officer_courses_list(self, page=1, search=None, status=None, **kw):
        """
        List all courses with filtering and search.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        
        # Build domain
        domain = []
        
        # By default show active courses, allow filtering inactive
        if status == 'inactive':
            domain.append(('active', '=', False))
        elif status == 'all':
            pass  # Show all
        else:
            domain.append(('active', '=', True))
        
        if search:
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', search))
            domain.append(('code', 'ilike', search))
            domain.append(('instructor', 'ilike', search))
        
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
        
        # Status counts
        status_counts = {
            'active': Course.search_count([('active', '=', True)]),
            'inactive': Course.search_count([('active', '=', False)]),
            'open': Course.search_count([('active', '=', True), ('registration_open', '=', True)]),
            'closed': Course.search_count([('active', '=', True), ('registration_open', '=', False)]),
            'total': Course.search_count([]),
        }
        
        total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
        
        values = {
            'page_name': 'Course Management',
            'user': user,
            'courses': courses,
            'search': search or '',
            'current_status': status or 'active',
            'status_counts': status_counts,
            'page': page,
            'total_pages': total_pages,
            'total': total,
            'success': kw.get('success'),
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.officer_courses_list', values)
    
    @http.route('/edu-portal/officer/courses/new', type='http', auth='user', website=True)
    def officer_course_create_form(self, **kw):
        """
        Display form to create a new course.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        values = {
            'page_name': 'Create Course',
            'user': user,
            'course': None,
            'is_edit': False,
            'semesters': [('fall', 'Fall'), ('spring', 'Spring'), ('summer', 'Summer')],
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.officer_course_form', values)
    
    @http.route('/edu-portal/officer/courses/create', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_course_create(self, **kw):
        """
        Process course creation.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        
        try:
            # Validate required fields
            name = kw.get('name', '').strip()
            code = kw.get('code', '').strip()
            
            if not name or not code:
                return request.redirect('/edu-portal/officer/courses/new?error=Course name and code are required')
            
            # Create course
            course_vals = {
                'name': name,
                'code': code,
                'description': kw.get('description', '').strip(),
                'instructor': kw.get('instructor', '').strip(),
                'total_seats': int(kw.get('total_seats', 30)),
                'credits': int(kw.get('credits', 3)),
                'schedule': kw.get('schedule', '').strip(),
                'semester': kw.get('semester', 'fall'),
                'year': int(kw.get('year', fields.Date.today().year)),
                'registration_open': kw.get('registration_open') == 'on',
                'active': True,
            }
            
            course = Course.create(course_vals)
            
            _logger.info(
                'Course created: %s (%s) by %s',
                course.name, course.code, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/courses?success=Course {course.code} created successfully')
            
        except Exception as e:
            _logger.error('Course creation failed: %s', str(e))
            return request.redirect(f'/edu-portal/officer/courses/new?error={str(e)}')
    
    @http.route('/edu-portal/officer/courses/<int:course_id>/edit', type='http', auth='user', website=True)
    def officer_course_edit_form(self, course_id, **kw):
        """
        Display form to edit an existing course.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        course = Course.browse(course_id)
        
        if not course.exists():
            raise NotFound('Course not found.')
        
        values = {
            'page_name': f'Edit Course: {course.code}',
            'user': user,
            'course': course,
            'is_edit': True,
            'semesters': [('fall', 'Fall'), ('spring', 'Spring'), ('summer', 'Summer')],
            'error': kw.get('error'),
        }
        
        return request.render('edu_portal_gateway.officer_course_form', values)
    
    @http.route('/edu-portal/officer/courses/<int:course_id>/update', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_course_update(self, course_id, **kw):
        """
        Process course update.
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        course = Course.browse(course_id)
        
        if not course.exists():
            return request.redirect('/edu-portal/officer/courses?error=Course not found')
        
        try:
            # Validate required fields
            name = kw.get('name', '').strip()
            code = kw.get('code', '').strip()
            
            if not name or not code:
                return request.redirect(f'/edu-portal/officer/courses/{course_id}/edit?error=Course name and code are required')
            
            # Update course
            course_vals = {
                'name': name,
                'code': code,
                'description': kw.get('description', '').strip(),
                'instructor': kw.get('instructor', '').strip(),
                'total_seats': int(kw.get('total_seats', 30)),
                'credits': int(kw.get('credits', 3)),
                'schedule': kw.get('schedule', '').strip(),
                'semester': kw.get('semester', 'fall'),
                'year': int(kw.get('year', fields.Date.today().year)),
                'registration_open': kw.get('registration_open') == 'on',
            }
            
            course.write(course_vals)
            
            _logger.info(
                'Course updated: %s (%s) by %s',
                course.name, course.code, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/courses?success=Course {course.code} updated successfully')
            
        except Exception as e:
            _logger.error('Course update failed: %s', str(e))
            return request.redirect(f'/edu-portal/officer/courses/{course_id}/edit?error={str(e)}')
    
    @http.route('/edu-portal/officer/courses/<int:course_id>/toggle-status', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_course_toggle_status(self, course_id, **kw):
        """
        Toggle course registration status (open/closed).
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        course = Course.browse(course_id)
        
        if not course.exists():
            return request.redirect('/edu-portal/officer/courses?error=Course not found')
        
        try:
            current_status = course.registration_open
            course.write({'registration_open': not current_status})
            
            status = 'opened' if not current_status else 'closed'
            _logger.info(
                'Course registration %s: %s by %s',
                status, course.code, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/courses?success=Course {course.code} registration {status}')
            
        except Exception as e:
            return request.redirect(f'/edu-portal/officer/courses?error={str(e)}')
    
    @http.route('/edu-portal/officer/courses/<int:course_id>/toggle-active', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_course_toggle_active(self, course_id, **kw):
        """
        Toggle course active status (archive/unarchive).
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        course = Course.browse(course_id)
        
        if not course.exists():
            return request.redirect('/edu-portal/officer/courses?error=Course not found')
        
        try:
            current_status = course.active
            course.write({'active': not current_status})
            
            status = 'archived' if current_status else 'restored'
            _logger.info(
                'Course %s: %s by %s',
                status, course.code, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/courses?success=Course {course.code} {status}')
            
        except Exception as e:
            return request.redirect(f'/edu-portal/officer/courses?error={str(e)}')
    
    @http.route('/edu-portal/officer/courses/<int:course_id>/delete', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def officer_course_delete(self, course_id, **kw):
        """
        Delete a course (permanently).
        """
        user = self._require_group(self.OFFICER_GROUP)
        if not user:
            return self._get_login_redirect()
        
        Course = request.env['education.course'].sudo()
        course = Course.browse(course_id)
        
        if not course.exists():
            return request.redirect('/edu-portal/officer/courses?error=Course not found')
        
        try:
            course_code = course.code
            course.unlink()
            
            _logger.info(
                'Course deleted: %s by %s',
                course_code, user.login
            )
            
            return request.redirect(f'/edu-portal/officer/courses?success=Course {course_code} deleted')
            
        except Exception as e:
            _logger.error('Course deletion failed: %s', str(e))
            return request.redirect(f'/edu-portal/officer/courses?error={str(e)}')
