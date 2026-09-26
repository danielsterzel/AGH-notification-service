from typing import Protocol
from mailer.models import Email

from notification.models import NotificationEvent


class EmailBuilder(Protocol):
    def build(self, notification: NotificationEvent) -> Email: ...
