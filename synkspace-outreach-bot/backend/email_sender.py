"""
Zoho SMTP email sender using aiosmtplib.
"""

import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from config import get_settings


class EmailSender:
    """Sends HTML emails via Zoho SMTP."""

    async def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
    ) -> None:
        settings = get_settings()

        if not settings.zoho_email or not settings.zoho_password:
            raise ValueError(
                "Zoho SMTP credentials are not configured. "
                "Set ZOHO_EMAIL and ZOHO_PASSWORD in your .env file."
            )

        message = MIMEMultipart("alternative")
        message["From"] = settings.zoho_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()

        await aiosmtplib.send(
            message,
            hostname=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.zoho_email,
            password=settings.zoho_password,
            start_tls=True,
            tls_context=context,
        )


email_sender = EmailSender()
