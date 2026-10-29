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
    assert any(event["id"] == sample_event[0] for event in events), "Not fetching correct event data!"


def test_get_event_by_id_returns_200_and_proper_format(client, sample_event):
    response = client.get(f"/api/events/{sample_event[0]}")
    assert response.status_code == 200
    assert "event" in response.json()
    
    event = response.json()["event"]
    assert isinstance(event, dict)
    expected_keys = {"id", "title", "description", "starts_at", "ends_at", "location", "address", "capacity", "created_at"}
    assert set(event.keys()) == expected_keys


def test_get_event_by_id_returns_correct_data(client, sample_event):
    response = client.get(f"/api/events/{sample_event[0]}")
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
    response = client.post(f"/api/events/{sample_event[0]}/rsvp",
                           headers={"Authorization": f"Bearer {token}"})

    try:
        assert response.status_code == 201
        assert "rsvp" in response.json()
        assert response.json()["rsvp"]["attendee_id"] == sample_user[0]
        assert response.json()["rsvp"]["event_id"] == sample_event[0]
    finally: # cleaning up the added rsvp
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM rsvps WHERE id = %s", (response.json()["rsvp"]["id"],))
        conn.commit()
        conn.close()


def test_rsvp_invalid_token_returns_401(client, sample_event):
    response = client.post(f"/api/events/{sample_event[0]}/rsvp",
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


## DELETION TESTS
def test_delete_rsvp_returns_204_and_no_content(client, sample_rsvp):
    token = login_user(client, sample_rsvp[1]).json()["access_token"]
    response = client.delete(f"/api/events/{sample_rsvp[2]}/rsvp/me",
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204
    assert not response.content


def test_delete_rsvp_invalid_token_returns_401(client, sample_rsvp):
    response = client.delete(f"/api/events/{sample_rsvp[2]}/rsvp/me",
                           headers={"Authorization": "Bearer faketoken"})

    assert response.status_code == 401


def test_delete_rsvp_doesnt_exist_returns_404(client, sample_user, sample_event):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.delete(f"/api/events/{sample_event[0]}/rsvp/me",
                           headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


## POST EVENT TESTS
def test_post_event_success_returns_201_and_details(client, sample_user, sample_venue):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.post(f"/api/events",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "title": "test_title",
                               "description": "test_desc",
                               "starts_at": "2025-08-15T18:00:00Z",
                               "ends_at": "2025-08-15T21:00:00Z",
                               "venue_id": sample_venue
                           })

    try:
        assert response.status_code == 201
        assert "event" in response.json()
        assert response.json()["event"]["organiser_id"] == sample_user[0]
        assert response.json()["event"]["venue_id"] == sample_venue
    finally: # cleaning up the added event
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM events WHERE id = %s", (response.json()["event"]["id"],))
        conn.commit()
        conn.close()


def test_post_event_invalid_token_returns_401(client, sample_venue):
    response = client.post(f"/api/events",
                           headers={"Authorization": "Bearer faketoken"},
                           json = {
                               "title": "test_title",
                               "description": "test_desc",
                               "starts_at": "2025-08-15T18:00:00Z",
                               "ends_at": "2025-08-15T21:00:00Z",
                               "venue_id": sample_venue
                           })

    assert response.status_code == 401


def test_post_event_venue_doesnt_exist_returns_404(client, sample_user):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.post(f"/api/events",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "title": "test_title",
                               "description": "test_desc",
                               "starts_at": "2025-08-15T18:00:00Z",
                               "ends_at": "2025-08-15T21:00:00Z",
                               "venue_id": 99999999
                           })

    assert response.status_code == 404


def test_post_event_missing_field_returns_400(client, sample_user):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.post(f"/api/events",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "title": "test_title",
                               "description": "test_desc",
                               "starts_at": "2025-08-15T18:00:00Z",
                               "ends_at": "2025-08-15T21:00:00Z"
                           })

    assert response.status_code == 400


def test_post_event_invalid_date_returns_400(client, sample_user, sample_venue):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.post(f"/api/events",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "title": "test_title",
                               "description": "test_desc",
                               "starts_at": "20258:00:00Z",
                               "ends_at": "2025-08-15T21:00:00Z",
                               "venue_id": sample_venue
                           })

    assert response.status_code == 400


