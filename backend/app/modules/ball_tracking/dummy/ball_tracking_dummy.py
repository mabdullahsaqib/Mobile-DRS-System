import random

def ball_tracking_dummy(duration_sec=15, fps=30):
    num_frames = int(duration_sec * fps)
    output = []

    for i in range(num_frames):
        timestamp = i / fps

        # Every 30th frame has the ball
        ball = []
        if i >= 90 and i <= 120:
            ball = [{
                "bbox": [random.randint(950, 1000), random.randint(950, 1000), 30, 30],
                "confidence": 1.0,
                "center": [1014, 1007],
                "radius": 15,
                "z": round(1.2 + (i - 90) * 0.01, 2)
            }]

        # Simple static stumps
        stumps = [{
            "bbox": [969, 491, 93, 262],
            "confidence": 1.0
        }]

        # Dummy batsman with low confidence every 20th frame
        batsman = []
        if i % 20 == 0:
            batsman = [{
                "bbox": [850, 150, 320, 630],
                "confidence": round(random.uniform(0.5, 0.6), 3)
            }]

        frame_data = {
            "frame_id": i,
            "timestamp": round(timestamp, 6),
            "detections": {
                "ball": ball,
                "stumps": stumps,
                "batsman": batsman,
                "bat": [],
                "pads": []
            },
            "ball_trajectory": {
                "current_position": {"x": 0.075, "y": -1.15 + i * -0.01, "z": 1.33},
                "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
                "acceleration": {"x": 0.0, "y": -9.8, "z": 0.0},
                "spin": {
                    "axis": {"x": 0.12, "y": 0.96, "z": 0.24},
                    "rate": 25.5
                },
                "detection_confidence": 1.0,
                "historical_positions": []
            }
        }

        output.append(frame_data)

    return output
