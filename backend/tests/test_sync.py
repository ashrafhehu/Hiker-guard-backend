from fastapi.testclient import TestClient
import uuid
from app.main import app

client = TestClient(app)


def test_idempotent_batch_sync():
    local_session_id = str(uuid.uuid4())
    event1_id = str(uuid.uuid4())
    event2_id = str(uuid.uuid4())

    payload = {
        "device_id": "test-device-123",
        "local_session_id": local_session_id,
        "events": [
            {
                "event_id": event1_id,
                "type": "location_point",
                "recorded_at": "2026-08-06T02:30:00Z",
                "payload": {
                    "latitude": 4.5892,
                    "longitude": 101.0621,
                    "horizontal_accuracy_m": 5.0,
                    "battery_level": 0.85,
                    "segment_id": "trail_jalan_kledang__s00000"
                }
            },
            {
                "event_id": event2_id,
                "type": "gap_warning_shown",
                "recorded_at": "2026-08-06T02:35:00Z",
                "payload": {
                    "segment_id": "trail_jalan_kledang__s00001",
                    "distance_to_gap_m": 550.0
                }
            }
        ]
    }

    # First Sync Attempt
    res1 = client.post("/api/v1/hikes/sync", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()

    assert "server_session_id" in data1
    assert set(data1["acknowledged_event_ids"]) == {event1_id, event2_id}
    assert len(data1["rejected_events"]) == 0

    # Second Sync Attempt with identical payload (Idempotency Check)
    res2 = client.post("/api/v1/hikes/sync", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["server_session_id"] == data1["server_session_id"]
    assert set(data2["acknowledged_event_ids"]) == {event1_id, event2_id}
    assert len(data2["rejected_events"]) == 0