def test_patch_events_success_returns_200_and_details(client, sample_event):
    token = login_user(client, sample_event[1]).json()["access_token"]
    response = client.patch(f"/api/events/{sample_event[0]}",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "description": "new_test_description",
                               "starts_at": "2025-08-15T19:00:00Z",
                               "ends_at": "2025-08-15T20:00:00Z",
                           })

    assert response.status_code == 200
    assert "event" in response.json()
    assert response.json()["event"]["id"] == sample_event[0]
    assert response.json()["event"]["organiser_id"] == sample_event[1][0]
    assert response.json()["event"]["description"] == "new_test_description"


def test_patch_invalid_token_returns_401(client, sample_event):
    response = client.patch(f"/api/events/{sample_event[0]}",
                           headers={"Authorization": f"Bearer faketoken"},
                           json = {
                               "description": "new_test_description",
                               "starts_at": "2025-08-15T19:00:00Z",
                               "ends_at": "2025-08-15T20:00:00Z",
                           })

    assert response.status_code == 401


def test_patch_event_different_user_returns_403(client, sample_user2, sample_event):
    token = login_user(client, sample_user2).json()["access_token"]
    response = client.patch(f"/api/events/{sample_event[0]}",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "description": "new_test_description",
                               "starts_at": "2025-08-15T19:00:00Z",
                               "ends_at": "2025-08-15T20:00:00Z",
                           })

    assert response.status_code == 403


def test_patch_event_not_found_returns_404(client, sample_user):
    token = login_user(client, sample_user).json()["access_token"]
    response = client.patch(f"/api/events/9999999999",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "description": "new_test_description",
                               "starts_at": "2025-08-15T19:00:00Z",
                               "ends_at": "2025-08-15T20:00:00Z",
                           })

    assert response.status_code == 404


def test_patch_event_invalid_date_returns_400(client, sample_event):
    token = login_user(client, sample_event[1]).json()["access_token"]
    response = client.patch(f"/api/events/{sample_event[0]}",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "description": "new_test_description",
                               "starts_at": "invalid",
                               "ends_at": "2025-08-15T20:00:00Z",
                           })

    assert response.status_code == 400

    token = login_user(client, sample_event[1]).json()["access_token"]
    response2 = client.patch(f"/api/events/{sample_event[0]}",
                           headers={"Authorization": f"Bearer {token}"},
                           json = {
                               "description": "new_test_description",
                               "starts_at": "2025-08-15T20:00:00Z",
                               "ends_at": "2025-08-15T19:00:00Z",
                           })

    assert response2.status_code == 400


def test_attendees_success_returns_200_and_details(client, sample_rsvp, sample_user, sample_user2):
    token1 = login_user(client, sample_user).json()["access_token"]
    response1 = client.get(f"/api/events/{sample_rsvp[2]}/attendees",
                        headers={"Authorization": f"Bearer {token1}"})
    
    assert response1.status_code == 200
    assert "attendees" in response1.json()
    assert len(response1.json()["attendees"]) == 1
    assert response1.json()["attendees"][0]["id"] == sample_user[0]

    token2 = login_user(client, sample_user2).json()["access_token"]
    rsvp = client.post(f"/api/events/{sample_rsvp[2]}/rsvp",
                           headers={"Authorization": f"Bearer {token2}"})

    try:
        response2 = client.get(f"/api/events/{sample_rsvp[2]}/attendees",
                            headers={"Authorization": f"Bearer {token1}"})
        
        assert len(response2.json()["attendees"]) == 2
        
    finally: # cleaning up the added rsvp
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM rsvps WHERE id = %s", (rsvp.json()["rsvp"]["id"],))
        conn.commit()
        conn.close()


def test_attendees_unauthenticated_user_returns_403(client, sample_rsvp, sample_user2):
    token1 = login_user(client, sample_user2).json()["access_token"]
    response1 = client.get(f"/api/events/{sample_rsvp[2]}/attendees",
                        headers={"Authorization": f"Bearer {token1}"})
    
    assert response1.status_code == 403


def test_attendees_no_user_returns_401(client, sample_rsvp):
    response1 = client.get(f"/api/events/{sample_rsvp[2]}/attendees",
                        headers={"Authorization": f"Bearer faketoken"})

    response1.status_code == 401


def test_attendees_no_event_returns_404(client, sample_user):
    token1 = login_user(client, sample_user).json()["access_token"]
    response1 = client.get(f"/api/events/99999999999/attendees",
                        headers={"Authorization": f"Bearer {token1}"})

    assert response1.status_code == 404