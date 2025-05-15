import random

def ball_tracking_dummy(duration_sec=15, fps=30):
    num_frames = int(duration_sec * fps)
    output = []

    for i in range(num_frames):
        timestamp = round(i / fps, 6)

        # Add ball for frames 100 to 140
        ball = []
        if 10 <= i <= num_frames - 10:
            ball = [{
                "bbox": [998, 991, 31, 31],
                "confidence": 1.0,
                "center": [1014, 1007],
                "radius": 15,
                "z": round(3.0 + (i - 100) * 0.02, 2)
            }]

        # Static stumps
        stumps = [{
            "bbox": [967, 501, 99, 265],
            "confidence": 1.0
        }]

        # Every 20th frame has batsman and bat
        batsman = []
        bat = []
        if i % 20 == 0:
            confidence = round(random.uniform(0.5, 0.6), 3)
            bbox = [871, 162, 305, 609]
            batsman = [{
                "bbox": bbox,
                "confidence": confidence
            }]
            bat = [{
                "bbox": bbox,
                "confidence": confidence,
                "z": 3.46
            }]

        frame = {
            "frame_id": i,
            "timestamp": timestamp,
            "detections": {
                "ball": ball,
                "stumps": stumps,
                "batsman": batsman,
                "bat": bat,
                "pads": []
            },
            "ball_trajectory": {
                "current_position": {
                    "x": 0.075,
                    "y": round(-1.15 + i * -0.01, 3),
                    "z": 1.333
                },
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

        output.append(frame)

    return output
