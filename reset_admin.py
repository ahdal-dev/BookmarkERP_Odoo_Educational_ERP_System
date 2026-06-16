admin_user = env['res.users'].search([('login', '=', 'admin')], limit=1)
if admin_user:
    admin_user.password = 'admin'
    print("SUCCESS: Admin password reset to 'admin'")
else:
    print("ERROR: Admin user not found!")

test_user = env['res.users'].search([('login', '=', 'admin@test.com')], limit=1)
if test_user:
    print("SUCCESS: admin@test.com exists! Setting password to admin123")
    test_user.password = 'admin123'
else:
    print("WARNING: admin@test.com does not exist.")

env.cr.commit()
