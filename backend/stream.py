import cv2
import numpy as np
import os

# ----------------------------
# Configurations
# ----------------------------
NUM_FRAMES = 100
FRAME_WIDTH, FRAME_HEIGHT = 640, 360
DECISION_TEXT = "OUT"  # Change to "NOT OUT" for alternate result
output_dir = "augmented_frames"
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Generate Dummy Ball Positions (like a curved trajectory)
# ----------------------------
np.random.seed(42)
ball_positions = [(int(FRAME_WIDTH * i / NUM_FRAMES), int(180 + 50 * np.sin(i / 10))) for i in range(NUM_FRAMES)]

# ----------------------------
# Generate Blank Frame in Base64
# ----------------------------
def generate_blank_frame():
    frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    pil_img = Image.fromarray(frame)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    base64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_img

# ----------------------------
# Simulated Frame Data
# ----------------------------
frame_data_list = [{
    "frame_id": i,
    "timestamp": f"00:00:{i:02}",
    "base64_image": generate_blank_frame(),
    "ball_position": ball_positions[i]
} for i in range(NUM_FRAMES)]

# ----------------------------
# Decode Base64 to OpenCV Image
# ----------------------------
def decode_base64_to_frame(base64_str):
    image_data = base64.b64decode(base64_str)
    np_arr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame

# ----------------------------
# Draw Trajectory and Decision Overlay
# ----------------------------
def augment_frames_with_trajectory_and_decision(frame_data_list, decision_text):
    augmented_frames = []
    positions_drawn = []

    for frame_data in frame_data_list:
        frame = decode_base64_to_frame(frame_data["base64_image"])
        ball_pos = frame_data["ball_position"]
        positions_drawn.append(ball_pos)

        # Draw trajectory line
        overlay = frame.copy()
        for i in range(1, len(positions_drawn)):
            cv2.line(overlay, positions_drawn[i - 1], positions_drawn[i], (0, 255, 255), 2)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw current ball point
        cv2.circle(frame, ball_pos, 5, (0, 0, 255), -1)

        # Add decision text on the last few frames
        if frame_data["frame_id"] >= NUM_FRAMES - 10:
            cv2.putText(frame, f"Decision: {decision_text}", (30, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0) if decision_text == "NOT OUT" else (0, 0, 255), 3)

        augmented_frames.append(frame)

    return augmented_frames

# ----------------------------
# Run the Augmentation and Save Frames
# ----------------------------
augmented_frames = augment_frames_with_trajectory_and_decision(frame_data_list, DECISION_TEXT)

for i, frame in enumerate(augmented_frames):
    path = os.path.join(output_dir, f"frame_{i:03}.png")
    cv2.imwrite(path, frame)

print(f"✅ Saved {NUM_FRAMES} augmented frames with trajectory and decision overlay in '{output_dir}/'")
import cv2
import os

# Folder with your saved frames
frame_folder = "augmented_frames"
video_filename = "final_output.mp4"

# Get list of frame files sorted in order
frames = sorted([f for f in os.listdir(frame_folder) if f.endswith(".png")])

# Get frame size from the first frame
sample_frame = cv2.imread(os.path.join(frame_folder, frames[0]))
height, width, _ = sample_frame.shape

# Define video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(video_filename, fourcc, 30, (width, height))

# Add all frames to the video
for frame_file in frames:
    frame = cv2.imread(os.path.join(frame_folder, frame_file))
    video.write(frame)

video.release()
print(f"🎬 Video saved as '{video_filename}'")
