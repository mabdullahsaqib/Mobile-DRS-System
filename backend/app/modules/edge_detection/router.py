import math

def calculate_distance(p1, p2):
    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2 +
        (p1[2] - p2[2]) ** 2
    )

def edge_detection(data: dict) -> dict:
    if not data['detections']['ball'] or not data['detections']['bat']:
        return {"is_edge_detected": False, "reason": "No ball or bat detected"}

    # Take the first ball and bat detections
    ball = data['detections']['ball'][0]
    bat = data['detections']['bat'][0]

    ball_center = ball['center']  # [x, y]
    ball_z = ball['z']
    ball_radius = ball['radius']

    bat_bbox = bat['bbox']  # {"x": ..., "y": ..., "width": ..., "height": ...}
    bat_z = bat['z']

    # Ball edge point in 3D
    ball_edge_point = (ball_center[0], ball_center[1], ball_z - ball_radius)

    # Sample bat edge + center points
    bat_edge_points_2d = sample_bat_edge_points(bat_bbox, step=1)
    bat_edge_points_3d = [(x, y, bat_z) for (x, y) in bat_edge_points_2d]

    # Calculate distances
    distances = [
        calculate_distance(ball_edge_point, bat_point)
        for bat_point in bat_edge_points_3d
    ]
    min_distance = min(distances)
    nearest_bat_point = bat_edge_points_3d[distances.index(min_distance)]

    threshold = bat_bbox['width'] // 2
    is_edge = min_distance < threshold

    return {
        "is_edge_detected": is_edge,
        "min_distance": min_distance,
        "ball_edge_point": ball_edge_point,
        "nearest_bat_point": nearest_bat_point
    }

def sample_bat_edge_points(bbox: dict, step=1):
    points = []
    # Top and bottom edges
    for x in range(bbox['x'], bbox['x'] + bbox['width'] + 1, step):
        points.append((x, bbox['y']))  # Top edge
        points.append((x, bbox['y'] + bbox['height']))  # Bottom edge

    # Left and right edges
    for y in range(bbox['y'], bbox['y'] + bbox['height'] + 1, step):
        points.append((bbox['x'], y))  # Left edge
        points.append((bbox['x'] + bbox['width'], y))  # Right edge

    # Vertical center line
    center_x = bbox['x'] + bbox['width'] // 2
    for y in range(bbox['y'], bbox['y'] + bbox['height'] + 1, step):
        points.append((center_x, y))

    return points


# if __name__ == "__main__":
#     sample_data = {
#         "detections": {
#             "ball": [{
#                 "center": [110, 130],
#                 "z": 50,
#                 "radius": 3
#             }],
#             "bat": [{
#                 "bbox": {
#                     "x": 100,
#                     "y": 120,
#                     "width": 20,
#                     "height": 60
#                 },
#                 "z": 50
#             }]
#         }
#     }

#     result = edge_detection(sample_data)
#     print("Edge Detection Result:")
#     for k, v in result.items():
#         print(f"{k}: {v}")