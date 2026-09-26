from mailer.models import Email
from mailer.renderer import render_template
from notification.models import NotificationEvent


class AssignmentDeadlineUpdateBuilder:
    def build(self, notification: NotificationEvent) -> Email:

        payload = notification.payload

        html = render_template(
            "assignment_deadline_update.html",
            assignment_title=payload.assignment_title,
            course_title=payload.course_title,
            professor_name=payload.professor_name,
            assignment_new_deadline=payload.assignment_new_deadline,
            assignment_url_path=payload.assignment_url_path,
        )

        payload = notification.payload

        return Email(
            subject=f"{payload.assignment_title} deadline has been updated for course: {payload.course_title}",
            html=html,
        )
