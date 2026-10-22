from fastapi import APIRouter, HTTPException
from db.connection import get_connection
from models.events import EventForList, AllEvents
from models.events import EventResponse
import psycopg2.extras

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=AllEvents)
def get_events():
    conn = get_connection()
    
    with conn.cursor() as cur:
        cur.execute("""SELECT e.id, e.title, e.starts_at, e.ends_at, v.name, v.address
                    FROM events e INNER JOIN venues v
                        ON e.venue_id = v.id
                    ORDER BY starts_at;""") # could order by id/end date
        rows = cur.fetchall()
    conn.close()

    events = [
        EventForList(
            id=event[0],
            title=event[1],
            starts_at=event[2],
            ends_at=event[3],
            location=", ".join(filter(None, [event[4], event[5]]))
        )
        for event in rows
    ]
    return AllEvents(events=events)






@router.get("/{id}", response_model=EventResponse)
def get_event_by_id(id: int):
    conn = get_connection()
    
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """SELECT e.id, e.title, e.description, e.starts_at, e.ends_at,
                v.name as location, v.address, v.capacity, e.created_at
            FROM events e INNER JOIN venues v
                ON e.venue_id = v.id
            WHERE e.id = %s;""",
            (id,)
        )
        row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "404", "message": "Event not found"},
        )

    return EventResponse(event=row)
