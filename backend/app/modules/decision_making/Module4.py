from fastapi import FastAPI

app = FastAPI()

@app.get("/module4_combined_data")
async def get_combined_data():
    # This is the combined data returned by the GET endpoint
    data = {
    "ball_trajectory": {
        "positions": [
            {"x": 4, "y": 1.2, "z": 5.0},
            {"x": 5, "y": 0.9, "z": 5.2},
            {"x": 6, "y": 0.6, "z": 5.0},
            {"x": 7, "y": 0.3, "z": 4.7},
            {"x": 8, "y": 0.01, "z": 4.5}  # Impact point: x = 8, z = 4.5
        ]
    },
    "stumps_data": {
        "position": {
            "base_center": {"x": 8}
        },
        "individual_stumps": [
            {"top_position": {"x": 8, "y": 0.71, "z": 6.7}},
            {"top_position": {"x": 8, "y": 0.71, "z": 6.8}},
            {"top_position": {"x": 8, "y": 0.71, "z": 6.9}}
        ]
    },
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
    ],
    "original_frames": [
        "base64encodedframe1",
        "base64encodedframe2"
    ],
    "predicted_path": [
        [10.5, 5.3, 1.2],
        [11.0, 5.5, 1.3],
        [11.5, 5.7, 1.4]
    ],
    "will_hit_stumps": True
}


    return data