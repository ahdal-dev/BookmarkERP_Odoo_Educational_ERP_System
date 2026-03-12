# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestSchoolProgram(TransactionCase):
    """Test suite for school.program model"""

    @classmethod
    def setUpClass(cls):
        super(TestSchoolProgram, cls).setUpClass()
        
        # Standard valid program data
        cls.valid_program_data = {
            'name': 'Software Engineering',
            'code': 'SE101',
            'description': 'Bachelor of Software Engineering',
            'duration': 4,
        }

    # ==========================================
    # Record Creation & Defaults
    # ==========================================

    def test_create_program_with_required_fields(self):
        """Test creating a program record with required fields"""
        program = self.env['school.program'].create({
            'name': 'Computer Science',
        })
        
        self.assertTrue(program.id, "Program record should be created")
        self.assertEqual(program.name, 'Computer Science')

    def test_create_program_with_all_fields(self):
        """Test creating a program with all fields populated"""
        program = self.env['school.program'].create(self.valid_program_data)
        
        self.assertEqual(program.name, 'Software Engineering')
        self.assertEqual(program.code, 'SE101')
        self.assertEqual(program.description, 'Bachelor of Software Engineering')
        self.assertEqual(program.duration, 4)

    def test_default_active_is_true(self):
        """Test that the default active field is True"""
        program = self.env['school.program'].create({
            'name': 'Data Science',
        })
        
        self.assertTrue(program.active, "Default active should be True")

    # ==========================================
    # Computed Field: admission_count
    # ==========================================

    def test_admission_count_zero_by_default(self):
        """Test that a new program has admission_count = 0"""
        program = self.env['school.program'].create(self.valid_program_data)
        
        self.assertEqual(program.admission_count, 0, 
                        "New program should have zero admissions")

    def test_admission_count_with_one_admission(self):
        """Test that admission_count increments when one admission is linked"""
        program = self.env['school.program'].create(self.valid_program_data)
        
        # Create one admission
        self.env['school.admission'].create({
            'name': 'Student One',
            'email': 'student1@example.com',
            'phone': '+1111111111',
            'national_id': 'ID111',
            'program_id': program.id,
        })
        
        self.assertEqual(program.admission_count, 1, 
                        "Program should have 1 admission")

    def test_admission_count_with_multiple_admissions(self):
        """Test that admission_count correctly counts multiple admissions"""
        program = self.env['school.program'].create(self.valid_program_data)
        
        # Create 3 admissions
        for i in range(1, 4):
            self.env['school.admission'].create({
                'name': f'Student {i}',
                'email': f'student{i}@example.com',
                'phone': f'+{i}{i}{i}{i}{i}{i}{i}{i}{i}{i}',
                'national_id': f'ID{i}{i}{i}',
                'program_id': program.id,
            })
        
        self.assertEqual(program.admission_count, 3, 
                        "Program should have 3 admissions")

    def test_admission_count_decreases_on_deletion(self):
        """Test that admission_count decreases when an admission is deleted"""
        program = self.env['school.program'].create(self.valid_program_data)
        
        # Create 2 admissions
        admission1 = self.env['school.admission'].create({
            'name': 'Student 1',
            'email': 'student1@example.com',
            'phone': '+1111111111',
            'national_id': 'ID111',
            'program_id': program.id,
        })
        
        admission2 = self.env['school.admission'].create({
            'name': 'Student 2',
            'email': 'student2@example.com',
            'phone': '+2222222222',
            'national_id': 'ID222',
            'program_id': program.id,
        })
        
        self.assertEqual(program.admission_count, 2)
        
        # Delete one admission
        admission1.unlink()
        
        self.assertEqual(program.admission_count, 1, 
                        "Count should decrease after deletion")

    def test_admission_count_with_different_programs(self):
        """Test that admission_count only counts admissions for the specific program"""
        program1 = self.env['school.program'].create({
            'name': 'Program 1',
        })
        program2 = self.env['school.program'].create({
            'name': 'Program 2',
        })
        
        # Create 2 admissions for program1
        for i in range(2):
            self.env['school.admission'].create({
                'name': f'P1 Student {i}',
                'email': f'p1student{i}@example.com',
                'phone': f'+1{i}{i}{i}{i}{i}{i}{i}{i}{i}',
                'national_id': f'P1-ID{i}',
                'program_id': program1.id,
            })
        
        # Create 3 admissions for program2
        for i in range(3):
            self.env['school.admission'].create({
                'name': f'P2 Student {i}',
                'email': f'p2student{i}@example.com',
                'phone': f'+2{i}{i}{i}{i}{i}{i}{i}{i}{i}',
                'national_id': f'P2-ID{i}',
                'program_id': program2.id,
            })
        
        self.assertEqual(program1.admission_count, 2, 
                        "Program 1 should have 2 admissions")
        self.assertEqual(program2.admission_count, 3, 
                        "Program 2 should have 3 admissions")

    # ==========================================
    # Active Flag / Archiving
    # ==========================================

    def test_archive_program_sets_active_false(self):
        """Test that archiving a program sets active to False"""
        program = self.env['school.program'].create(self.valid_program_data)
        self.assertTrue(program.active)
        
        program.active = False
        
        self.assertFalse(program.active, "Program should be archived")

    def test_search_active_programs_excludes_archived(self):
        """Test that searching for active programs excludes archived ones"""
        active_program = self.env['school.program'].create({
            'name': 'Active Program',
            'active': True,
        })
        
        archived_program = self.env['school.program'].create({
            'name': 'Archived Program',
            'active': False,
        })
        
        # Search only active programs
        active_programs = self.env['school.program'].search([
            ('active', '=', True),
            ('id', 'in', [active_program.id, archived_program.id])
        ])
        
        self.assertIn(active_program, active_programs, 
                     "Active program should be in results")
        self.assertNotIn(archived_program, active_programs, 
                        "Archived program should NOT be in results")

    def test_reactivate_archived_program(self):
        """Test that an archived program can be reactivated"""
        program = self.env['school.program'].create({
            'name': 'Temporarily Archived Program',
            'active': False,
        })
        
        self.assertFalse(program.active)
        
        program.active = True
        
        self.assertTrue(program.active, "Program should be reactivated")

    # ==========================================
    # One2many Relationship
    # ==========================================

    def test_admission_ids_reflects_linked_admissions(self):
        """Test that admission_ids properly reflects linked admission records"""
        program = self.env['school.program'].create(self.valid_program_data)
        
        admission1 = self.env['school.admission'].create({
            'name': 'Student A',
            'email': 'studenta@example.com',
            'phone': '+1111111111',
            'national_id': 'IDA',
            'program_id': program.id,
        })
        
        admission2 = self.env['school.admission'].create({
            'name': 'Student B',
            'email': 'studentb@example.com',
            'phone': '+2222222222',
            'national_id': 'IDB',
            'program_id': program.id,
        })
        
        self.assertEqual(len(program.admission_ids), 2, 
                        "Program should have 2 linked admissions")
        self.assertIn(admission1, program.admission_ids)
        self.assertIn(admission2, program.admission_ids)

    def test_admission_ids_empty_for_new_program(self):
        """Test that a new program has empty admission_ids"""
        program = self.env['school.program'].create(self.valid_program_data)
        
        self.assertEqual(len(program.admission_ids), 0, 
                        "New program should have no admissions")

    def test_changing_admission_program_updates_admission_ids(self):
        """Test that changing an admission's program updates admission_ids"""
        program1 = self.env['school.program'].create({
            'name': 'Original Program',
        })
        program2 = self.env['school.program'].create({
            'name': 'New Program',
        })
        
        admission = self.env['school.admission'].create({
            'name': 'Transferring Student',
            'email': 'transfer@example.com',
            'phone': '+3333333333',
            'national_id': 'IDTRANS',
            'program_id': program1.id,
        })
        
        self.assertIn(admission, program1.admission_ids)
        self.assertNotIn(admission, program2.admission_ids)
        
        # Transfer to program2
        admission.program_id = program2
        
        self.assertNotIn(admission, program1.admission_ids, 
                        "Admission should be removed from original program")
        self.assertIn(admission, program2.admission_ids, 
                     "Admission should be added to new program")

    # ==========================================
    # Ordering
    # ==========================================

    def test_programs_ordered_by_name(self):
        """Test that programs are ordered by name"""
        program_c = self.env['school.program'].create({'name': 'C Program'})
        program_a = self.env['school.program'].create({'name': 'A Program'})
        program_b = self.env['school.program'].create({'name': 'B Program'})
        
        programs = self.env['school.program'].search([
            ('id', 'in', [program_a.id, program_b.id, program_c.id])
        ])
        
        self.assertEqual(programs[0].id, program_a.id, "Should be ordered alphabetically")
        self.assertEqual(programs[1].id, program_b.id)
        self.assertEqual(programs[2].id, program_c.id)