
from mailer.models import Email
from notification.models import NotificationEvent
from mailer.renderer import render_template

class AssignmentCreationBuilder:
    def build(self, notification: NotificationEvent) -> Email:

        payload = notification.payload

        html = render_template(
            "assignment_creation.html",
            assignment_title=payload.assignment_title,
            course_title=payload.course_title,
            professor_name=payload.professor_name,
            assignment_deadline=payload.assignment_deadline,
            assignment_url_path=payload.assignment_url_path,
        )

        return Email(
            subject=f"New Assignment dropped 😭🤧🤧🥀\n for course: {notification.payload.course_title}",
            html=html,
        )
