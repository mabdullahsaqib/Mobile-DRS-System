import cv2
import os

# Configuration
FRAME_DIR = "output/augmented_frames"
OUTPUT_VIDEO = "output/output_video.mp4"
FPS = 30

# Get all frames
frames = sorted([f for f in os.listdir(FRAME_DIR) if f.endswith(".png")])
if not frames:
    print(f"Error: No frames found in {FRAME_DIR}!")
    print("Run stream.py first to generate frames")
    exit()

# Get frame size from first frame
sample = cv2.imread(os.path.join(FRAME_DIR, frames[0]))
height, width = sample.shape[:2]

# Create video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (width, height))

# Add all frames to video
for frame_file in frames:
    frame_path = os.path.join(FRAME_DIR, frame_file)
    frame = cv2.imread(frame_path)
    if frame is not None:
        video.write(frame)

video.release()
print(f"🎥 Video saved as {OUTPUT_VIDEO}")