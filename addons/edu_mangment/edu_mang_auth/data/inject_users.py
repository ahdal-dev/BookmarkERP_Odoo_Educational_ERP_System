#!/usr/bin/env python3
"""
Manual User Injection Script for Educational ERP
================================================

This script manually creates test users for each role in the Educational ERP system.
Use this if the demo data installation doesn't work or if you need to recreate the users.

Usage:
    python inject_users.py --database YOUR_DB_NAME [--odoo-path /path/to/odoo]

Requirements:
    - Odoo instance must be accessible
    - Database must exist
    - edu_mang_auth module must be installed
"""

import sys
import argparse
import os

try:
    import odoorpc
    ODOORPC_AVAILABLE = True
except ImportError:
    ODOORPC_AVAILABLE = False


def inject_users_odoorpc(host='localhost', port=8069, database=None, admin_user='admin', admin_password='admin'):
    """Inject users using OdooRPC library"""
    if not ODOORPC_AVAILABLE:
        print("ERROR: odoorpc library not found. Install it with: pip install odoorpc")
        return False

    print(f"Connecting to Odoo at {host}:{port}...")
    odoo = odoorpc.ODOO(host, port=port)

    try:
        odoo.login(database, admin_user, admin_password)
        print(f"✓ Connected to database '{database}'")
    except Exception as e:
        print(f"ERROR: Could not connect to Odoo: {e}")
        return False

    Users = odoo.env['res.users']
    Groups = odoo.env['res.groups']

    # Get group IDs
    try:
        group_admin = Groups.search([('name', '=', 'Educational ERP - Administrator')])[0]
        group_student = Groups.search([('name', '=', 'Educational ERP - Student')])[0]
        group_officer = Groups.search([('name', '=', 'Educational ERP - Admission Officer')])[0]
        print("✓ Found all required groups")
    except Exception as e:
        print(f"ERROR: Could not find required groups. Make sure edu_mang_auth is installed: {e}")
        return False

    # Define test users
    test_users = [
        {
            'name': 'Admin Test',
            'login': 'admin@test.com',
            'password': 'admin123',
            'email': 'admin@test.com',
            'groups_id': [(4, group_admin)],
        },
        {
            'name': 'Student Test',
            'login': 'student@test.com',
            'password': 'student123',
            'email': 'student@test.com',
            'groups_id': [(4, group_student)],
        },
        {
            'name': 'Admission Officer Test',
            'login': 'officer@test.com',
            'password': 'officer123',
            'email': 'officer@test.com',
            'groups_id': [(4, group_officer)],
        },
        {
            'name': 'John Smith (Admin)',
            'login': 'john.admin',
            'password': 'admin123',
            'email': 'john.admin@university.edu',
            'groups_id': [(4, group_admin)],
        },
        {
            'name': 'Sarah Johnson (Student)',
            'login': 'sarah.student',
            'password': 'student123',
            'email': 'sarah.student@university.edu',
            'groups_id': [(4, group_student)],
        },
        {
            'name': 'Michael Brown (Admission Officer)',
            'login': 'michael.officer',
            'password': 'officer123',
            'email': 'michael.officer@university.edu',
            'groups_id': [(4, group_officer)],
        },
    ]

    created_count = 0
    updated_count = 0

    for user_data in test_users:
        login = user_data['login']

        # Check if user already exists
        existing_user = Users.search([('login', '=', login)])

        if existing_user:
            print(f"⟳ Updating existing user: {login}")
            Users.write(existing_user, user_data)
            updated_count += 1
        else:
            print(f"✓ Creating user: {login}")
            Users.create(user_data)
            created_count += 1

    print(f"\n{'='*60}")
    print(f"✓ Injection complete!")
    print(f"  - Created: {created_count} users")
    print(f"  - Updated: {updated_count} users")
    print(f"{'='*60}\n")

    return True


def print_manual_instructions():
    """Print manual SQL instructions if automatic injection fails"""
    print("\n" + "="*60)
    print("MANUAL INSTALLATION VIA ODOO SHELL")
    print("="*60)
    print("\nIf the automatic injection doesn't work, you can use Odoo shell:\n")
    print("1. Start Odoo shell:")
    print("   ./odoo-bin shell -d YOUR_DATABASE\n")
    print("2. Run this Python code:\n")
    print("""
# Get groups
admin_group = env.ref('edu_mang_auth.group_erp_admin')
student_group = env.ref('edu_mang_auth.group_erp_student')
officer_group = env.ref('edu_mang_auth.group_erp_admission_officer')

# Create users
env['res.users'].create({
    'name': 'Admin Test',
    'login': 'admin@test.com',
    'password': 'admin123',
    'email': 'admin@test.com',
    'groups_id': [(4, admin_group.id)],
})

env['res.users'].create({
    'name': 'Student Test',
    'login': 'student@test.com',
    'password': 'student123',
    'email': 'student@test.com',
    'groups_id': [(4, student_group.id)],
})

env['res.users'].create({
    'name': 'Admission Officer Test',
    'login': 'officer@test.com',
    'password': 'officer123',
    'email': 'officer@test.com',
    'groups_id': [(4, officer_group.id)],
})

env.cr.commit()
print("Users created successfully!")
""")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Inject test users into Educational ERP system'
    )
    parser.add_argument(
        '--database', '-d',
        required=True,
        help='Odoo database name'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Odoo host (default: localhost)'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8069,
        help='Odoo port (default: 8069)'
    )
    parser.add_argument(
        '--admin-user',
        default='admin',
        help='Admin username (default: admin)'
    )
    parser.add_argument(
        '--admin-password',
        default='admin',
        help='Admin password (default: admin)'
    )
    parser.add_argument(
        '--manual',
        action='store_true',
        help='Show manual installation instructions instead of automatic injection'
    )

    args = parser.parse_args()

    if args.manual:
        print_manual_instructions()
        return 0

    print("="*60)
    print("Educational ERP - Test User Injection Script")
    print("="*60)
    print()

    success = inject_users_odoorpc(
        host=args.host,
        port=args.port,
        database=args.database,
        admin_user=args.admin_user,
        admin_password=args.admin_password
    )

    if not success:
        print("\nAutomatic injection failed. Use --manual flag for instructions.")
        print_manual_instructions()
        return 1

    print("\nTest Users Created! Login credentials:\n")
    print("Admin:")
    print("  - admin@test.com / admin123")
    print("  - john.admin / admin123\n")
    print("Student:")
    print("  - student@test.com / student123")
    print("  - sarah.student / student123\n")
    print("Admission Officer:")
    print("  - officer@test.com / officer123")
    print("  - michael.officer / officer123\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
