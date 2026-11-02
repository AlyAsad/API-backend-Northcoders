from db.connection import get_connection

def test_get_organiser_stats_returns_correct_data(client, sample_rsvp, sample_user2, sample_venue):
    user = sample_rsvp[1]
    organiser_id = user[0]
    other_organiser_id = sample_user2[0]

    conn = get_connection()
    created_event_ids = []

    with conn.cursor() as cursor:
        # creating a second event for the target organiser (zero RSVPs)
        cursor.execute(
            """
            INSERT INTO events (
                title, description, starts_at, ends_at,
                organiser_id, venue_id
            )
            VALUES (
                'second_event', 'description',
                '2026-07-18T18:30:00+01:00',
                '2026-07-18T21:00:00+01:00',
                %s, %s
            )
            RETURNING id
            """,
            (organiser_id, sample_venue)
        )
        created_event_ids.append(cursor.fetchone()[0])

        # Give another organiser three events
        for i in range(3):
            cursor.execute(
                """
                INSERT INTO events (
                    title, description, starts_at, ends_at,
                    organiser_id, venue_id
                )
                VALUES (
                    %s, 'description',
                    '2026-08-18T18:30:00+01:00',
                    '2026-08-18T21:00:00+01:00',
                    %s, %s
                )
                RETURNING id
                """,
                (f'other_event_{i}', other_organiser_id, sample_venue)
            )
            created_event_ids.append(cursor.fetchone()[0])

    conn.commit()

    try:
        response = client.get(
            f"/api/organisers/{organiser_id}/stats"
        )

        assert response.status_code == 200
        assert "stats" in response.json()

        stats = response.json()["stats"]

        assert stats["organiser_id"] == organiser_id
        assert stats["name"] == "sample_user"
        assert stats["total_events"] == 2
        assert stats["avg_attendance"] == 0.5
        assert stats["best_attended_count"] == 1

        # checking ranking against another organiser
        other_response = client.get(
            f"/api/organisers/{other_organiser_id}/stats"
        )

        other_stats = other_response.json()["stats"]

        assert other_stats["organiser_rank"] < stats["organiser_rank"]

    finally:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM events WHERE id = ANY(%s)",
                (created_event_ids,)
            )

        conn.commit()
        conn.close()


def test_get_organiser_stats_nonexistent_returns_404(client):
    response = client.get("/api/organisers/999999999/stats")

    assert response.status_code == 404


def test_get_organiser_stats_no_events_returns_404(client, sample_user):
    response = client.get(f"/api/organisers/{sample_user[0]}/stats")

    assert response.status_code == 404