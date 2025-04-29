import cv2
import numpy as np
import base64


from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def process_frame(frame_data, predicted_path, is_out):
    # Convert base64 frame to an image
    image = Image.open(BytesIO(frame_data))
    draw = ImageDraw.Draw(image)

    # Example: Add trajectory line (dummy)
    for point in predicted_path:
        # Access position attributes correctly (assuming position is a dictionary with x, y, z)
        x = point.position['x']
        y = point.position['y']
        draw.line([x, y, x+10, y+10], fill="red", width=2)  # Draw line (dummy logic)

    # Example: Add "OUT" or "NOT OUT" text
    decision_text = "OUT" if is_out else "NOT OUT"
    draw.text((10, 10), decision_text, fill="white")
    
    # Convert image back to base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    return img_data

# def process_frame(frame, predicted_path, is_out):
#     # Decode the base64 image data to a format OpenCV can work with
#     img = base64_to_cv2_image(frame.data)

#     # Apply overlay for trajectory and decision text
#     trajectory_path = adjust_trajectory_for_camera(predicted_path, frame.resolution)
#     frame_with_overlay = draw_overlay(img, trajectory_path, "OUT" if is_out else "NOT OUT")
    
#     # Return the frame with the overlay as base64
#     return cv2_image_to_base64(frame_with_overlay)

def adjust_trajectory_for_camera(predicted_path, resolution):
    # Adjust the trajectory coordinates based on the resolution
    scaled_path = []
    for point in predicted_path:
        scaled_x = int(point[0] * resolution[0] / 100)  # Example scaling factor
        scaled_y = int(point[1] * resolution[1] / 100)
        scaled_path.append([scaled_x, scaled_y])
    return scaled_path

def draw_overlay(frame, trajectory_path, decision_text):
    # Draw the ball trajectory as a red circle at each predicted point
    for point in trajectory_path:
        cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)  # Red circles

    # Add decision text ("OUT" or "NOT OUT")
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, decision_text, (50, 50), font, 1, (255, 255, 255), 2)
    return frame

def base64_to_cv2_image(base64_data):
    # Convert base64 image to OpenCV format (NumPy array)
    img_data = base64.b64decode(base64_data)
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def cv2_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode("utf-8")
