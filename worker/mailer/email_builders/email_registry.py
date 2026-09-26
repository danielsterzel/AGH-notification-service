from notification.models import NotificationEventType
from mailer.email_builders.base import EmailBuilder
from mailer.email_builders.assignment_creation import AssignmentCreationBuilder
from mailer.email_builders.assignment_deadline_approach import (
    AssignmentDeadlineApproachBuilder,
)
from mailer.email_builders.assignment_deadline_update import (
    AssignmentDeadlineUpdateBuilder,
)
from mailer.email_builders.grade_return import GradeReturnBuilder

BUILDERS: dict[NotificationEventType, EmailBuilder] = {
    NotificationEventType.GRADE_RETURN: GradeReturnBuilder(),
    NotificationEventType.ASSIGNMENT_CREATION: AssignmentCreationBuilder(),
    NotificationEventType.ASSIGNMENT_DEADLINE_APPROACH: AssignmentDeadlineApproachBuilder(),
    NotificationEventType.ASSIGNMENT_DEADLINE_UPDATE: AssignmentDeadlineUpdateBuilder(),
}
