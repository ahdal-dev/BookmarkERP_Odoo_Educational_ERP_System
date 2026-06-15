import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))
from Backend.admin_auth import send_email

send_email(
    to_email="noureqomohamed13+test2@gmail.com",
    subject="Test email",
    html_body="<h1>This is a test email</h1>"
)
