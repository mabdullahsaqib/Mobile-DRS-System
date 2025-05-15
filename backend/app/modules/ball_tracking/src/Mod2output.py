import json

def get_detections_by_type(detection_type):
    with open('output.json', 'r') as file:
        frames_data = json.load(file)
    
    filtered_detections = []

    for frame in frames_data:
        objects = frame.get("detections", {}).get(detection_type, [])
        for obj in objects:
            filtered_detections.append({
                "frame_id": frame["frame_id"],
                "timestamp": frame["timestamp"],
                "batsman_position": frame["batsman_position"],
                "detection_type": detection_type,
                "details": obj
            })

    return filtered_detections
