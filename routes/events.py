from fastapi import APIRouter, HTTPException, status, Depends
from db.connection import get_connection
from models.events import EventForList, AllEvents, RSVPResponse, EventPostRequest, EventPostResponse, EventPatchRequest, GetEventAttendees
from models.events import EventResponse
import psycopg2.extras
from routes.auth import get_current_user_id

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



@router.post("/{event_id}/rsvp", status_code=status.HTTP_201_CREATED)
def rsvp_to_event(event_id: int, user_id: int = Depends(get_current_user_id)) -> RSVPResponse:
    conn = get_connection()

    # check if user already rsvp'ed before
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM rsvps " \
            "WHERE attendee_id = %s AND event_id = %s;",
            (user_id, event_id),
        )
        rsvp = cursor.fetchone()

    if rsvp:
        raise HTTPException(status_code=409, detail="Already RSVP'd")

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        try:
            cursor.execute(
                "INSERT INTO rsvps (attendee_id, event_id) VALUES (%s, %s) RETURNING *;",
                (user_id, event_id),
            )
            row = cursor.fetchone()
            conn.commit()
            conn.close()

        except psycopg2.errors.ForeignKeyViolation:
            raise HTTPException(status_code=404, detail="Event not found")
        
    return {"rsvp": row}



@router.delete("/{event_id}/rsvp/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, user_id: int = Depends(get_current_user_id)) -> None:
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM rsvps " \
            "WHERE attendee_id = %s AND event_id = %s " \
            "RETURNING *;",
            (user_id, event_id),
        )
        row = cursor.fetchone()
    conn.commit()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="RSVP not found")
        
    return


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(event: EventPostRequest, user_id: int = Depends(get_current_user_id)) -> EventPostResponse:
    changes = event.model_dump()
    
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        try:
            cursor.execute(
                "INSERT INTO events (title, description, starts_at, ends_at, venue_id, organiser_id) " \
                "VALUES (%s, %s, %s, %s, %s, %s) " \
                "RETURNING *;",
                (*changes.values(), user_id),
            )
            row = cursor.fetchone()
            conn.commit()
            conn.close()

        except psycopg2.errors.ForeignKeyViolation:
            raise HTTPException(status_code=404, detail="Venue not found")
        
    return {"event": row}



@router.patch("/{event_id}")
def update_event(event_id: int, updates: EventPatchRequest, user_id: int = Depends(get_current_user_id)) -> EventPostResponse:
    updates = updates.model_dump(exclude_unset=True)

    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor: # get current event details
        cursor.execute(
            "SELECT * FROM events " \
            "WHERE id = %s;",
            (event_id,)
        )
        event = cursor.fetchone()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event["organiser_id"] != user_id:
        raise HTTPException(status_code=403, detail="Logged in user is not the organiser of event")

    if not updates:
        return {"event": event}

    if "starts_at" in updates and "ends_at" in updates:
        starts, ends = updates["starts_at"], updates["ends_at"]
    elif "starts_at" in updates:
        starts, ends = updates["starts_at"], event["ends_at"]
    elif "ends_at" in updates:
        starts, ends = event["starts_at"], updates["ends_at"]
    
    if ends <= starts:
        raise HTTPException(status_code=400, detail="Invalid timings, event ends before starting")

    # now updating
    assignments = ", ".join(f"{column} = %s" for column in updates)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(
            f"UPDATE events SET {assignments} " \
            "WHERE id = %s RETURNING *;",
            (*updates.values(), event_id,)
        )
        event = cursor.fetchone()
    conn.commit()
    conn.close()

    return {"event": event}


@router.get("/{event_id}/attendees")
def get_attendees(event_id: int, user_id: int = Depends(get_current_user_id)) -> GetEventAttendees:
    conn = get_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor: # get event details
        cursor.execute(
            "SELECT * FROM events " \
            "WHERE id = %s;",
            (event_id,)
        )
        event = cursor.fetchone()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event["organiser_id"] != user_id:
        raise HTTPException(status_code=403, detail="Logged in user is not the organiser of event")

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(
            "SELECT u.id, u.name, u.email " \
            "FROM rsvps r INNER JOIN users u " \
                "ON r.attendee_id = u.id " \
            "WHERE r.event_id = %s;",
            (event_id,)
        )
        attendees = cursor.fetchall()
    conn.close()

    return {"attendees": attendees}


