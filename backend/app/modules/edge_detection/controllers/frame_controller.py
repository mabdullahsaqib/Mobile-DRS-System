# from modules.edge_detection.models.frame_model import EdgeDetectionInput
# import math

# def calculate_distance(pos1, pos2):
#     return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2 + (pos1.z - pos2.z)**2)

# def detect_edge(data: EdgeDetectionInput) -> dict:
#     ball_pos = data.ball_data.current_position
#     bat_edge_pos = data.bat_data.position.edge

#     distance = calculate_distance(ball_pos, bat_edge_pos)
#     threshold = 0.5  

#     is_edge = distance < threshold

#     return {
#         "is_edge_detected": is_edge,
#         "distance": distance
#     }
