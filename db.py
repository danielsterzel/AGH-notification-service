
from asyncpg import create_pool, Pool
from notification.models import NotificationEvent

from settings import settings

async def get_pool() -> Pool:
    return await create_pool(settings.database_url, min_size=1, max_size=3)


async def save_notification(
    pool: Pool, user_id: str, notification: NotificationEvent
) -> None:

    await pool.execute(
        """
    INSERT INTO notification(user_id, event_type, payload, is_read, sent_at, expires_at)
                       VALUES($1, $2, $3, $4, $5, $6)
    """,
        user_id,
        notification.payload.event_type,
        notification.model_dump_json(),
        False,
        notification.sent_at,
        None,
    )

async def get_user_emails(pool: Pool, user_ids: list[str]) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT email FROM "user"
        WHERE id = ANY($1) AND banned = false AND email_verified = true
        """,
        user_ids,
    )
    return [r["email"] for r in rows]

async def try_mark_processed(pool: Pool, event_id) -> bool:
    result = await pool.execute(
        """
INSERT INTO processed_event(event_id) VALUES($1)
    ON CONFLICT DO NOTHING
""",
event_id
    )

    return result == "INSERT 0 1"
 