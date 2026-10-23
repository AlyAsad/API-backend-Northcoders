"""
Tests for the events API/table
"""

from db.connection import get_connection
from tests.test_auth import login_user

def test_get_events_returns_200_and_proper_format(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert "events" in response.json()
    
    events = response.json()["events"]
    assert isinstance(events, list)
    expected_keys = {"id", "title", "starts_at", "ends_at", "location"}
    assert set(events[0].keys()) == expected_keys


def test_get_events_returns_correct_data(client, sample_event):
    response = client.get("/api/events")
    events = response.json()["events"]
    assert any(event["id"] == sample_event for event in events), "Not fetching correct event data!"


def test_get_event_by_id_returns_200_and_proper_format(client, sample_event):
    response = client.get(f"/api/events/{sample_event}")
    assert response.status_code == 200
    assert "event" in response.json()
    
    event = response.json()["event"]
    assert isinstance(event, dict)
    expected_keys = {"id", "title", "description", "starts_at", "ends_at", "location", "address", "capacity", "created_at"}
    assert set(event.keys()) == expected_keys


def test_get_event_by_id_returns_correct_data(client, sample_event):
    response = client.get(f"/api/events/{sample_event}")
    event = response.json()["event"] 
    assert event["title"] == "sample_event", "Not fetching correct event data!"


def test_get_event_by_id_raises_correct_errors(client):
    response = client.get(f"/api/events/99999999")
    assert response.status_code == 404

    response = client.get(f"/api/events/str")
    assert response.status_code == 400



### RSVP TESTS
def test_rsvp_to_event_success_returns_201_and_details(client, sample_user, sample_event):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.post(f"/api/events/{sample_event}/rsvp",
                           headers={"Authorization": f"Bearer {token}"})

    try:
        assert response.status_code == 201
        assert "rsvp" in response.json()
        assert response.json()["rsvp"]["attendee_id"] == sample_user[0]
        assert response.json()["rsvp"]["event_id"] == sample_event
    finally: # cleaning up the added rsvp
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM rsvps WHERE id = %s", (response.json()["rsvp"]["id"],))
        conn.commit()
        conn.close()


def test_rsvp_invalid_token_returns_401(client, sample_event):
    response = client.post(f"/api/events/{sample_event}/rsvp",
                           headers={"Authorization": "Bearer faketoken"})

    assert response.status_code == 401


def test_rsvp_nonexistent_event_returns_404(client, sample_user):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.post("/api/events/99999999/rsvp",
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


def test_duplicate_rsvp_returns_409(client, sample_rsvp):
    token = login_user(client, sample_rsvp[1]).json()["access_token"]
    response = client.post(f"/api/events/{sample_rsvp[2]}/rsvp",
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 409