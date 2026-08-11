from fastapi.testclient import TestClient
import pytest
from app.main import app
from scripts.seed_trails import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    seed_database()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_trails():
    response = client.get("/api/v1/trails")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    trail_ids = [t["trail_id"] for t in data]
    assert "trail_jalan_kledang" in trail_ids
    assert "trail_jalan_bukit_larut" in trail_ids


def test_get_trail_pack_and_checksum_verification():
    response = client.get("/api/v1/trails/trail_jalan_kledang/pack")
    assert response.status_code == 200
    pack = response.json()
    
    assert pack["schema_version"] == "trail-pack-v1"
    assert pack["trail_id"] == "trail_jalan_kledang"
    assert "integrity" in pack
    assert pack["integrity"]["algorithm"] == "sha256"
    assert len(pack["integrity"]["checksum"]) == 64
    
    # Check risk classes in segments
    segments = pack["segments"]
    assert len(segments) >= 2
    assert segments[0]["risk_class"] in ["likely_covered", "uncertain", "predicted_gap"]
    assert segments[1]["risk_class"] == "predicted_gap"
    assert segments[1]["warning_eligible"] is True


def test_get_nonexistent_trail_pack():
    response = client.get("/api/v1/trails/nonexistent_trail/pack")
    assert response.status_code == 404
