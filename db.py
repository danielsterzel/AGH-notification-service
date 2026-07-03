import asyncio
from asyncpg import connect, Connection
from models import NotificationEvent

from settings import settings


async def get_connection() -> Connection:
    return await connect(settings.database_url)


async def save_notification(
    conn: Connection, user_id: str, notification: NotificationEvent
) -> None:

    await conn.execute(
        """
    INSERT INTO notification(user_id, event_type, payload, is_read, sent_at, expires_at)
                       VALUES($1, $2, $3, $4, $5, $6)
    """,
        user_id,
        notification.event_type,
        notification.model_dump_json(),
        False,
        notification.sent_at,
        None,
    )


async def _fetch_single_user_email(conn: Connection, user_id: str) -> str:
    return await conn.fetchval(
        """
        SELECT email FROM "user" WHERE id = $1 AND banned = false AND email_verified = true
    """,
        user_id,
    )


async def get_user_emails(
    conn: Connection, notification: NotificationEvent
) -> list[str]:

    return await asyncio.gather(
        *[_fetch_single_user_email(conn, user_id) for user_id in notification.user_ids]
    )
