import pytest
from fastapi.testclient import TestClient
from db.connection import get_connection
from main import app
from routes.auth import hash_password


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def static():
    """
    Used to make sure the database doesn't change after
    tests have run by comparing row counts before and after.
    It won't catch if a row's data got edited as a side-effect
    (only catches if rows added/deleted), since it would be too
    expensive to check that.
    """
    
    conn = get_connection()
    tables = {"users": 0, "venues": 0, "events": 0, "rsvps": 0}

    # gathering row counts
    for table in tables.keys():
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            tables[table] = cur.fetchone()[0]

    yield
    
    # checking again after test
    for table in tables.keys():
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            assert cur.fetchone()[0] == tables[table], "Rows modified by test!"

    conn.close()


@pytest.fixture
def sample_user():
    email = "sample_user@email.com"
    password = "sample_password"
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES ('sample_user', %s, %s)
            RETURNING id
            """,
            (email, hash_password(password))
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        yield user_id, email, password
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()



@pytest.fixture
def sample_venue():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO venues (name, address, capacity)
            VALUES ('sample_venue', 'sample address', 5)
            RETURNING id
            """
        )
        venue_id = cur.fetchone()[0]
        conn.commit()
        yield venue_id
        cur.execute("DELETE FROM venues WHERE id = %s", (venue_id,))
    conn.commit()
    conn.close()


@pytest.fixture
def sample_event(sample_user, sample_venue):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO events (title, description, starts_at, ends_at, organiser_id, venue_id)
            VALUES ('sample_event', 'sample description', '2026-06-18T18:30:00+01:00', '2026-06-18T21:00:00+01:00', %s, %s)
            RETURNING id
            """,
            (sample_user[0], sample_venue)
        )
        event_id = cur.fetchone()[0]
        conn.commit()
        yield event_id
        cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
    conn.commit()
    conn.close()


@pytest.fixture
def sample_rsvp(sample_user, sample_event):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO rsvps (attendee_id, event_id)
            VALUES (%s, %s)
            RETURNING id
            """,
            (sample_user[0], sample_event)
        )
        rsvp_id = cur.fetchone()[0]
        conn.commit()
        yield rsvp_id, sample_user, sample_event
        cur.execute("DELETE FROM rsvps WHERE id = %s", (rsvp_id,))
    conn.commit()
    conn.close()