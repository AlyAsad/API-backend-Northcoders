"""
Tests for the events API/table
"""


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