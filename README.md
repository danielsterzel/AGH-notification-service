
# Notification microservice

This is the notification microservice for the new AGH elearning platfrom ment to supersede the *UPEL platform*. 


Offers notification functionality: students get messages when an assignment was created, removed, updated, returned etc.

## Technological stack:
- Python 3.12
- Resend
- AWS SQS queue
- ECS Fargate
- supabase(PostgreSQL)
- Redis... (maybe)

## Worker logical flow

When the worker starts it initializes health check server required for keeping Fargate deployment alive and allowing to restart after 




## Data flow chart

...

## AWS configfuration:

**SQS**
- Type Standard
- Receive message time: 20 seconds

**ECR** 


## Email service


## Database and database connection




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




## SQS JSON model:
```
{
    "Messages": [
        "MessageId": "abc123",
        "RecipientHandle": "some-long-string",
        "Body": '{"event_type": "grade_return", ...}'
    ]
}
```

 - `RecipientHandle` parameter is used to delete this message from SQS
 - `Body` - JSON body sent by NEXT.js


 ## Notification Service workflow:




 ## Email worker
 Pattern: Builder per event type implementuje EmailBuilder Protocol. email.py używa dispatch pattern — na podstawie event_type wybiera odpowiedni builder, buduje Email obiekt, wysyła przez resend.Emails.send_async.
Dlaczego Protocol a nie ABC: Protocol = duck typing, nie wymaga dziedziczenia. Czyściejsze i bardziej Pythonowe.

**Protocol** - Builders do not inherit any other behaviour. EmailBuilder is strictly a contract. 
`ABC` is closer to Java's abstract classes. EmailBuilder does not impose any shared function implementations.


SMART UNION (doesnt validate each class already inferes class from event_type) errors are specific to one class not all Union types at all

SQS moze oddac ta sama wiadomosc dwa razy(gwarantuje co najmniej jeden wiec no) dlatego trzeba
wprowadzic event_id zeby n
ie byly wysylane emaile do evnetów które juz zostaly przerobione


healthcheck bo fargate potrzebuje sygnalu. Nie daje anam informacji poza tym ze proces dziala i tyle.

We used `try_mark_processed` to combat over sending of emails due to SQS policy: "at-least-once-delivery".