import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    
    # Create Message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Código de recuperación - OHTUIE"
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.SMTP_USER}>"
    message["To"] = email_to
    
    part = MIMEText(html_content, "html")
    message.attach(part)
    
    try:
        # Connect and send
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email_to, message.as_string())
        
        print(f"DEBUG: Email sent successfully to {email_to}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email to {email_to}: {e}")
        return False
