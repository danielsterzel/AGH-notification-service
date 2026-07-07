
from mailer.models import Email
from notification.models import NotificationEvent
from mailer.renderer import render_template

class AssignmentDeadlineApproachBuilder:
    def build(self, notification: NotificationEvent) -> Email:

        payload = notification.payload
        
        html = render_template(
            "assignment_deadline_approach.html",
            assignment_title=payload.assignment_title,
            course_title=payload.course_title,
            time_till_deadline=payload.time_till_deadline,
            assignment_url_path=payload.assignment_url_path
        )

        return Email(
            subject=f"Assignment Deadline is approaching for {notification.payload.assignment_title}",
            html=html,
        )
