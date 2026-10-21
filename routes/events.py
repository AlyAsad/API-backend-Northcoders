from fastapi import APIRouter
from db.connection import get_connection

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("")
def get_events():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""SELECT e.id, e.title, e.starts_at, e.ends_at, v.name, v.address
                    FROM events e INNER JOIN venues v
                        ON e.venue_id = v.id
                    ORDER BY starts_at;""") # could order by id/end date
        rows = cur.fetchall()
    
    conn.close()

    events = [{"id": event[0], "title": event[1], "starts_at": event[2],
                "ends_at": event[3], "location": ", ".join(filter(None, [event[4], event[5]]))}
              for event in rows]
    return {"events": events}


