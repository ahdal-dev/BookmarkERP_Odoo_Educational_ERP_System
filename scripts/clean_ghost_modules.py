"""Clean orphaned modules and ghost models from the Odoo database.

Usage:
    python scripts/clean_ghost_modules.py [config_file] [db_name]
"""
import sys
import os
import subprocess

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config/odoo.conf"
    db_name = sys.argv[2] if len(sys.argv) > 2 else "edu_demo_new"

    # Modules to clean (code was removed but DB still references them)
    ghost_modules = ['education_management']

    # Ghost models (from removed modules, no longer in any addon)
    ghost_models = [
        'education.student',
        'education.teacher',
        'education.course',
        'education.enrollment',
    ]

    code_lines = []

    # Uninstall ghost modules from DB
    for mod in ghost_modules:
        code_lines.append(
            f"m = env['ir.module.module'].search([('name', '=', '{mod}')])\n"
            f"if m:\n"
            f"    if m.state == 'installed':\n"
            f"        m.button_immediate_uninstall()\n"
            f"        print(f'Uninstalled module: {mod}')\n"
            f"    else:\n"
            f"        m.write({{'state': 'uninstalled'}})\n"
            f"        print(f'Marked module {mod} as uninstalled (was {{m.state}})')\n"
            f"else:\n"
            f"    print(f'Module {mod} not found in DB')\n"
        )

    # Clean ghost model references from ir_model
    for model_name in ghost_models:
        code_lines.append(
            f"recs = env['ir.model'].search([('model', '=', '{model_name}')])\n"
            f"if recs:\n"
            f"    # Remove related data, fields, access rules first\n"
            f"    env['ir.model.data'].search([('model', '=', 'ir.model'), ('res_id', 'in', recs.ids)]).unlink()\n"
            f"    env['ir.model.fields'].search([('model_id', 'in', recs.ids)]).unlink()\n"
            f"    env['ir.model.access'].search([('model_id', 'in', recs.ids)]).unlink()\n"
            f"    env.cr.execute(\"DELETE FROM ir_model WHERE model = '{model_name}'\")\n"
            f"    print(f'Cleaned ghost model: {model_name}')\n"
            f"else:\n"
            f"    print(f'Model {model_name} not found in DB')\n"
        )

    code_lines.append("env.cr.commit()\n")
    code_lines.append("print('\\nDone! Restart Odoo to verify.')\n")

    code = "\n".join(code_lines)

    root_dir = os.path.join(os.path.dirname(__file__), "..")
    odoo_bin = os.path.join(root_dir, "odoo", "odoo-bin")

    result = subprocess.run(
        [sys.executable, odoo_bin, "shell", "-c", config_file, "-d", db_name, "--no-http"],
        input=code.encode(),
        cwd=root_dir,
    )
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
