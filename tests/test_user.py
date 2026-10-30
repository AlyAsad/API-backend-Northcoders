from db.connection import get_connection
from tests.test_auth import login_user

def test_get_user_events_returns_correct_data(client, sample_rsvp, sample_venue):
    user = sample_rsvp[1]
    token = login_user(client, user).json()["access_token"]
    
    conn = get_connection()
    # creating another event, earlier than sample_event
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO events (
                title, description, starts_at, ends_at,
                organiser_id, venue_id
            )
            VALUES (
                'earlier_event', 'description',
                '2026-05-18T18:30:00+01:00',
                '2026-05-18T21:00:00+01:00',
                %s, %s
            )
            RETURNING id
            """,
            (user[0], sample_venue)
        )
        event_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO rsvps (attendee_id, event_id)
            VALUES (%s, %s)
            """,
            (user[0], event_id)
        )

    conn.commit()

    try:
        response = client.get(
            "/api/user/me/events",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        events = response.json()["events"]

        assert len(events) == 2
        assert events[0]["title"] == "earlier_event"
        assert events[0]["event_rank"] == 1
        assert events[1]["event_rank"] == 2

        assert all(event["total_rsvps"] == 2 for event in events)
        assert events[0]["starts_at"] < events[1]["starts_at"]
        assert all("rsvp_date" in event for event in events)

    finally:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM rsvps WHERE event_id = %s",
                (event_id,)
            )
            cursor.execute(
                "DELETE FROM events WHERE id = %s",
                (event_id,)
            )
        conn.commit()
        conn.close()


def test_get_user_events_invalid_token_returns_401(client):
    response = client.get(
        "/api/user/me/events",
        headers={"Authorization": "Bearer faketoken"}
    )
    assert response.status_code == 401


def test_get_user_events_missing_token_returns_401(client):
    response = client.get("/api/user/me/events")
    assert response.status_code == 401


