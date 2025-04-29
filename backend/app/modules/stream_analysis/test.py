import cv2
import os

# ===== 1. CONFIGURATION =====
FRAME_DIR = "output/augmented_frames"  # Directory containing individual frame images
OUTPUT_VIDEO = "output/output_video.mp4" # Output path for the final video
FPS = 30                                 # Frames per second for the vide

# ===== 2. LOAD FRAMES =====
# Collect all .png files in the frame directory and sort them
frames = sorted([f for f in os.listdir(FRAME_DIR) if f.endswith(".png")])
if not frames:
    print(f"Error: No frames found in {FRAME_DIR}!")
    print("Run stream.py first to generate frames")
    exit()

# ===== 3. GET VIDEO DIMENSIONS =====
# Read the first frame to get the frame size
sample = cv2.imread(os.path.join(FRAME_DIR, frames[0]))
height, width = sample.shape[:2]

# ===== 4. INITIALIZE VIDEO WRITER =====
fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for MP4
video = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (width, height))

# ===== 5. ADD FRAMES TO VIDEO =====
for frame_file in frames:
    frame_path = os.path.join(FRAME_DIR, frame_file)
    frame = cv2.imread(frame_path)
    if frame is not None:
        video.write(frame)
# ===== 6. CLEANUP =====
video.release()
print(f"🎥 Video saved as {OUTPUT_VIDEO}")
