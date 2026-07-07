import aioboto3
from types_aiobotocore_sqs import SQSClient

import json
import logging

from asyncio import run, gather

from settings import settings

from pydantic import ValidationError

from notification.models import NotificationEvent
from db import get_user_emails, get_pool, save_notification, try_mark_processed
from mailer.emails import send_notification_email

from health import start_health_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

async def main():
    
    await start_health_server()
    print(f"I am running...")

    session = aioboto3.Session()
    try:
        pool = await get_pool()

        async with session.client(
            "sqs",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        ) as sqs:
            sqs: SQSClient
            while True:
                resp = await sqs.receive_message(
                    QueueUrl=settings.sqs_queue_url, WaitTimeSeconds=20
                )

                messages = resp.get("Messages", [])

                if not messages:
                    logging.debug("No messages in response inside SQS")

                for msg in messages:
                    try:
                        body = json.loads(msg["Body"])
                        notification = NotificationEvent(**body)

                    except (ValidationError, json.JSONDecodeError) as e:
                        logging.error(f"Invalid notification: {e}")

                        await sqs.delete_message(
                            QueueUrl=settings.sqs_queue_url,
                            ReceiptHandle=msg["ReceiptHandle"],
                        )
                        continue
                        
                    # REFACTOR !!!!!!!!!
                    if not await try_mark_processed(pool, notification.event_id):
                        logging.info(f"Duplicate event {notification.event_id}, skipping")
                        await sqs.delete_message(
                            QueueUrl=settings.sqs_queue_url,
                            ReceiptHandle=msg["ReceiptHandle"],
                        )
                        continue

                    await gather(
                        *[
                            save_notification(
                                pool=pool, user_id=user_id, notification=notification
                            )
                            for user_id in notification.user_ids
                        ]
                    )

                    emails = await get_user_emails(
                        pool=pool, user_ids=notification.user_ids
                    )
                    # send email worker
                    if emails:
                        await send_notification_email(emails=emails, notification=notification)

                    await sqs.delete_message(
                        QueueUrl=settings.sqs_queue_url,
                        ReceiptHandle=msg["ReceiptHandle"],
                    )
    finally:
        await pool.close()


if __name__ == "__main__":
    run(main())
