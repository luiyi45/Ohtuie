import os
import httpx
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings

# Setup Jinja2 environment
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))

async def send_password_recovery_email(email_to: str, full_name: str, code: str):
    template = env.get_template("password_recovery.html")
    html_content = template.render(
        user_full_name=full_name,
        recovery_code=code
    )
    
    # Debug info for API Key (secure)
    key_len = len(settings.BREVO_API_KEY)
    key_mask = f"{settings.BREVO_API_KEY[:4]}...{settings.BREVO_API_KEY[-4:]}" if key_len > 8 else "***"
    print(f"DEBUG: Attempting to send email via Brevo. API Key length: {key_len}, Mask: {key_mask}")

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "sender": {"name": settings.EMAILS_FROM_NAME, "email": settings.EMAILS_FROM_EMAIL},
        "to": [{"email": email_to}],
        "subject": "Código de recuperación - OHTUIE",
        "htmlContent": html_content
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
        if response.status_code in [200, 201, 202]:
            print(f"DEBUG: Email sent successfully via Brevo to {email_to}")
            return True
        else:
            print(f"ERROR: Brevo API error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to send email via Brevo to {email_to}: {e}")
        return False

async def send_account_deletion_warning_email(email_to: str, full_name: str):
    template = env.get_template("account_deletion.html")
    html_content = template.render(
        user_full_name=full_name
    )
    
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "sender": {"name": settings.EMAILS_FROM_NAME, "email": settings.EMAILS_FROM_EMAIL},
        "to": [{"email": email_to}],
        "subject": "Solicitud de Eliminación de Cuenta - OHTUIE",
        "htmlContent": html_content
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
        if response.status_code in [200, 201, 202]:
            return True
        else:
            print(f"ERROR: Brevo API error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Failed to send email via Brevo to {email_to}: {e}")
        return False
