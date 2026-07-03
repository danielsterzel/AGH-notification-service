from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, HttpUrl
from pydantic.alias_generators import to_camel
from typing import List, Union, Literal, Optional
from enum import Enum

WARSAW_TZ = ZoneInfo("Europe/Warsaw")


class NotificationEventType(str, Enum):
    GRADE_RETURN = "grade_return"
    ASSIGNMENT_CREATION = "assignment_creation"
    ASSIGNMENT_DEADLINE_UPDATE = "assignment_deadline_update"
    ASSIGNMENT_DEADLINE_APPROACH = "assigment_deadline_approach"


class BasePayload(BaseModel):
    model_config = {"alias_generator": to_camel, "extra": "forbid"}
    assignment_title: str = Field(..., min_length=3, max_length=50)
    course_title: str = Field(..., min_length=3, max_length=75)
    assignment_url_path: Optional[HttpUrl] = Field(None)


class GradeReturnPayload(BasePayload):
    event_type: Literal["grade_return"] = Field(...)


# Prowadzacy: <nazwa> utworzył nowe zadanie: <nazwa> w kursie: <>
class AssigmentCreationPayload(BasePayload):
    event_type: Literal["assignment_creation"] = Field(...)
    professor_name: str = Field(..., min_length=3, max_length=100)
    assignment_deadline: Optional[datetime]


# Prowadzacy przedłuzył termin oddania o <czas: tydzien | dzien | ...>. Nowy termin oddania: <konkretna data>
class AssigmentDeadlineUpdatePayload(BasePayload):
    event_type: Literal["assignment_deadline_update"]
    professor_name: str = Field(..., min_length=3, max_length=100)
    assignmnet_new_deadline: datetime = Field(...)


# Masz jeszcze <x czasu> na oddanie zadania: <nazwa zadania>
class AssigmentDeadlineApproachPayload(BasePayload):
    event_type: Literal["assigment_deadline_approach"]
    time_till_deadline: timedelta = Field(...)


# issued by sprawdzarka-frontend on SQS
class NotificationEvent(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "str_strip_whitespace": True,
        "extra": "forbid",
    }

    event_type: NotificationEventType = Field(...)
    course_id: str = Field(...)
    user_ids: List[str] = Field(..., min_length=1)

    payload: Union[
        GradeReturnPayload,
        AssigmentCreationPayload,
        AssigmentDeadlineApproachPayload,
        AssigmentDeadlineUpdatePayload,
    ] = Field(..., discriminator="event_type")
    sent_at: datetime = Field(..., default_factory=lambda: datetime.now(tz=WARSAW_TZ))
