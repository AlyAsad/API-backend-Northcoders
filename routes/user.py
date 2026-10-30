from fastapi import APIRouter, Depends
from db.connection import get_connection
from routes.auth import get_current_user_id
from models.user import GetUserEvents
import psycopg2

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("/me/events")
def get_all_events(user_id: int = Depends(get_current_user_id)) -> GetUserEvents:
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("""
            SELECT e.id, e.title, e.starts_at, r.created_at AS rsvp_date,
                ROW_NUMBER() OVER (
                    ORDER BY e.starts_at ASC
                ) AS event_rank,
                COUNT(*) OVER () AS total_rsvps
            FROM rsvps r
            JOIN events e ON r.event_id = e.id
            WHERE r.attendee_id = %s
            ORDER BY e.starts_at ASC;
            """,
            (user_id,)
        )
        events = cursor.fetchall()
    conn.close()

    return {"events": events}
