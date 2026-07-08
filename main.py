import aioboto3
from types_aiobotocore_sqs import SQSClient

import json
import logging

from asyncio import run, sleep

from settings import settings

from pydantic import ValidationError

from notification.models import NotificationEvent
from db import (
    get_user_emails,
    get_pool,
    save_notifications,
    try_mark_processed,
    unmark_processed,
)
from mailer.emails import send_notification_email

from health import start_health_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

""" Później mozemy dodac jakiegos Redisa ma processed_event tabele 
bo latwiej tak storowac z TTL czy są processed czy nie. Nie dawałem tego
bo nie korzystamy z Redisa na razie"""


async def process_message(pool, sqs, msg) -> None:
    try:
        body = json.loads(msg["Body"])
        notification = NotificationEvent(**body)
    except (ValidationError, json.JSONDecodeError) as e:
        logging.error(f"Invalid notification: {e}")
        await sqs.delete_message(
            QueueUrl=settings.sqs_queue_url,
            ReceiptHandle=msg["ReceiptHandle"],
        )
        return

    logging.info(f"\n ==== RECEIVED JSON ==== \n{body}\n")

    if not await try_mark_processed(pool, notification.event_id):
        logging.info(f"Duplicate event {notification.event_id}, skipping")
        await sqs.delete_message(
            QueueUrl=settings.sqs_queue_url,
            ReceiptHandle=msg["ReceiptHandle"],
        )
        return

    try:
        await save_notifications(
            pool=pool, user_ids=notification.user_ids, notification=notification
        )

        logging.info(f"Saved notification {notification.event_id} into Supabase")

        emails = await get_user_emails(pool=pool, user_ids=notification.user_ids)

        logging.info(f"EMAILS content: \n{emails}\n")

        if emails:
            logging.info("\nSENDING EMAIL TO EMAILS...\n")
            await send_notification_email(emails=emails, notification=notification)

        await sqs.delete_message(
            QueueUrl=settings.sqs_queue_url,
            ReceiptHandle=msg["ReceiptHandle"],
        )
    except Exception:
        logging.exception(f"Failed to process event: {notification.event_id}")
        try:
            await unmark_processed(pool, notification.event_id)
        except Exception:
            logging.critical(
                f"Failed to unmark {notification.event_id} - stuck as processed but never sent"
            )


async def main():
    await start_health_server()
    print("I am running...")

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
                    await process_message(pool, sqs, msg)
    finally:
        await pool.close()


if __name__ == "__main__":
    run(main())
