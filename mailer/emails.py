
import resend
from settings import settings
from notification.models import NotificationEvent
from mailer.email_builders.email_registry import BUILDERS

resend.api_key = settings.resend_api_key

async def send_notification_email(
    emails: list[str], notification: NotificationEvent
) -> None:

    builder = BUILDERS.get(notification.payload.event_type)
    if builder is None:
        raise ValueError(f"No email builder registered for {notification.payload.event_type}")
    email = builder.build(notification)

    params = [
        {
            "from": "onboarding@resend.dev",
            "to": [recipient],
            "subject": mailer.subject,
            "html": mailer.html,
        }
        for recipient in emails
    ]
    for patch_index in range(0, len(params), 100):
        await resend.Batch.send_async(params[patch_index: patch_index + 100])

