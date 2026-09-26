from unittest.mock import AsyncMock, MagicMock

import pytest

from mailer import emails
from notification.models import NotificationEvent


@pytest.fixture
def assignment_notification() -> NotificationEvent:
    return NotificationEvent(
        eventId="550e8400-e29b-41d4-a716-446655440000",
        courseId="course-1",
        userIds=["student-1"],
        payload={
            "eventType": "assignment_creation",
            "assignmentTitle": "Sortowanie przez scalanie",
            "courseTitle": "Algorytmy i Struktury Danych",
            "assignmentUrlPath": "https://example.edu/tasks/merge-sort",
            "professorName": "Jan Kowalski",
            "assignmentDeadline": "2026-10-02T16:25:00+02:00",
        },
        sentAt="2026-09-25T18:25:32+02:00",
    )


def test_send_via_smtp_uses_tls_and_sends_separate_messages(mocker):
    smtp = MagicMock()
    smtp_factory = mocker.patch("mailer.emails.smtplib.SMTP")
    smtp_factory.return_value.__enter__.return_value = smtp

    mocker.patch.object(emails.settings, "smtp_email", "sender@gmail.com")
    mocker.patch.object(emails.settings, "smtp_app_password", "app-password")
    mocker.patch.object(emails.settings, "smtp_host", "smtp.gmail.com")
    mocker.patch.object(emails.settings, "smtp_port", 587)

    emails._send_via_smtp(
        ["first@example.com", "second@example.com"],
        "Test subject",
        "<strong>Test body</strong>",
    )

    smtp_factory.assert_called_once_with("smtp.gmail.com", 587, timeout=30)
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with("sender@gmail.com", "app-password")
    assert smtp.send_message.call_count == 2

    first_message = smtp.send_message.call_args_list[0].args[0]
    second_message = smtp.send_message.call_args_list[1].args[0]
    assert first_message["To"] == "first@example.com"
    assert second_message["To"] == "second@example.com"
    assert first_message["Subject"] == "Test subject"


@pytest.mark.parametrize("subject", ["line one\nline two", "line one\rline two"])
def test_send_via_smtp_rejects_newlines_in_subject(subject):
    with pytest.raises(ValueError, match="cannot contain newline"):
        emails._send_via_smtp(["student@example.com"], subject, "<p>Body</p>")


async def test_send_notification_email_renders_jinja_and_offloads_smtp(
    assignment_notification, mocker
):
    to_thread = mocker.patch("mailer.emails.asyncio.to_thread", new=AsyncMock())

    await emails.send_notification_email(
        ["first@example.com", "second@example.com"], assignment_notification
    )

    to_thread.assert_awaited_once()
    smtp_function, recipients, subject, html = to_thread.await_args.args
    assert smtp_function is emails._send_via_smtp
    assert recipients == ["first@example.com", "second@example.com"]
    assert "\n" not in subject
    assert "Algorytmy i Struktury Danych" in subject
    assert "Sortowanie przez scalanie" in html
    assert "Jan Kowalski" in html
    assert "https://example.edu/tasks/merge-sort" in html


def test_send_via_smtp_propagates_authentication_failure(mocker):
    smtp = MagicMock()
    smtp.login.side_effect = emails.smtplib.SMTPAuthenticationError(
        535, b"Authentication failed"
    )
    smtp_factory = mocker.patch("mailer.emails.smtplib.SMTP")
    smtp_factory.return_value.__enter__.return_value = smtp

    with pytest.raises(emails.smtplib.SMTPAuthenticationError):
        emails._send_via_smtp(
            ["student@example.com"], "Test subject", "<p>Test body</p>"
        )

    smtp.send_message.assert_not_called()
