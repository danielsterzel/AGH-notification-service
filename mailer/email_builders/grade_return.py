
from mailer.models import Email
from mailer.renderer import render_template
from notification.models import NotificationEvent

class GradeReturnBuilder:
    def build(self, notification: NotificationEvent) -> Email:
        
        payload = notification.payload

        html = render_template(
            "grade_return.html",
            assignment_title=payload.assignment_title,
            course_title=payload.course_title,
            assignment_url_path=payload.assignment_url_path
        )

        return Email(
            subject=f"Grade for assignment {notification.payload.assignment_title} has been returned",
            html=html,
        )
