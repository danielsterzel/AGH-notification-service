
# Notification microservice

Offers notification functionality: students get messages when an assignment was created, removed, updated, returned etc.

## Technological stack:
- Python 3.12
- Resend
- AWS SQS queue
- supabase(PostgreSQL)
- Redis... (maybe)

## Notification Models

- `NotificationEvent`:
JSON issued by `sprawdzarka-frontend` component. Created whenever an assigment is created or reshaped in any way. Sent on the AWS SQS in order to be read by notification-service worker. Data model:

|Field | Type | Meaning |
|----- | -----| ------- |
| `event_type` | `NotificationEventType`| Type of notification: goto NotificationEventType model for more information |
| `course_id ` | String | Id of course the assignment is tied to|
| `user_ids` | List[String] | List of user ids to which send the notification |
| `payload` | Python: Union Type: `GradeReturnPayload`, `AssigmentCreationPayload`, `AssigmentDeadlineApproachPayload`, `AssigmentDeadlineUpdatePayload` SQL: TEXT | Message content| 
| `sent_at` | Python: Datetime SQL: TIMESTAMP | CET time at which the message was sent|

- `NotificationEventType`:

