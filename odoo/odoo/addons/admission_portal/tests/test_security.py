# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError


class TestAdmissionSecurity(TransactionCase):
    """Test suite for admission_portal security and access rights"""

    @classmethod
    def setUpClass(cls):
        super(TestAdmissionSecurity, cls).setUpClass()
        
        # Create test program
        cls.program = cls.env['school.program'].create({
            'name': 'Security Test Program',
            'code': 'SEC101',
        })
        
        # Create users with different access levels
        cls.public_user = cls.env.ref('base.public_user')
        
        cls.portal_user = cls.env['res.users'].create({
            'name': 'Portal User',
            'login': 'portal_user',
            'email': 'portal@example.com',
            'group_ids': [(6, 0, [cls.env.ref('base.group_portal').id])]
        })
        
        cls.internal_user = cls.env['res.users'].create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'internal@example.com',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
        
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager_user',
            'email': 'manager@example.com',
            'group_ids': [(6, 0, [cls.env.ref('base.group_system').id])]
        })
        
        # Create a test admission record
        cls.test_admission = cls.env['school.admission'].create({
            'name': 'Security Test Student',
            'email': 'security@example.com',
            'phone': '+1234567890',
            'national_id': 'SEC-ID-001',
            'program_id': cls.program.id,
        })

    # ==========================================
    # school.admission - Public User
    # ==========================================

    def test_public_user_can_read_admission(self):
        """Test that public user can read school.admission"""
        admission_as_public = self.test_admission.with_user(self.public_user)
        
        # Should be able to read
        name = admission_as_public.name
        self.assertEqual(name, 'Security Test Student', 
                        "Public user should be able to read admission")

    def test_public_user_can_create_admission(self):
        """Test that public user can create school.admission"""
        admission = self.env['school.admission'].with_user(self.public_user).create({
            'name': 'Public Created',
            'email': 'public@example.com',
            'phone': '+1111111111',
            'national_id': 'PUB-ID',
            'program_id': self.program.id,
        })
        
        self.assertTrue(admission.id, "Public user should be able to create admission")

    def test_public_user_cannot_write_admission(self):
        """Test that public user cannot write/update school.admission"""
        admission_as_public = self.test_admission.with_user(self.public_user)
        
        with self.assertRaises(AccessError, msg="Public user should NOT be able to write"):
            admission_as_public.write({'name': 'Changed Name'})

    def test_public_user_cannot_unlink_admission(self):
        """Test that public user cannot unlink/delete school.admission"""
        admission = self.env['school.admission'].create({
            'name': 'To Delete',
            'email': 'delete@example.com',
            'phone': '+9999999999',
            'national_id': 'DEL-ID',
            'program_id': self.program.id,
        })
        
        admission_as_public = admission.with_user(self.public_user)
        
        with self.assertRaises(AccessError, msg="Public user should NOT be able to unlink"):
            admission_as_public.unlink()

    # ==========================================
    # school.admission - Portal User
    # ==========================================

    def test_portal_user_can_read_admission(self):
        """Test that portal user can read school.admission"""
        admission_as_portal = self.test_admission.with_user(self.portal_user)
        
        name = admission_as_portal.name
        self.assertEqual(name, 'Security Test Student', 
                        "Portal user should be able to read admission")

    def test_portal_user_can_create_admission(self):
        """Test that portal user can create school.admission"""
        admission = self.env['school.admission'].with_user(self.portal_user).create({
            'name': 'Portal Created',
            'email': 'portal_create@example.com',
            'phone': '+2222222222',
            'national_id': 'PORT-ID',
            'program_id': self.program.id,
        })
        
        self.assertTrue(admission.id, "Portal user should be able to create admission")

    def test_portal_user_cannot_write_admission(self):
        """Test that portal user cannot write school.admission"""
        admission_as_portal = self.test_admission.with_user(self.portal_user)
        
        with self.assertRaises(AccessError, msg="Portal user should NOT be able to write"):
            admission_as_portal.write({'name': 'Changed by Portal'})

    def test_portal_user_cannot_unlink_admission(self):
        """Test that portal user cannot unlink school.admission"""
        admission = self.env['school.admission'].create({
            'name': 'Portal Delete Test',
            'email': 'portaldelete@example.com',
            'phone': '+8888888888',
            'national_id': 'PDEL-ID',
            'program_id': self.program.id,
        })
        
        admission_as_portal = admission.with_user(self.portal_user)
        
        with self.assertRaises(AccessError, msg="Portal user should NOT be able to unlink"):
            admission_as_portal.unlink()

    # ==========================================
    # school.admission - Internal User
    # ==========================================

    def test_internal_user_can_read_admission(self):
        """Test that internal user can read school.admission"""
        admission_as_internal = self.test_admission.with_user(self.internal_user)
        
        name = admission_as_internal.name
        self.assertEqual(name, 'Security Test Student', 
                        "Internal user should be able to read admission")

    def test_internal_user_can_write_admission(self):
        """Test that internal user can write school.admission"""
        admission_as_internal = self.test_admission.with_user(self.internal_user)
        
        admission_as_internal.write({'name': 'Updated by Internal'})
        self.assertEqual(admission_as_internal.name, 'Updated by Internal', 
                        "Internal user should be able to write admission")

    def test_internal_user_can_create_admission(self):
        """Test that internal user can create school.admission"""
        admission = self.env['school.admission'].with_user(self.internal_user).create({
            'name': 'Internal Created',
            'email': 'internal_create@example.com',
            'phone': '+3333333333',
            'national_id': 'INT-ID',
            'program_id': self.program.id,
        })
        
        self.assertTrue(admission.id, "Internal user should be able to create admission")

    def test_internal_user_cannot_unlink_admission(self):
        """Test that internal user cannot unlink school.admission"""
        admission = self.env['school.admission'].create({
            'name': 'Internal Delete Test',
            'email': 'internaldelete@example.com',
            'phone': '+7777777777',
            'national_id': 'IDEL-ID',
            'program_id': self.program.id,
        })
        
        admission_as_internal = admission.with_user(self.internal_user)
        
        with self.assertRaises(AccessError, msg="Internal user should NOT be able to unlink"):
            admission_as_internal.unlink()

    # ==========================================
    # school.admission - Manager User
    # ==========================================

    def test_manager_can_read_admission(self):
        """Test that manager can read school.admission"""
        admission_as_manager = self.test_admission.with_user(self.manager_user)
        
        name = admission_as_manager.name
        self.assertEqual(name, 'Security Test Student', 
                        "Manager should be able to read admission")

    def test_manager_can_write_admission(self):
        """Test that manager can write school.admission"""
        admission_as_manager = self.test_admission.with_user(self.manager_user)
        
        admission_as_manager.write({'name': 'Updated by Manager'})
        self.assertEqual(admission_as_manager.name, 'Updated by Manager', 
                        "Manager should be able to write admission")

    def test_manager_can_create_admission(self):
        """Test that manager can create school.admission"""
        admission = self.env['school.admission'].with_user(self.manager_user).create({
            'name': 'Manager Created',
            'email': 'manager_create@example.com',
            'phone': '+4444444444',
            'national_id': 'MGR-ID',
            'program_id': self.program.id,
        })
        
        self.assertTrue(admission.id, "Manager should be able to create admission")

    def test_manager_can_unlink_admission(self):
        """Test that manager can unlink school.admission"""
        admission = self.env['school.admission'].create({
            'name': 'Manager Delete Test',
            'email': 'managerdelete@example.com',
            'phone': '+6666666666',
            'national_id': 'MDEL-ID',
            'program_id': self.program.id,
        })
        
        admission_as_manager = admission.with_user(self.manager_user)
        admission_as_manager.unlink()
        
        # Verify it's deleted
        exists = self.env['school.admission'].search_count([('id', '=', admission.id)])
        self.assertEqual(exists, 0, "Manager should be able to unlink admission")

    # ==========================================
    # school.program - Public User
    # ==========================================

    def test_public_user_can_read_program(self):
        """Test that public user can read school.program"""
        program_as_public = self.program.with_user(self.public_user)
        
        name = program_as_public.name
        self.assertEqual(name, 'Security Test Program', 
                        "Public user should be able to read program")

    def test_public_user_cannot_create_program(self):
        """Test that public user cannot create school.program"""
        with self.assertRaises(AccessError, msg="Public user should NOT be able to create program"):
            self.env['school.program'].with_user(self.public_user).create({
                'name': 'Public Program',
            })

    def test_public_user_cannot_write_program(self):
        """Test that public user cannot write school.program"""
        program_as_public = self.program.with_user(self.public_user)
        
        with self.assertRaises(AccessError, msg="Public user should NOT be able to write program"):
            program_as_public.write({'name': 'Changed Program'})

    def test_public_user_cannot_unlink_program(self):
        """Test that public user cannot unlink school.program"""
        program = self.env['school.program'].create({'name': 'To Delete Program'})
        program_as_public = program.with_user(self.public_user)
        
        with self.assertRaises(AccessError, msg="Public user should NOT be able to unlink program"):
            program_as_public.unlink()

    # ==========================================
    # school.program - Portal User
    # ==========================================

    def test_portal_user_can_read_program(self):
        """Test that portal user can read school.program"""
        program_as_portal = self.program.with_user(self.portal_user)
        
        name = program_as_portal.name
        self.assertEqual(name, 'Security Test Program', 
                        "Portal user should be able to read program")

    def test_portal_user_cannot_create_program(self):
        """Test that portal user cannot create school.program"""
        with self.assertRaises(AccessError, msg="Portal user should NOT be able to create program"):
            self.env['school.program'].with_user(self.portal_user).create({
                'name': 'Portal Program',
            })

    def test_portal_user_cannot_write_program(self):
        """Test that portal user cannot write school.program"""
        program_as_portal = self.program.with_user(self.portal_user)
        
        with self.assertRaises(AccessError, msg="Portal user should NOT be able to write program"):
            program_as_portal.write({'name': 'Portal Changed'})

    def test_portal_user_cannot_unlink_program(self):
        """Test that portal user cannot unlink school.program"""
        program = self.env['school.program'].create({'name': 'Portal Delete Program'})
        program_as_portal = program.with_user(self.portal_user)
        
        with self.assertRaises(AccessError, msg="Portal user should NOT be able to unlink program"):
            program_as_portal.unlink()

    # ==========================================
    # school.program - Internal User
    # ==========================================

    def test_internal_user_can_read_program(self):
        """Test that internal user can read school.program"""
        program_as_internal = self.program.with_user(self.internal_user)
        
        name = program_as_internal.name
        self.assertEqual(name, 'Security Test Program', 
                        "Internal user should be able to read program")

    def test_internal_user_can_write_program(self):
        """Test that internal user can write school.program"""
        program_as_internal = self.program.with_user(self.internal_user)
        
        program_as_internal.write({'description': 'Updated description'})
        self.assertEqual(program_as_internal.description, 'Updated description', 
                        "Internal user should be able to write program")

    def test_internal_user_can_create_program(self):
        """Test that internal user can create school.program"""
        program = self.env['school.program'].with_user(self.internal_user).create({
            'name': 'Internal Program',
        })
        
        self.assertTrue(program.id, "Internal user should be able to create program")

    def test_internal_user_cannot_unlink_program(self):
        """Test that internal user cannot unlink school.program"""
        program = self.env['school.program'].create({'name': 'Internal Delete Program'})
        program_as_internal = program.with_user(self.internal_user)
        
        with self.assertRaises(AccessError, msg="Internal user should NOT be able to unlink program"):
            program_as_internal.unlink()

    # ==========================================
    # school.program - Manager User
    # ==========================================

    def test_manager_can_read_program(self):
        """Test that manager can read school.program"""
        program_as_manager = self.program.with_user(self.manager_user)
        
        name = program_as_manager.name
        self.assertEqual(name, 'Security Test Program', 
                        "Manager should be able to read program")

    def test_manager_can_write_program(self):
        """Test that manager can write school.program"""
        program_as_manager = self.program.with_user(self.manager_user)
        
        program_as_manager.write({'code': 'MGR-UPDATED'})
        self.assertEqual(program_as_manager.code, 'MGR-UPDATED', 
                        "Manager should be able to write program")

    def test_manager_can_create_program(self):
        """Test that manager can create school.program"""
        program = self.env['school.program'].with_user(self.manager_user).create({
            'name': 'Manager Program',
        })
        
        self.assertTrue(program.id, "Manager should be able to create program")

    def test_manager_can_unlink_program(self):
        """Test that manager can unlink school.program"""
        program = self.env['school.program'].create({'name': 'Manager Delete Program'})
        program_as_manager = program.with_user(self.manager_user)
        
        program_as_manager.unlink()
        
        # Verify deletion
        exists = self.env['school.program'].search_count([('id', '=', program.id)])
        self.assertEqual(exists, 0, "Manager should be able to unlink program")