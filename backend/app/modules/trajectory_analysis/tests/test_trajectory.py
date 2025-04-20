
import pytest
from fastapi.testclient import TestClient
from main import app  

client = TestClient(app)

dummy = {
  "frame_id": 1,
  "timestamp": "2025-04-20T10:00:00Z",
  "delivery_id": "test-001",
  "match_id": "TEST-MATCH",
  "edge_detected": False,
  "ball_data": {
    "current_position": {"x":0,"y":1,"z":2},
    "velocity": {"x":10,"y":0,"z":-5},
    "spin": {"axis":{"x":0,"y":0,"z":1},"rate":15.0},
    "historical_positions": [
      {"x":0.5,"y":1.1,"z":2.1,"timestamp":"2025-04-20T09:59:59Z"}
    ]
  }
}

def test_process_frame():
    resp = client.post("/trajectory_analysis/process_frame", json=dummy)
    assert resp.status_code == 200
    data = resp.json()
    assert data["frame_id"] == 1
    assert "predicted_trajectory" in data
    assert isinstance(data["predicted_trajectory"], list)
