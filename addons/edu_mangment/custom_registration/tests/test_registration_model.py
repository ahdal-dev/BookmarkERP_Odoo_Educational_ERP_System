# -*- coding: utf-8 -*-
"""
Odoo Unit Tests: education.registration Model
Tests enrollment, drop, re-enroll, seat locking, holds, officer overrides.
Run via: odoo-bin --test-enable --test-tags custom_registration
"""
from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestEducationRegistration(TransactionCase):
    """Test suite for education.registration model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Course = cls.env['education.course']
        cls.Registration = cls.env['education.registration']

        cls.course = cls.Course.create({
            'name': 'Data Structures',
            'code': 'CS201',
            'total_seats': 2,
            'registration_open': True,
        })
        cls.student = cls.env['res.users'].create({
            'name': 'Student One',
            'login': 'student_one_cs201',
            'is_on_hold': False,
        })
        cls.student2 = cls.env['res.users'].create({
            'name': 'Student Two',
            'login': 'student_two_cs201',
            'is_on_hold': False,
        })

    # ── Enrollment Creation ─────────────────────────────────────────────────

    def test_create_enrollment_success(self):
        """Enrolling a student in an open course with seats should succeed."""
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        self.assertEqual(reg.state, 'enrolled')
        self.assertTrue(reg.registration_date)

    def test_enrollment_decreases_available_seats(self):
        """Creating an enrollment should decrease available_seats."""
        self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        self.course._compute_available_seats()
        self.assertEqual(self.course.available_seats, 1)

    def test_duplicate_enrollment_rejected(self):
        """Same student cannot enroll twice in the same course."""
        self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        with self.assertRaises(ValidationError):
            self.Registration.create({
                'student_id': self.student.id,
                'course_id': self.course.id,
            })

    def test_no_seats_available_rejected(self):
        """Enrollment should fail when all seats are filled."""
        # Fill both seats
        self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        self.Registration.create({
            'student_id': self.student2.id,
            'course_id': self.course.id,
        })
        # Third student should be rejected
        student3 = self.env['res.users'].create({
            'name': 'Student Three', 'login': 'student_three_cs201',
            'is_on_hold': False,
        })
        with self.assertRaises(ValidationError):
            self.Registration.create({
                'student_id': student3.id,
                'course_id': self.course.id,
            })

    def test_closed_registration_rejected(self):
        """Enrollment should fail when registration_open is False."""
        closed_course = self.Course.create({
            'name': 'Closed Course', 'code': 'CL001',
            'total_seats': 30, 'registration_open': False,
        })
        with self.assertRaises(ValidationError):
            self.Registration.create({
                'student_id': self.student.id,
                'course_id': closed_course.id,
            })

    # ── Student Hold ────────────────────────────────────────────────────────

    def test_student_on_hold_rejected(self):
        """Students on hold should not be able to register."""
        held_student = self.env['res.users'].create({
            'name': 'Held Student', 'login': 'held_student_cs201',
            'is_on_hold': True,
        })
        with self.assertRaises(ValidationError):
            self.Registration.create({
                'student_id': held_student.id,
                'course_id': self.course.id,
            })

    # ── Officer Override ────────────────────────────────────────────────────

    def test_officer_override_bypasses_closed_registration(self):
        """Officer override should allow enrollment even when closed."""
        closed_course = self.Course.create({
            'name': 'Override Course', 'code': 'OV001',
            'total_seats': 30, 'registration_open': False,
        })
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': closed_course.id,
            'is_officer_override': True,
        })
        self.assertEqual(reg.state, 'enrolled')

    # ── Drop Action ─────────────────────────────────────────────────────────

    def test_action_drop_changes_state(self):
        """Dropping should set state to 'dropped' and record the date."""
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        reg.action_drop()
        self.assertEqual(reg.state, 'dropped')
        self.assertTrue(reg.dropped_date)

    def test_drop_already_dropped_raises_error(self):
        """Dropping an already-dropped course should raise UserError."""
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        reg.action_drop()
        with self.assertRaises(UserError):
            reg.action_drop()

    def test_drop_past_deadline_rejected(self):
        """Drop after add/drop deadline should fail (unless officer)."""
        course_deadline = self.Course.create({
            'name': 'Deadline Course', 'code': 'DL001',
            'total_seats': 30, 'registration_open': True,
            'add_drop_deadline': date.today() - timedelta(days=1),
        })
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': course_deadline.id,
        })
        with self.assertRaises(ValidationError):
            reg.action_drop()

    def test_officer_drop_bypasses_deadline(self):
        """Officer override should allow drop past deadline."""
        course_deadline = self.Course.create({
            'name': 'Officer Drop Course', 'code': 'OD001',
            'total_seats': 30, 'registration_open': True,
            'add_drop_deadline': date.today() - timedelta(days=1),
        })
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': course_deadline.id,
        })
        reg.action_drop(is_officer_override=True)
        self.assertEqual(reg.state, 'dropped')

    # ── Re-enroll Action ────────────────────────────────────────────────────

    def test_action_reenroll_from_dropped(self):
        """Re-enrolling a dropped registration should set state to enrolled."""
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        reg.action_drop()
        reg.action_reenroll()
        self.assertEqual(reg.state, 'enrolled')
        self.assertFalse(reg.dropped_date)

    def test_reenroll_already_enrolled_raises_error(self):
        """Re-enrolling when already enrolled should raise UserError."""
        reg = self.Registration.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        with self.assertRaises(UserError):
            reg.action_reenroll()


class TestEducationCart(TransactionCase):
    """Test suite for education.cart model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Cart = cls.env['education.cart']
        cls.Course = cls.env['education.course']
        
        cls.course = cls.Course.create({
            'name': 'Algorithm Analysis',
            'code': 'CS301',
            'total_seats': 30,
            'registration_open': True,
        })
        cls.student = cls.env['res.users'].create({
            'name': 'Cart Student',
            'login': 'cart_student',
        })

    def test_cart_to_registration_success(self):
        """action_register should create a registration and remove cart item."""
        cart_item = self.Cart.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        reg = cart_item.action_register()
        self.assertEqual(reg.state, 'enrolled')
        self.assertFalse(cart_item.exists())

    def test_cart_register_on_hold_rejected(self):
        """action_register should fail if student is on hold."""
        self.student.is_on_hold = True
        cart_item = self.Cart.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        with self.assertRaises(ValidationError):
            cart_item.action_register()

    def test_cart_register_closed_rejected(self):
        """action_register should fail if registration is closed."""
        self.course.registration_open = False
        cart_item = self.Cart.create({
            'student_id': self.student.id,
            'course_id': self.course.id,
        })
        with self.assertRaises(ValidationError):
            cart_item.action_register()
