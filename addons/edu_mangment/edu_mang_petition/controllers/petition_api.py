"""
JSON-RPC controllers for the student petition system.

These endpoints are consumed by the FastAPI gateway (via /web/dataset/call_kw
proxying) and mirror the gateway's own petition router logic so Odoo enforces
ORM-level access rules in addition to the gateway's JWT/RBAC layer.

All routes use type='json' (Odoo JSON-RPC) and auth='user' so Odoo validates
the service-account session cookie set by the gateway.
"""
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PetitionApiController(http.Controller):

    @http.route('/edu/api/petitions/types', type='json', auth='user', methods=['POST'], csrf=False)
    def list_petition_types(self, **kwargs):
        """Return active petition types the student can choose from."""
        types = request.env['petition.type'].sudo().search_read(
            [('active', '=', True)],
            fields=['id', 'name', 'description'],
            order='name asc',
        )
        return {'petition_types': types}

    @http.route('/edu/api/petitions/my', type='json', auth='user', methods=['POST'], csrf=False)
    def my_petitions(self, **kwargs):
        """Return the calling user's own petitions (any state)."""
        user = request.env.user
        petitions = request.env['student.petition'].search_read(
            [('student_id', '=', user.partner_id.id)],
            fields=['name', 'subject', 'state', 'current_tier',
                    'petition_type_id', 'submitted_date', 'days_pending'],
            order='create_date desc',
        )
        return {'count': len(petitions), 'petitions': petitions}

    @http.route('/edu/api/petitions/submit', type='json', auth='user', methods=['POST'], csrf=False)
    def submit_petition(self, petition_type_id, subject, description,
                        course_id=None, requested_date=None, **kwargs):
        """Create and immediately submit a new petition on behalf of the caller."""
        if not petition_type_id or not subject or not description:
            return {'error': 'petition_type_id, subject, and description are required'}

        user = request.env.user
        vals = {
            'petition_type_id': int(petition_type_id),
            'subject': subject[:200],
            'description': description[:5000],
            'student_id': user.partner_id.id,
        }
        if course_id:
            vals['course_id'] = int(course_id)
        if requested_date:
            vals['requested_date'] = requested_date

        petition = request.env['student.petition'].sudo().create(vals)
        try:
            petition.action_submit()
        except Exception as e:
            _logger.error('Petition auto-submit failed for %s: %s', petition.name, e)

        return {
            'petition_id': petition.id,
            'reference':   petition.name,
            'state':       petition.state,
            'current_tier': petition.current_tier,
        }

    @http.route('/edu/api/petitions/faculty/queue', type='json', auth='user', methods=['POST'], csrf=False)
    def faculty_queue(self, states=None, limit=50, **kwargs):
        """
        Return petitions visible to the current faculty user based on their tier.
        Only instructor / advisor / chair / admin roles reach this endpoint
        (enforced at the gateway RBAC layer; Odoo record rules provide defence in depth).
        """
        user = request.env.user
        if states is None:
            states = ['submitted', 'under_review']

        domain = [('state', 'in', states)]

        if user.has_group('edu_mang_auth.group_erp_instructor'):
            domain += [
                ('current_tier', '=', 'instructor'),
                ('course_id.instructor_user_id', '=', user.id),
            ]
        elif user.has_group('edu_mang_auth.group_erp_academic_advisor'):
            domain += [('current_tier', '=', 'advisor')]
        elif user.has_group('edu_mang_auth.group_erp_department_chair'):
            domain += [
                ('current_tier', 'in', ['chair', 'done']),
                ('department_id.chair_id', '=', user.id),
            ]
        elif not user.has_group('edu_mang_auth.group_erp_admin'):
            return {'error': 'Access denied'}

        petitions = request.env['student.petition'].sudo().search_read(
            domain,
            fields=['id', 'name', 'subject', 'student_id', 'petition_type_id',
                    'course_id', 'department_id', 'current_tier', 'state',
                    'days_pending', 'submitted_date', 'is_escalated'],
            limit=int(limit),
            order='submitted_date asc',
        )
        return {'count': len(petitions), 'petitions': petitions}

    @http.route('/edu/api/petitions/<int:petition_id>/action', type='json',
                auth='user', methods=['POST'], csrf=False)
    def tier_action(self, petition_id, action, reason=None, **kwargs):
        """Approve, reject, or escalate a petition at the current tier."""
        _ACTION_MAP = {
            'approve':  'tier_approve',
            'reject':   'tier_reject',
            'escalate': 'action_escalate',
        }
        method_name = _ACTION_MAP.get(action)
        if not method_name:
            return {'error': f"Unknown action '{action}'. Use: approve, reject, escalate"}

        petition = request.env['student.petition'].sudo().browse(petition_id)
        if not petition.exists():
            return {'error': 'Petition not found'}

        try:
            getattr(petition, method_name)(
                acting_user_id=request.env.user.id,
                reason=reason,
            )
        except Exception as e:
            _logger.error('Tier action %s failed on petition %s: %s', action, petition_id, e)
            return {'error': str(e)}

        petition.invalidate_recordset()
        return {
            'success':      True,
            'petition_id':  petition_id,
            'action':       action,
            'new_state':    petition.state,
            'current_tier': petition.current_tier,
        }

    @http.route('/edu/api/petitions/<int:petition_id>/override', type='json',
                auth='user', methods=['POST'], csrf=False)
    def chair_override(self, petition_id, decision, reason, **kwargs):
        """Department Chair final override — bypasses the tier sequence."""
        if decision not in ('approve', 'reject'):
            return {'error': "decision must be 'approve' or 'reject'"}
        if not reason or len(reason.strip()) < 5:
            return {'error': 'A meaningful override reason is required (min 5 chars)'}

        petition = request.env['student.petition'].sudo().browse(petition_id)
        if not petition.exists():
            return {'error': 'Petition not found'}

        try:
            petition.chair_override(
                acting_user_id=request.env.user.id,
                decision=decision,
                reason=reason,
            )
        except Exception as e:
            _logger.error('Chair override failed on petition %s: %s', petition_id, e)
            return {'error': str(e)}

        petition.invalidate_recordset()
        return {
            'success':        True,
            'petition_id':    petition_id,
            'decision':       decision,
            'final_state':    petition.state,
            'override_reason': petition.override_reason,
        }
