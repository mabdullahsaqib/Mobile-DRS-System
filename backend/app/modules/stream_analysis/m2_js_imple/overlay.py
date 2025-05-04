import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import os
from .models import FrameDetection

# Load base image once (at the top)
BASE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "straight_view.jpg")
base_image = cv2.imread(BASE_IMAGE_PATH)

if base_image is None:
    raise FileNotFoundError(f"Base image not found at {BASE_IMAGE_PATH}")

def process_frame(frame: FrameDetection) -> np.ndarray:
    # Clone the base image to draw on it
    img = base_image.copy()

    # Draw stumps in blue
    for stump in frame.detections.stumps:
        x, y, w, h = stump.bbox
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(img, f"Stump {stump.confidence:.2f}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Draw ball in red
    for ball in frame.detections.ball:
        x, y, w, h = ball.bbox
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(img, f"Ball {ball.confidence:.2f}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"frame_{frame.frame_id}.jpg")
    cv2.imwrite(output_path, img)

    return img
