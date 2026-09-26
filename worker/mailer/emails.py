import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from settings import settings
from notification.models import NotificationEvent
from mailer.email_builders.email_registry import BUILDERS


def _send_via_smtp(recipients: list[str], subject: str, html: str) -> None:
    if "\n" in subject or "\r" in subject:
        raise ValueError("Email subject cannot contain newline characters")

    tls_context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:

        smtp.starttls(context=tls_context)
        smtp.login(settings.smtp_email, settings.smtp_app_password)

        for recipient in recipients:
            message = EmailMessage()
            message["From"] = settings.smtp_email
            message["To"] = recipient
            message["Subject"] = subject
            message.set_content(
                f"Nowe powiadomienie: {subject}\n"
                "Otwórz wiadomość w kliencie obsługującym HTML, aby zobaczyć szczegóły."
            )
            message.add_alternative(html, subtype="html")
            smtp.send_message(message)


async def send_notification_email(
    emails: list[str], notification: NotificationEvent
) -> None:
    builder = BUILDERS.get(notification.payload.event_type)
    if builder is None:
        raise ValueError(
            f"No email builder registered for {notification.payload.event_type}"
        )
    email = builder.build(notification)
    await asyncio.to_thread(_send_via_smtp, emails, email.subject, email.html)
