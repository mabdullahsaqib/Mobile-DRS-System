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
        """Initialize the overlay generator with output directories and background image"""
        # Set up output directory structure
        self.output_dir = Path("output/augmented_frames")
        self.output_dir.mkdir(exist_ok=True, parents=True)  # Create if doesn't exist
        
        # Load and preprocess background image
        self.background = cv2.imread("input/straight_view.jpg")
        if self.background is None:
            raise FileNotFoundError("Required background image not found at input/straight_view.jpg")
        
        # Standardize to HD resolution (1280x720) for broadcast compatibility
        self.background = cv2.resize(self.background, (1280, 720))

    def generate_test_frames(self, num_frames=100):
        """
        Generate synthetic test frames when real data is unavailable
        Args:
            num_frames: Number of frames to generate (default 100 = 3.3sec @30FPS)
        """
        # Synthetic ball trajectory data (parabolic path)
        module2_data = {
            "ball_positions": self._generate_ball_path(num_frames),
            "bounce_point": {"x": 800, "y": 400},  # 60% down pitch
            "impact_point": {"x": 900, "y": 350}   # Near stumps
        }
        
        # Mock decision data
        module5_data = {
            "decision": "OUT",  # or "NOT OUT"
            "pitching_zone": "OUTSIDE_OFF"  # "LINE"/"LEG"
        }

        # Generate each frame
        for frame_id in range(num_frames):
            self.process_frame(
                ball_positions=module2_data["ball_positions"][:frame_id+1],
                bounce_point=module2_data["bounce_point"],
                impact_point=module2_data["impact_point"],
                decision_data=module5_data,
                frame_id=frame_id,
                total_frames=num_frames
            )

    def _generate_ball_path(self, num_frames):
        """
        Generate realistic cricket ball trajectory
        Args:
            num_frames: Length of trajectory in frames
        Returns:
            List of [x,y] positions forming a parabolic path
        """
        x = np.linspace(200, 1000, num_frames)  # From bowler (left) to stumps (right)
        y = 500 - 0.002 * (x - 600)**2  # Physics-based parabola
        return [[int(x[i]), int(y[i])] for i in range(num_frames)]

    def process_frame(self, ball_positions, bounce_point, impact_point, decision_data, frame_id, total_frames):
        """
        Process a single frame with all visual overlays
        Args:
            ball_positions: List of historical [x,y] ball positions
            bounce_point: Dict with 'x','y' bounce coordinates
            impact_point: Dict with 'x','y' impact coordinates
            decision_data: Contains 'decision' and 'pitching_zone'
            frame_id: Current frame number (0-indexed)
            total_frames: Total frames in sequence
        """
        frame = self.background.copy()
        
        # 1. TRAJECTORY LINE (Green)
        if len(ball_positions) > 1:
            for i in range(1, len(ball_positions)):
                cv2.line(frame, 
                        tuple(ball_positions[i-1]), 
                        tuple(ball_positions[i]), 
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
        if frame_id > 0.8 * total_frames:
            # Black background box
            cv2.rectangle(frame, 
                         (1000, 20),  # Top-left
                         (1200, 80),   # Bottom-right
                         (0, 0, 0),    # Black
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
        output_path = self.output_dir / f"frame_{frame_id:04d}.png"
        cv2.imwrite(str(output_path), frame)

def main():
    """Entry point for standalone testing"""
    try:
        processor = StreamOverlay()
        processor.generate_test_frames(100)  # 100 frames = 3.3sec @30FPS
        print("Successfully generated 100 test frames in:")
        print(f"→ {processor.output_dir.resolve()}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Troubleshooting:")
        print("1. Verify input/straight_view.jpg exists")
        print("2. Check output directory permissions")

if __name__ == "__main__":
    main()
