"""
Stream Analysis and Overlay Module (Module 6)
--------------------------------------------
Processes ball tracking data and renders broadcast-style overlays including:
- Ball trajectory path
- Bounce/impact markers
- Umpire decision graphics
"""

import cv2
import numpy as np
from pathlib import Path

class StreamOverlay:
    def __init__(self):
        """Initialize the overlay generator with output directories"""
        # Set up output directory structure
        self.output_dir = Path("output/augmented_frames")
        self.output_dir.mkdir(exist_ok=True, parents=True)  # Create if doesn't exist
        
        # Frame counter for naming
        self.frame_count = 0

    def process_frame(self, frame, ball_positions, decision_data, total_frames):
        """
        Process a single frame with all visual overlays
        Args:
            frame: Current video frame from Module 1 (numpy array)
            ball_positions: List of [x, y, z] ball positions from Module 2
            decision_data: Contains 'decision' and 'pitching_zone' from Module 5
            total_frames: Total frames in sequence for decision timing
        """
        # Standardize frame to HD resolution (1280x720) for broadcast compatibility
        frame = cv2.resize(frame, (1280, 720))

        # Convert ball positions from (x, y, z) to 2D (x, y) for overlay
        # For simplicity, we're ignoring z for now and using (x, y) directly
        projected_positions = [[int(pos[0]), int(pos[1])] for pos in ball_positions]

        # Detect bounce point (where z is closest to 0)
        bounce_idx = np.argmin([pos[2] for pos in ball_positions])
        bounce_point = {"x": int(ball_positions[bounce_idx][0]), "y": int(ball_positions[bounce_idx][1])}

        # Impact point is the last position (near stumps)
        impact_point = {"x": int(ball_positions[-1][0]), "y": int(ball_positions[-1][1])}

        # 1. TRAJECTORY LINE (Green)
        if len(projected_positions) > 1:
            for i in range(1, len(projected_positions)):
                cv2.line(frame, 
                         tuple(projected_positions[i-1]), 
                         tuple(projected_positions[i]), 
                         (0, 255, 0),  # Green
                         2, cv2.LINE_AA)  # Anti-aliased
        
        # 2. BOUNCE MARKER (Yellow circle)
        cv2.circle(frame, 
                  (bounce_point["x"], bounce_point["y"]), 
                  8,  # Radius
                  (0, 255, 255),  # Yellow
                  -1)  # Filled
        
        # 3. IMPACT MARKER (Red ring)
        cv2.circle(frame, 
                  (impact_point["x"], impact_point["y"]), 
                  10,  # Radius
                  (0, 0, 255),  # Red
                  2)  # Thickness
        
        # 4. DECISION OVERLAY (Last 20% frames only)
        if self.frame_count > 0.8 * total_frames:
            # Black background box
            cv2.rectangle(frame, 
                         (1000, 20),  # Top-left
                         (1200, 80),  # Bottom-right
                         (0, 0, 0),  # Black
                         -1)  # Filled
            
            # Decision text (red=OUT, green=NOT OUT)
            color = (0, 0, 255) if decision_data["decision"] == "OUT" else (0, 255, 0)
            cv2.putText(frame, 
                       decision_data["decision"], 
                       (1050, 60),  # Position
                       cv2.FONT_HERSHEY_DUPLEX,  # Professional font
                       1.5,  # Font scale
                       color, 
                       2)  # Thickness
        
        # Save frame with zero-padded filename (e.g., frame_0085.png)
        output_path = self.output_dir / f"frame_{self.frame_count:04d}.png"
        cv2.imwrite(str(output_path), frame)
        self.frame_count += 1

    def reset(self):
        """Reset frame counter for a new sequence"""
        self.frame_count = 0

def main():
    """Entry point for standalone testing with mock data"""
    try:
        processor = StreamOverlay()

        # Mock data for testing
        num_frames = 100
        # Simulate ball positions (x, y, z) moving across the pitch
        ball_positions = [[200 + i*8, 500 - 0.002 * (200 + i*8 - 600)**2, 100 - i] for i in range(num_frames)]
        decision_data = {"decision": "OUT", "pitching_zone": "OUTSIDE_OFF"}

        # Load a sample frame for testing (replace with real frame input in production)
        frame = cv2.imread("input/straight_view.jpg")
        if frame is None:
            raise FileNotFoundError("Required background image not found at input/straight_view.jpg")

        # Process each frame
        for _ in range(num_frames):
            # In a real scenario, ball_positions would grow frame by frame
            processor.process_frame(frame, ball_positions[:processor.frame_count + 1], decision_data, num_frames)

        print("Successfully generated 100 test frames in:")
        print(f"→ {processor.output_dir.resolve()}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Troubleshooting:")
        print("1. Verify input/straight_view.jpg exists")
        print("2. Check output directory permissions")

if __name__ == "__main__":
    main()