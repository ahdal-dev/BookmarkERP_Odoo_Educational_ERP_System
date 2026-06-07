# -*- coding: utf-8 -*-
"""
Odoo Unit Tests: education.course Model
Tests seat computation, code uniqueness, registration actions, constraints.
Run via: odoo-bin --test-enable --test-tags custom_registration
"""
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestEducationCourse(TransactionCase):
    """Test suite for education.course model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Course = cls.env['education.course']
        cls.course = cls.Course.create({
            'name': 'Introduction to CS',
            'code': 'CS101',
            'total_seats': 30,
            'credits': 3,
            'semester': 'fall',
            'registration_open': False,
        })

    # ── Record Creation ─────────────────────────────────────────────────────

    def test_create_course_with_defaults(self):
        """Course should be created with correct defaults."""
        course = self.Course.create({'name': 'Test Course', 'total_seats': 20})
        self.assertEqual(course.code, 'NEW')
        self.assertTrue(course.active)
        self.assertFalse(course.registration_open)
        self.assertEqual(course.credits, 3)

    def test_display_name_with_code(self):
        """Display name should include code when it's not 'NEW'."""
        self.assertEqual(self.course.display_name, '[CS101] Introduction to CS')

    def test_display_name_without_code(self):
        """Display name should be just the name when code is 'NEW'."""
        course = self.Course.create({'name': 'No Code Course', 'total_seats': 10})
        self.assertEqual(course.display_name, 'No Code Course')

    # ── Available Seats Computation ─────────────────────────────────────────

    def test_available_seats_no_enrollments(self):
        """Available seats should equal total_seats when no one is enrolled."""
        self.assertEqual(self.course.available_seats, 30)

    def test_available_seats_decreases_with_enrollment(self):
        """Available seats should decrease when students enroll."""
        student = self.env['res.users'].create({
            'name': 'Test Student', 'login': 'test_student_cs101',
            'is_on_hold': False,
        })
        self.course.write({'registration_open': True})
        self.env['education.registration'].create({
            'student_id': student.id,
            'course_id': self.course.id,
            'state': 'enrolled',
        })
        self.course._compute_available_seats()
        self.assertEqual(self.course.available_seats, 29)

    # ── Constraints ─────────────────────────────────────────────────────────

    def test_negative_total_seats_rejected(self):
        """Total seats cannot be negative."""
        with self.assertRaises(ValidationError):
            self.Course.create({'name': 'Bad Course', 'total_seats': -1})

    def test_duplicate_code_rejected(self):
        """Two courses with the same code should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.Course.create({
                'name': 'Duplicate Course', 'code': 'CS101', 'total_seats': 10,
            })

    def test_duplicate_code_new_allowed(self):
        """Multiple courses with code 'NEW' should be allowed."""
        c1 = self.Course.create({'name': 'Course A', 'total_seats': 10})
        c2 = self.Course.create({'name': 'Course B', 'total_seats': 10})
        self.assertEqual(c1.code, 'NEW')
        self.assertEqual(c2.code, 'NEW')

    # ── Registration Actions ────────────────────────────────────────────────

    def test_action_open_registration(self):
        """action_open_registration should set registration_open to True."""
        self.course.action_open_registration()
        self.assertTrue(self.course.registration_open)

    def test_action_close_registration(self):
        """action_close_registration should set registration_open to False."""
        self.course.write({'registration_open': True})
        self.course.action_close_registration()
        self.assertFalse(self.course.registration_open)
