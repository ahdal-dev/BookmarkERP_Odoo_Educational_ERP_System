"""
Quick script to inject test users via Odoo shell
Run with: venv/Scripts/python.exe odoo/odoo-bin shell -c config/odoo.conf -d edu_demo_new < addons/edu_mangment/edu_mang_auth/data/create_users_shell.py
"""

print("Creating test users for Educational ERP...")

# Get groups
try:
    admin_group = env.ref('edu_mang_auth.group_erp_admin')
    student_group = env.ref('edu_mang_auth.group_erp_student')
    officer_group = env.ref('edu_mang_auth.group_erp_admission_officer')
    print("✓ Found all required groups")
except Exception as e:
    print(f"ERROR: Could not find groups. Is edu_mang_auth installed? {e}")
    exit(1)

# Test users to create
users_data = [
    {
        'name': 'Admin Test',
        'login': 'admin@test.com',
        'password': 'admin123',
        'email': 'admin@test.com',
        'group': admin_group,
        'role': 'Admin'
    },
    {
        'name': 'Student Test',
        'login': 'student@test.com',
        'password': 'student123',
        'email': 'student@test.com',
        'group': student_group,
        'role': 'Student'
    },
    {
        'name': 'Admission Officer Test',
        'login': 'officer@test.com',
        'password': 'officer123',
        'email': 'officer@test.com',
        'group': officer_group,
        'role': 'Officer'
    },
    {
        'name': 'John Smith (Admin)',
        'login': 'john.admin',
        'password': 'admin123',
        'email': 'john.admin@university.edu',
        'group': admin_group,
        'role': 'Admin'
    },
    {
        'name': 'Sarah Johnson (Student)',
        'login': 'sarah.student',
        'password': 'student123',
        'email': 'sarah.student@university.edu',
        'group': student_group,
        'role': 'Student'
    },
    {
        'name': 'Michael Brown (Admission Officer)',
        'login': 'michael.officer',
        'password': 'officer123',
        'email': 'michael.officer@university.edu',
        'group': officer_group,
        'role': 'Officer'
    },
]

created = 0
updated = 0

for user_data in users_data:
    login = user_data['login']

    # Check if user exists
    existing_user = env['res.users'].search([('login', '=', login)])

    if existing_user:
        print(f"⟳ Updating existing user: {login} ({user_data['role']})")
        existing_user.write({
            'name': user_data['name'],
            'password': user_data['password'],
            'email': user_data['email'],
            'active': True,
        })
        # Update groups
        existing_user.write({'groups_id': [(6, 0, [user_data['group'].id])]})
        updated += 1
    else:
        print(f"✓ Creating user: {login} ({user_data['role']})")
        user = env['res.users'].create({
            'name': user_data['name'],
            'login': login,
            'password': user_data['password'],
            'email': user_data['email'],
            'active': True,
        })
        # Add group after creation
        user.write({'groups_id': [(6, 0, [user_data['group'].id])]})
        created += 1

env.cr.commit()

print("\n" + "="*60)
print("✓ Test users created successfully!")
print(f"  - Created: {created} users")
print(f"  - Updated: {updated} users")
print("="*60)
print("\nTest Credentials:")
print("  Admin:    admin@test.com / admin123")
print("  Student:  student@test.com / student123")
print("  Officer:  officer@test.com / officer123")
print("\nYou can now log in with these credentials!")
