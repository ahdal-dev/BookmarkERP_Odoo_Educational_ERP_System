# Educational ERP - Test Data

This directory contains demo/test data for the Educational ERP authentication system.

## Files

- **demo_users.xml** - Odoo XML data file with demo users (automatically loaded)
- **inject_users.py** - Python script for manual user injection
- **TEST_USERS.md** - Complete reference guide with credentials and testing scenarios

## Quick Start

### Option 1: Automatic Installation (Easiest)

Just upgrade the module and the demo users will be created automatically:

```bash
./odoo-bin -d your_database -u edu_mang_auth
```

### Option 2: Manual Script Injection

If automatic installation doesn't work:

```bash
cd addons/edu_mangment/edu_mang_auth/data
python inject_users.py --database your_database
```

### Option 3: Odoo Shell

For more control, use Odoo shell (see TEST_USERS.md for complete instructions).

## Test Credentials

Quick reference for testing:

| Role | Login | Password |
|------|-------|----------|
| Admin | admin@test.com | admin123 |
| Student | student@test.com | student123 |
| Officer | officer@test.com | officer123 |

For complete user list and testing scenarios, see **TEST_USERS.md**.

## Security Warning

⚠️ **These users are for development/testing only!**
- Never use in production
- Delete before deploying to production
- Passwords are intentionally simple for testing

## Need Help?

See TEST_USERS.md for:
- Complete user list
- Testing scenarios
- Troubleshooting guide
- Manual installation instructions
