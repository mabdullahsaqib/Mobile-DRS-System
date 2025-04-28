from fastapi.testclient import TestClient
from check_ball_inline import app 

# Create a TestClient instance
client = TestClient(app)

# Sample input data for the request
data = {
    "frame_id": 1542,
    "timestamp": "2025-04-02T11:02:47.123Z",
    "processing_timestamp": "2025-04-02T11:02:47.150Z",
    "delivery_id": "2025040201-D127",
    "match_id": "IPL2025-M042",
    "edge_detected": True,
    "contact_type": "glancing_edge",
    "contact_point": {
        "x": 10.65,
        "y": 0.7,
        "z": 0.22
    },
    "impact_angle": 12.5,
    "updated_trajectory": [
        {
            "x": 11.0,
            "y": 0.8,
            "z": 0.25,
            "velocity": {
                "x": -15.2,
                "y": 3.1,
                "z": -0.8
            }
        },
        {
            "x": 11.5,
            "y": 0.6,
            "z": 0.3,
            "velocity": {
                "x": -14.0,
                "y": 2.8,
                "z": -0.7
            }
        }
    ],
    "deviation_from_original": 8.2,
    "edge_detection_confidence": 0.92,
    "trajectory_adjustment_confidence": 0.88,
    "error_flags": [
        {
            "code": "WIND_INFLUENCE",
            "severity": "low"
        },
        {
            "code": "PARTIAL_OCCLUSION",
            "severity": "medium"
        },
        {
            "code": "TOO_MUCH_NOISE",
            "severity": "high"
        }
    ]
}

# Send a POST request to the FastAPI endpoint using TestClient
response = client.post("/bat_edge_detect", json=data)

# Print the response from the server
if response.status_code == 200:
    print("Response from server:", response.json())
else:
    print(f"Failed to get response, status code: {response.status_code}")
