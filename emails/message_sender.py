import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
 
 
# ─── Configuration ────────────────────────────────────────────────────────────
 
SMTP_HOST = "smtp.gmail.com"       # Gmail: smtp.gmail.com | Outlook: smtp.office365.com
SMTP_PORT = 465                    # 465 for SSL | 587 for TLS/STARTTLS
USE_SSL   = True                   # True for port 465 | False for port 587
 
SENDER_EMAIL    = ""  # Your email address
SENDER_PASSWORD = ""  # Gmail: use an App Password (not your real password)
                                            # Generate one at: myaccount.google.com/apppasswords
 
 
# ─── Recipients ───────────────────────────────────────────────────────────────
 
RECIPIENTS = {
    "Alice Smith":   "alice@example.com",
    "Bob Johnson":   "bob@example.com",
    "Carol Williams":"carol@example.com",
    "Test": "yasef52132@4heats.com"
}
 
 
# ─── Email Content ────────────────────────────────────────────────────────────
 
SUBJECT = "Recibo de nómina {fecha}"
 
# Plain text fallback (shown if recipient's client doesn't support HTML)
TEXT_BODY = """\
Hola {name},
 
Este correo contiene un recibo de nómina para el periodo {fecha}.
 
Atentamente,
SCI - Servicio de Comedores Industriales
"""
 
# HTML body (optional — set to None to send plain text only)
HTML_BODY = """\
<html>
  <body>
    <p>Hola {name},</p>
    <p>Este correo contiene un recibo de nómina para el periodo <strong>{fecha}</strong>.</p>
    <p>Atentamente,<br>SCI - Servicio de Comedores Industriales</p>
  </body>
</html>
"""
 
# Attachments: list of file paths to attach (or leave empty)
ATTACHMENTS = []
# ATTACHMENTS = ["/path/to/file.pdf", "/path/to/image.png"]
 
 
# ─── Core Functions ───────────────────────────────────────────────────────────
 
def build_message(sender: str, recipient_name: str, recipient_email: str) -> MIMEMultipart:
    """Build a MIME email message with optional HTML and attachments."""
    msg = MIMEMultipart("alternative") if not ATTACHMENTS else MIMEMultipart("mixed")
    msg["Subject"] = SUBJECT
    msg["From"]    = sender
    msg["To"]      = recipient_email
 
    # Personalise body text
    plain = TEXT_BODY.format(name=recipient_name)
    msg.attach(MIMEText(plain, "plain"))
 
    if HTML_BODY:
        html = HTML_BODY.format(name=recipient_name)
        msg.attach(MIMEText(html, "html"))
 
    # Attach files
    for filepath in ATTACHMENTS:
        if not os.path.isfile(filepath):
            print(f"  ⚠  Attachment not found, skipping: {filepath}")
            continue
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(filepath)}"')
        msg.attach(part)
 
    return msg
 
 
def send_emails(recipients: dict) -> None:
    """Connect to SMTP server and send emails to all recipients."""
    context = ssl.create_default_context()
 
    try:
        if USE_SSL:
            # Port 465 — SSL from the start
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context)
        else:
            # Port 587 — plain connection upgraded via STARTTLS
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
 
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print(f"✓ Logged in as {SENDER_EMAIL}\n")
 
        success, failed = [], []
 
        for name, email in recipients.items():
            try:
                msg = build_message(SENDER_EMAIL, name, email)
                server.sendmail(SENDER_EMAIL, email, msg.as_string())
                print(f"  ✓ Sent to {name} <{email}>")
                success.append(email)
            except Exception as e:
                print(f"  ✗ Failed for {name} <{email}>: {e}")
                failed.append(email)
 
        server.quit()
 
        print(f"\n─── Summary ───────────────────────────")
        print(f"  Sent:   {len(success)}")
        print(f"  Failed: {len(failed)}")
        if failed:
            print(f"  Failed addresses: {', '.join(failed)}")
 
    except smtplib.SMTPAuthenticationError:
        print("✗ Authentication failed. Check your email/password.")
        print("  Gmail users: enable 2FA and use an App Password.")
        print("  → https://myaccount.google.com/apppasswords")
    except Exception as e:
        print(f"✗ Could not connect to SMTP server: {e}")
 
 
# ─── Entry Point ──────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    send_emails(RECIPIENTS)