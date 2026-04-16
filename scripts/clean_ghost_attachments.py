"""Clean ghost attachments from the Odoo database.

Removes attachments that reference non-existent files in the filestore.
Usage:
    python scripts/clean_ghost_attachments.py [config_file] [db_name]
"""
import sys
import os
import subprocess

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config/odoo.conf"
    db_name = sys.argv[2] if len(sys.argv) > 2 else "edu_demo_new"

    # Run a Python script in Odoo context to clean attachments
    code = '''
import os
from odoo import api, SUPERUSER_ID
from odoo.tools import config

env = api.Environment(cr, SUPERUSER_ID, {})
filestore_path = config.filestore(db_name)

attachments = env['ir.attachment'].search([('store_fname', '!=', False)])
missing_count = 0

for attachment in attachments:
    file_path = os.path.join(filestore_path, attachment.store_fname)
    if not os.path.exists(file_path):
        print(f"Removing ghost attachment: {attachment.name} (id: {attachment.id}, path: {file_path})")
        attachment.unlink()
        missing_count += 1

print(f"Removed {missing_count} ghost attachments")
'''

    # Run the code using odoo shell
    cmd = [
        "python", "../odoo/odoo-bin",
        "--config", "../config/odoo.conf",
        "--database", db_name,
        "shell",
        "-c", code
    ]

    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))

    if result.returncode == 0:
        print("Success:")
        print(result.stdout)
    else:
        print("Error:")
        print(result.stderr)

if __name__ == "__main__":
    main()