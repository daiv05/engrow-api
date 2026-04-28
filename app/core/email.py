import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings


def send_reset_email(to_email: str, reset_link: str) -> None:
    """Send a password reset email via SMTP. Silently skips if SMTP is not configured."""
    if not settings.smtp_user or not settings.smtp_password:
        # Dev mode: print the link to console instead of sending
        print(f"[DEV] Password reset link for {to_email}: {reset_link}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Restablecer contraseña — Engrow"
    msg["From"] = settings.from_email
    msg["To"] = to_email

    plain = f"Hola,\n\nHaz clic en este enlace para restablecer tu contraseña:\n{reset_link}\n\nEste enlace expira en 60 minutos.\n\nSi no solicitaste esto, ignora este mensaje."
    html = f"""
    <html><body>
    <p>Hola,</p>
    <p>Haz clic en el siguiente enlace para restablecer tu contraseña:</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    <p>Este enlace expira en 60 minutos.</p>
    <p>Si no solicitaste esto, ignora este mensaje.</p>
    </body></html>
    """

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
