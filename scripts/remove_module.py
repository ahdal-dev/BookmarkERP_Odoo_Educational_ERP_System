"""Uninstall an Odoo module by name via odoo-bin shell."""
import sys
import os
import subprocess
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/remove_module.py <module_name> [config_file] [db_name]")
        sys.exit(1)

    module_name = sys.argv[1]
    config_file = sys.argv[2] if len(sys.argv) > 2 else "config/odoo.conf"
    db_name = sys.argv[3] if len(sys.argv) > 3 else "edu_demo_new"

    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', module_name):
        print(f"Error: Invalid module name '{module_name}'")
        sys.exit(1)

    code = (
        f"module = env['ir.module.module'].search("
        f"[('name', '=', '{module_name}'), ('state', '=', 'installed')])\n"
        f"if module:\n"
        f"    module.button_immediate_uninstall()\n"
        f"    print('Module {module_name} uninstalled successfully.')\n"
        f"else:\n"
        f"    print('Module {module_name} is not installed or not found.')\n"
    )

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
