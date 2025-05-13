import json
import base64
from pathlib import Path
import cv2
import numpy as np
from overlay_utils import  stream_analysis  #  overlay logic
#from stream import StreamOverlay  # Assuming this is the correct import path
# Function to simulate the generation of frames based on a background img

def generate_frames_from_background(num_frames=50, background_image_path="input/straight_view.jpg"):
    # Load the background image
    background = cv2.imread(background_image_path)
    if background is None:
        raise FileNotFoundError(f"Background image not found at {background_image_path}")
    
    frames = []
    for i in range(num_frames):
        frame = background.copy()  # Create  copy of the background img
        # Update ball position dynamically
        ball_position_x = int(100 + i * 10)  # Ball moves in x-dir
        cv2.circle(frame, (ball_position_x, 300), 20, (0, 255, 0), -1)  # Draw the moving ball
        
        # Convert frame to base64
        _, buffer = cv2.imencode(".jpg", frame)
        frame_base64 = base64.b64encode(buffer).decode("utf-8")
        frames.append({"frameData": frame_base64})
    
    return frames
# Function to simulate ball trajectory data
def generate_ball_positions(num_positions=50):
    ball_positions = []
    for i in range(num_positions):
        ball_positions.append({
            "ball_trajectory": {
                "current_position": {
                    "x": 0.1 * i,  # Ball moves slightly in x-direction
                    "y": 20 - i * 4,  # Ball is approaching stumps in y-direction
                    "z": 0.5 + 0.1 * i  # Simulating bounce arc in z-direction
                }
            }
        })
    return ball_positions

# Simulate the decision data (e.g., 'OUT' or 'NOT OUT')
def generate_decision_data():
    return {"Out": True, "Reason": "Ball hit pad in line"}

# Main func to run the test
def main():
    try:
        # Path to the background img
        background_image_path = "input/straight_view.jpg"

        # Step 1: Generate frames based on background image
        dummy_frames = generate_frames_from_background(num_frames=50, background_image_path=background_image_path)

        # Step 2: Generate simulated ball trajectory data
        ball_positions = generate_ball_positions(num_positions=50)

        # Step 3: Generate mock decision data (e.g., OUT decision)
        decision_data = generate_decision_data()

        # Step 4: Run stream analysis (overlay the ball trajectory and decision on frames)
        video_base64 = stream_analysis(dummy_frames, ball_positions, decision_data)

        # Step 5: Save the output as a base64-decoded MP4 video file
        with open("augmented_video.mp4", "wb") as f:
            f.write(base64.b64decode(video_base64))
        
        print("✅ Test completed successfully. Output saved as augmented_video.mp4")

    except Exception as e:
        print("❌ Error during processing:")
        print(str(e))
        print("📌 Troubleshooting:")
        print("1. Ensure 'input/straight_view.jpg' exists")
        print("2. Ensure all paths and data structures are correct.")
        print("3. Ensure 'overlay_utils.py' is imported correctly.")

if __name__ == "__main__":
    main()
