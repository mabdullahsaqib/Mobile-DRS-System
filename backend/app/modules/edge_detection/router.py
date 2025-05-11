import math
import json
from modules.edge_detection.controllers.audio_detection import drs_system_pipeline
from typing import List, Dict

def calculate_distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2 +
        (p1[2] - p2[2]) ** 2
    )

def get_audio_base64_list(input_json_path, skip_empty=True):
    with open(input_json_path, 'r') as f:
        data = json.load(f)

    audio_list = []

    for frame in data.get("results", []):
        audio_b64 = frame.get("audioData", "")
        if skip_empty and not audio_b64:
            continue
        audio_list.append(audio_b64)

    return audio_list

def edge_detection(frames: List[Dict], file_path:str) -> Dict:
    results = {}
    c=0

    for frame in frames:
        frame_id = frame.get("frame_id")
        timestamp = frame.get("timestamp")

        if not frame['detections']['ball'] or not frame['detections']['bat']:
            results = {
                "frame_id": frame_id,
                "timestamp": timestamp,
                "is_edge_detected": False,
                "reason": "No ball or bat detected"
            }
            continue

        ball = frame['detections']['ball'][0]
        bat = frame['detections']['bat'][0]

        ball_center = ball['center']
        ball_z = ball['z']
        ball_radius = ball['radius']
        ball_edge_point = (ball_center[0], ball_center[1], ball_z - ball_radius)

        bat_bbox = bat['bbox']  # This is now a list
        bat_z = bat['z']


        bat_edge_points_2d = sample_bat_edge_points(bat_bbox, step=1)
        bat_edge_points_3d = [(x, y, bat_z) for (x, y) in bat_edge_points_2d]

        distances = [
            calculate_distance(ball_edge_point, bat_point)
            for bat_point in bat_edge_points_3d
        ]
        min_distance = min(distances)
        nearest_bat_point = bat_edge_points_3d[distances.index(min_distance)]

        threshold = bat_bbox[2] // 2  # Width is at index 2
        is_edge = min_distance < threshold
        
        if is_edge:
            results={
                "frame_id": frame_id,
                "timestamp": timestamp,
                "is_edge_detected": is_edge,
                "min_distance": min_distance,
                "ball_edge_point": ball_edge_point,
                "nearest_bat_point": nearest_bat_point
                }
            break
        else:
            if c ==0:
                results={
                    "is_edge_detected": is_edge,
                    "min_distance": min_distance,
                    "ball_edge_point": ball_edge_point,
                    "nearest_bat_point": nearest_bat_point
                        }
                c=1



    audio_chunks = get_audio_base64_list(file_path)
    for i in audio_chunks:
        decision = drs_system_pipeline(i)
        if decision=='Out': 
            break
    results["audio_decision"]=decision

    return results
    


def sample_bat_edge_points(bbox: list, step=1):
    points = []
    x, y, width, height = bbox  # Unpack the list into variables

    # Top and bottom edges
    for x_coord in range(x, x + width + 1, step):
        points.append((x_coord, y))  # Top edge
        points.append((x_coord, y + height))  # Bottom edge

    # Left and right edges
    for y_coord in range(y, y + height + 1, step):
        points.append((x, y_coord))  # Left edge
        points.append((x + width, y_coord))  # Right edge

    # Vertical center line
    center_x = x + width // 2
    for y_coord in range(y, y + height + 1, step):
        points.append((center_x, y_coord))

    return points

