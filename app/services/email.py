import os
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings

# Setup Jinja2 environment
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))

def send_password_recovery_email(email_to: str, full_name: str, code: str):
    template = env.get_template("password_recovery.html")
    html_content = template.render(
        user_full_name=full_name,
        recovery_code=code
    )
    
    # MOCK: In a real app, you would use a library like fastapi-mail or smtplib
    print(f"DEBUG: Sending email to {email_to}")
    print(f"DEBUG: Content excerpt: ...{full_name}, your code is {code}...")
    
    # Save to a file for verification during development
    with open(f"recovery_email_{email_to}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return True
