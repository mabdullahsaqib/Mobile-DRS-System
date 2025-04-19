import numpy as np
import cv2
import base64
from PIL import Image
import io
import os


NUM_FRAMES = 100
FRAME_WIDTH, FRAME_HEIGHT = 640, 360
output_dir = "augmented_frames"
os.makedirs(output_dir, exist_ok=True)

# Generate dummy ball positions
np.random.seed(42)
ball_positions = [(int(FRAME_WIDTH * i / NUM_FRAMES), int(180 + 50 * np.sin(i / 10))) for i in range(NUM_FRAMES)]

# Function to create blank base64 frame
def generate_blank_frame():
    frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    pil_img = Image.fromarray(frame)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    base64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_img

# Simulate 100-frame data
frame_data_list = [{
    "frame_id": i,
    "timestamp": f"00:00:{i:02}",
    "base64_image": generate_blank_frame(),
    "resolution": (FRAME_WIDTH, FRAME_HEIGHT),
    "camera_position": "end-on",
    "role": "main_cam",
    "audio_info": "none",
    "base64_audio": "",
    "ball_position": ball_positions[i]
} for i in range(NUM_FRAMES)]

# Decode base64 to OpenCV image
def decode_base64_to_frame(base64_str):
    image_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame

# Augment frames with trajectory
def augment_frames_with_trajectory(frame_data_list):
    augmented_frames = []
    positions_drawn = []

    for frame_data in frame_data_list:
        frame = decode_base64_to_frame(frame_data["base64_image"])
        ball_pos = frame_data["ball_position"]
        positions_drawn.append(ball_pos)

        # Draw translucent trajectory
        overlay = frame.copy()
        for i in range(1, len(positions_drawn)):
            cv2.line(overlay, positions_drawn[i - 1], positions_drawn[i], (0, 255, 255), 2)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw current ball point
        cv2.circle(frame, ball_pos, 5, (0, 0, 255), -1)

        augmented_frames.append(frame)

    return augmented_frames

# Process and save frames
augmented_frames = augment_frames_with_trajectory(frame_data_list)

for i, frame in enumerate(augmented_frames):
    path = os.path.join(output_dir, f"frame_{i:03}.png")
    cv2.imwrite(path, frame)

print(f"Saved {NUM_FRAMES} augmented frames in '{output_dir}/'")
