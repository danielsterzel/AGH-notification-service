from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, HttpUrl, field_validator
from pydantic.alias_generators import to_camel
from typing import List, Union, Literal, Optional
from enum import Enum
from uuid import UUID

WARSAW_TZ = ZoneInfo("Europe/Warsaw")


class NotificationEventType(str, Enum):
    GRADE_RETURN = "grade_return"
    ASSIGNMENT_CREATION = "assignment_creation"
    ASSIGNMENT_DEADLINE_UPDATE = "assignment_deadline_update"
    ASSIGNMENT_DEADLINE_APPROACH = "assignment_deadline_approach"


class BasePayload(BaseModel):
    model_config = {"alias_generator": to_camel, "extra": "forbid"}
    assignment_title: str = Field(..., min_length=3, max_length=50)
    course_title: str = Field(..., min_length=3, max_length=75)

    assignment_url_path: Optional[HttpUrl] = Field(None)

    # @field_validator("assignment_url_path")
    # @classmethod
    # def is_internal_domain(cls, v):
    #     if v is not None and v.host not in ("nasza domena",):
    #         raise ValueError("URL points outside of our domain")
    #     return v


class GradeReturnPayload(BasePayload):
    event_type: Literal[NotificationEventType.GRADE_RETURN] = Field(...)


# Prowadzacy: <nazwa> utworzył nowe zadanie: <nazwa> w kursie: <>
class AssignmentCreationPayload(BasePayload):
    event_type: Literal[NotificationEventType.ASSIGNMENT_CREATION] = Field(...)
    professor_name: str = Field(..., min_length=3, max_length=100)
    assignment_deadline: Optional[datetime] = Field(None)


# Prowadzacy przedłuzył termin oddania o <czas: tydzien | dzien | ...>. Nowy termin oddania: <konkretna data>
class AssignmentDeadlineUpdatePayload(BasePayload):
    event_type: Literal[NotificationEventType.ASSIGNMENT_DEADLINE_UPDATE]
    professor_name: str = Field(..., min_length=3, max_length=100)
    assignment_new_deadline: datetime = Field(...)


# Masz jeszcze <x czasu> na oddanie zadania: <nazwa zadania>
class AssignmentDeadlineApproachPayload(BasePayload):
    event_type: Literal[NotificationEventType.ASSIGNMENT_DEADLINE_APPROACH]
    time_till_deadline: timedelta = Field(...)


# issued by sprawdzarka-frontend on SQS
class NotificationEvent(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "str_strip_whitespace": True,
        "extra": "forbid",
    }
    event_id: UUID = Field(...)

    course_id: str = Field(...)

    user_ids: List[str] = Field(..., min_length=1)

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, v):
        if not v or any(not uid.strip() for uid in v):
            raise ValueError("User ids must be non-empty strings")
        return v

    payload: Union[
        GradeReturnPayload,
        AssignmentCreationPayload,
        AssignmentDeadlineApproachPayload,
        AssignmentDeadlineUpdatePayload,
    ] = Field(..., discriminator="event_type")
    sent_at: datetime = Field(default_factory=lambda: datetime.now(tz=WARSAW_TZ))
