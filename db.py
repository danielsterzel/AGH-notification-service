from asyncpg import create_pool, Pool
from notification.models import NotificationEvent

from settings import settings


async def get_pool() -> Pool:
    return await create_pool(
        settings.database_url, min_size=1, max_size=3, statement_cache_size=0
    )


async def save_notifications(
    pool: Pool, user_ids: list[str], notification: NotificationEvent
) -> None:

    await pool.execute(
        """
    INSERT INTO notification(user_id, event_type, payload, is_read, sent_at, expires_at)
    SELECT u.user_id, $2, $3::jsonb, false, $4, NULL
    FROM unnest($1::text[]) AS u(user_id)
    """,
        user_ids,
        notification.payload.event_type,
        notification.model_dump_json(),
        notification.sent_at,
    )


async def get_user_emails(pool: Pool, user_ids: list[str]) -> list[str]:

    # AND banned = false AND email_verified = true
    rows = await pool.fetch(
        """
        SELECT email FROM "user"
        WHERE id = ANY($1) 
        """,
        user_ids,
    )
    return [r["email"] for r in rows]


async def try_mark_processed(pool: Pool, event_id) -> bool:

    result = await pool.execute(
        """
INSERT INTO processed_event(event_id) VALUES($1)
    ON CONFLICT (event_id) DO UPDATE
    SET processed_at = now()
    WHERE processed_event.processed_at < now() - interval '10 minutes'
""",
        event_id,
    )

    return result == "INSERT 0 1"


async def unmark_processed(pool: Pool, event_id) -> bool:

    result = await pool.execute(
        """DELETE FROM processed_event WHERE event_id = $1 """, event_id
    )

    return result == "DELETE 1"
