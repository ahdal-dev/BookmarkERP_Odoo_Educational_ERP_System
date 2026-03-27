# Test Users for Authentication Testing

This file contains credentials for demo users created for testing the Educational ERP authentication system.

## Quick Reference

### Admin Users
| Name | Login | Password | Email |
|------|-------|----------|-------|
| Admin Test | `admin@test.com` | `admin123` | admin@test.com |
| John Smith (Admin) | `john.admin` | `admin123` | john.admin@university.edu |

**Permissions:** Full access to all Educational ERP modules, user management, and system configuration.

### Student Users
| Name | Login | Password | Email |
|------|-------|----------|-------|
| Student Test | `student@test.com` | `student123` | student@test.com |
| Sarah Johnson (Student) | `sarah.student` | `student123` | sarah.student@university.edu |

**Permissions:** Portal access only - can view dashboard, submit petitions, register for courses, and view academic records.

### Admission Officer Users
| Name | Login | Password | Email |
|------|-------|----------|-------|
| Admission Officer Test | `officer@test.com` | `officer123` | officer@test.com |
| Michael Brown (Admission Officer) | `michael.officer` | `officer123` | michael.officer@university.edu |

**Permissions:** Backend access to review applications, manage admissions, and access admission-related data.

## Installation

### Automatic Installation (Recommended)
The demo users are automatically created when you install or upgrade the `edu_mang_auth` module with demo data enabled:

```bash
# Install with demo data
./odoo-bin -d your_database -i edu_mang_auth --load-language=en_US

# Or upgrade the module
./odoo-bin -d your_database -u edu_mang_auth
```

### Manual Installation
If you need to manually inject these users or the automatic installation didn't work, use the provided Python script:

```bash
python addons/edu_mangment/edu_mang_auth/data/inject_users.py
```

## Testing Scenarios

### Test Admin Access
1. Log in with `admin@test.com` / `admin123`
2. Verify you can access:
   - Backend Odoo interface
   - All Educational ERP modules
   - User management
   - System settings

### Test Student Access
1. Log in with `student@test.com` / `student123`
2. Verify you:
   - Are redirected to student dashboard
   - Cannot access backend interface
   - Can view your academic records
   - Can submit petitions/applications

### Test Admission Officer Access
1. Log in with `officer@test.com` / `officer123`
2. Verify you can:
   - Access backend interface
   - View and manage admission applications
   - Cannot access admin-only features

## Security Notes

**⚠️ IMPORTANT:** These users are for **DEVELOPMENT AND TESTING ONLY**.

- Never use these credentials in a production environment
- The `noupdate="1"` flag means these records won't be updated on module upgrade
- Delete or deactivate these users before deploying to production
- All passwords are intentionally simple for testing purposes

## Troubleshooting

### Users not created
- Check that demo data is enabled: `--without-demo=False` (default)
- Verify the module installed successfully
- Check Odoo logs for any errors during installation

### Cannot log in
- Verify the user is active in Settings → Users & Companies → Users
- Check that the user has the correct group assigned
- Try resetting the password through Odoo backend (as admin)

### Permission issues
- Verify the user group in Settings → Users & Companies → Users
- Check the security rules in `security/security.xml`
- Review access rights in `security/ir.model.access.csv`
