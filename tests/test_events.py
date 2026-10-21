"""
Tests for the events API/table
"""


def test_get_events_returns_200_and_proper_format(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert "events" in response.json()
    
    events = response.json()["events"]
    assert isinstance(events, list)
    assert all(key in ["id", "title", "starts_at", "ends_at", "location"] for key in events[0].keys())


def test_get_events_returns_correct_data(client, sample_event):
    response = client.get("/api/events")
    events = response.json()["events"]
    assert any(event["id"] == sample_event for event in events), "Not fetching correct event data!"
