import pytest
from pydantic import ValidationError

from notification.models import (
    AssignmentCreationPayload,
    NotificationEvent,
    NotificationEventType,
)


def test_assignment_creation_payload_accepts_camel_case_fields():
    payload = AssignmentCreationPayload(
        eventType="assignment_creation",
        assignmentTitle="Zadanie testowe",
        courseTitle="Algorytmy",
        assignmentUrlPath="https://example.edu/task",
        professorName="Jan Kowalski",
        assignmentDeadline="2026-10-02T16:25:00+02:00",
    )

    assert payload.event_type is NotificationEventType.ASSIGNMENT_CREATION
    assert payload.assignment_title == "Zadanie testowe"
    assert str(payload.assignment_url_path) == "https://example.edu/task"


def test_notification_rejects_blank_user_id():
    with pytest.raises(ValidationError, match="non-empty strings"):
        NotificationEvent(
            eventId="550e8400-e29b-41d4-a716-446655440000",
            courseId="course-1",
            userIds=["   "],
            payload={
                "eventType": "grade_return",
                "assignmentTitle": "Zadanie testowe",
                "courseTitle": "Algorytmy",
            },
        )


def test_payload_rejects_unknown_fields():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        AssignmentCreationPayload(
            eventType="assignment_creation",
            assignmentTitle="Zadanie testowe",
            courseTitle="Algorytmy",
            professorName="Jan Kowalski",
            unexpectedField="not allowed",
        )
