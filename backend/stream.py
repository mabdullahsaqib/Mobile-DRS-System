import cv2
import numpy as np
import os

# ===== 1. CONFIGURATION =====
OUTPUT_DIR = "output/augmented_frames"
BG_IMAGE = "straight_view.jpg"  # Your pitch image
NUM_FRAMES = 90  # 3-second video at 30FPS

# ===== 2. PITCH COORDINATES =====
# Adjust these to match your image's perspective
BOWLER_X = 100    # Starting x (left side)
BOWLER_Y = 300    # Starting y (bottom)
STUMPS_X = 500    # Stumps x (right side)
STUMPS_Y = 100    # Stumps y (top)
BOUNCE_X = 300    # Where ball pitches

# ===== 3. REALISTIC TRAJECTORY =====
def calculate_trajectory():
    """Generates physics-based trajectory:
    - Starts bottom-left (bowler's hand)
    - Moves diagonally upward to stumps
    - Natural bounce at BOUNCE_X"""
    x = np.linspace(BOWLER_X, STUMPS_X, NUM_FRAMES)
    
    # Phase 1: Bowler to bounce (parabolic)
    pre_bounce = x <= BOUNCE_X
    y_pre = BOWLER_Y - 0.002 * (x[pre_bounce] - BOWLER_X)**2
    
    # Phase 2: Bounce to stumps (linear rise)
    post_bounce = x > BOUNCE_X
    y_post = (STUMPS_Y + 50) - 0.3 * (x[post_bounce] - BOUNCE_X)
    
    return x.astype(int), np.concatenate((y_pre, y_post)).astype(int)

# ===== 4. GENERATE FRAMES =====
bg = cv2.imread(BG_IMAGE)
x_pos, y_pos = calculate_trajectory()

for frame_id in range(NUM_FRAMES):
    frame = bg.copy()
    x, y = x_pos[frame_id], y_pos[frame_id]
    
    # Draw trajectory (light blue)
    if frame_id > 0:
        prev_x, prev_y = x_pos[frame_id-1], y_pos[frame_id-1]
        cv2.line(frame, (prev_x, prev_y), (x, y), (200, 200, 255), 2)
    
    # Draw ball (red with white seam)
    cv2.circle(frame, (x, y), 8, (255, 255, 255), -1)  # White base
    cv2.circle(frame, (x, y), 6, (0, 0, 255), -1)      # Red cover
    cv2.line(frame, (x-5, y), (x+5, y), (255,255,255), 1)  # Seam
    
    # Add decision (last 10 frames)
    if frame_id >= NUM_FRAMES - 10:
        cv2.putText(frame, "OUT", (STUMPS_X-50, STUMPS_Y+30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.imwrite(f"{OUTPUT_DIR}/frame_{frame_id:03d}.png", frame)

print(f"✅ Generated {NUM_FRAMES} frames with bowler's perspective")
