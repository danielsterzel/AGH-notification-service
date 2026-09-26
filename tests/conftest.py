import os

import pytest
from unittest.mock import AsyncMock, MagicMock
import json


# Test collection imports worker modules before fixtures run. These local-only
# defaults keep tests independent from a developer's private .env file.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("AWS_REGION", "eu-central-1")
os.environ.setdefault("SQS_QUEUE_URL", "https://sqs.eu-central-1.amazonaws.com/123/test")
os.environ.setdefault("SMTP_EMAIL", "sender@gmail.com")
os.environ.setdefault("SMTP_APP_PASSWORD", "test-app-password")


@pytest.fixture
def mock_sqs():
    sqs = AsyncMock()
    return sqs


@pytest.fixture
def mock_pool():
    return MagicMock()


@pytest.fixture
def valid_notification_body() -> dict:

    return {
        "eventId": "550e8400-e29b-41d4-a716-446655440000",
        "courseId": "course123",
        "userIds": ["user1"],
        "payload": {
            "eventType": "grade_return",
            "assignmentTitle": "Zadanie 1",
            "courseTitle": "Informatyka",
            "assignmentUrlPath": None,
        },
        "sentAt": "2026-07-08T12:00:00+02:00",
    }


@pytest.fixture
def make_sqs_message():
    def _make(body: dict) -> dict:
        return {"Body": json.dumps(body), "ReceiptHandle": "fake-recipt-handle-123"}

    return _make
