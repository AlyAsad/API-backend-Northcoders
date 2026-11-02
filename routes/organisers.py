from fastapi import APIRouter, HTTPException
from db.connection import get_connection
import psycopg2
from models.organisers import GetOrganiserStats

router = APIRouter(prefix="/api/organisers", tags=["Organisers"])

@router.get("/{organiser_id}/stats")
def get_organiser_stats(organiser_id: int) -> GetOrganiserStats:
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute("""
            WITH event_attendance AS (
                SELECT
                    e.id AS event_id,
                    e.organiser_id,
                    COUNT(r.id) AS attendee_count
                FROM events e
                LEFT JOIN rsvps r ON e.id = r.event_id
                GROUP BY e.id, e.organiser_id
            ),
            organiser_stats AS (
                SELECT
                    u.id AS organiser_id,
                    u.name,
                    COUNT(ea.event_id) AS total_events,
                    ROUND(AVG(ea.attendee_count), 1) AS avg_attendance,
                    MAX(ea.attendee_count) AS best_attended_count,
                    RANK() OVER (
                        ORDER BY COUNT(ea.event_id) DESC
                    ) AS organiser_rank
                FROM users u
                JOIN event_attendance ea
                    ON u.id = ea.organiser_id
                GROUP BY u.id, u.name
            )
            SELECT *
            FROM organiser_stats
            WHERE organiser_id = %s;
            """,
            (organiser_id,)
        )
        organiser = cursor.fetchone()
    conn.close()

    if not organiser:
        raise HTTPException(status_code=404, detail="Organiser not found or has no events")

    return {"stats": organiser}
