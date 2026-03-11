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
        # Try port 465 (SSL) first as configured
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, email_to, message.as_string())
        else:
            # Try port 587 (STARTTLS) or others
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, email_to, message.as_string())
        
        print(f"DEBUG: Email sent successfully to {email_to}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email to {email_to} on port {settings.SMTP_PORT}: {e}")
        # Fallback to port 587 if 465 failed and vice versa (common issue)
        try:
            fallback_port = 587 if settings.SMTP_PORT == 465 else 465
            print(f"DEBUG: Attempting fallback to port {fallback_port}")
            if fallback_port == 465:
                # This check is just for safety, usually fallback is to 587
                with smtplib.SMTP_SSL(settings.SMTP_HOST, 465, timeout=15) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_USER, email_to, message.as_string())
            else:
                with smtplib.SMTP(settings.SMTP_HOST, 587, timeout=15) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_USER, email_to, message.as_string())
            print(f"DEBUG: Fallback email sent successfully to {email_to}")
            return True
        except Exception as fallback_e:
            print(f"ERROR: Fallback also failed: {fallback_e}")
            return False
