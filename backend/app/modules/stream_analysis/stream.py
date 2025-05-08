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

    def project_3d_to_2d(self, x, y, z, frame_width=1280, frame_height=720):
        """
        Map 3D (x, y, z) to 2D (x, y) screen coordinates for a vertical pitch view
        Args:
            x, y, z: 3D coordinates (x=lateral, y=distance along pitch, z=height)
            frame_width, frame_height: Dimensions of the video frame
        Returns:
            Tuple (x_2d, y_2d) for screen coordinates
        """
        # Pitch view: y=0 (stumps) at top (y_2d=0), y=20 (bowler) at bottom (y_2d=720)
        y_2d = int((y / 20) * frame_height)  # Map y (0 to 20m) to screen y (0 to 720)
        
        # x_2d: Center at 640, adjust for lateral movement (x)
        # Positive x (off side) moves left in frame, negative x (leg side) moves right
        x_2d = int(frame_width / 2 + x * 50)  # Scale lateral movement
        
        return x_2d, y_2d

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

        # Project 3D ball positions to 2D screen coordinates
        projected_positions = []
        for pos in ball_positions:
            x_2d, y_2d = self.project_3d_to_2d(pos[0], pos[1], pos[2])
            projected_positions.append([x_2d, y_2d])

        # Detect bounce point (where z, the height, is closest to 0)
        bounce_idx = np.argmin([pos[2] for pos in ball_positions])
        bounce_x, bounce_y = self.project_3d_to_2d(ball_positions[bounce_idx][0], 
                                                   ball_positions[bounce_idx][1], 
                                                   ball_positions[bounce_idx][2])
        bounce_point = {"x": bounce_x, "y": bounce_y}

        # Detect post-bounce peak height (maximum z after bounce)
        post_bounce_positions = [pos for pos in ball_positions[bounce_idx:] if pos[2] > 0]
        if post_bounce_positions:
            peak_idx = np.argmax([pos[2] for pos in post_bounce_positions])
            peak_x, peak_y = self.project_3d_to_2d(post_bounce_positions[peak_idx][0], 
                                                  post_bounce_positions[peak_idx][1], 
                                                  post_bounce_positions[peak_idx][2])
            peak_point = {"x": peak_x, "y": peak_y}
        else:
            peak_point = None

        # Impact point is the last position (near stumps)
        impact_x, impact_y = self.project_3d_to_2d(ball_positions[-1][0], 
                                                  ball_positions[-1][1], 
                                                  ball_positions[-1][2])
        impact_point = {"x": impact_x, "y": impact_y}

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
        
        # 3. POST-BOUNCE PEAK MARKER (Blue circle)
        if peak_point:
            cv2.circle(frame, 
                      (peak_point["x"], peak_point["y"]), 
                      6,  # Radius
                      (255, 0, 0),  # Blue
                      -1)  # Filled
        
        # 4. IMPACT MARKER (Red ring)
        cv2.circle(frame, 
                  (impact_point["x"], impact_point["y"]), 
                  10,  # Radius
                  (0, 0, 255),  # Red
                  2)  # Thickness
        
        # 5. DECISION OVERLAY (Last 20% frames only)
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

    def _generate_realistic_ball_path(self, num_frames):
        """
        Generate a realistic cricket ball path for a good length delivery
        Args:
            num_frames: Length of trajectory in frames
        Returns:
            List of [x, y, z] positions simulating a ball path with bounce and slight swing
        """
        # Coordinate system:
        # - x: lateral movement (negative = leg side, positive = off side)
        # - y: distance along pitch (0 at stumps, 20m at bowler)
        # - z: height above ground (0 on pitch, positive upward)

        # Pitch length: 20m, mapped to 720 pixels (y=0 at stumps, y=720 at bowler)
        y = np.linspace(20, 0, num_frames)  # From bowler (20m) to stumps (0m)

        # Lateral movement (x): Start straight, slight outswing toward off-stump after bounce
        bounce_y = 12  # Bounce at 12m from stumps
        x = np.zeros(num_frames)
        for i in range(num_frames):
            if y[i] < bounce_y:
                # After bounce, swing toward off-stump (positive x)
                swing = 0.05 * (bounce_y - y[i])  # Up to 1m swing
                x[i] = swing
            else:
                x[i] = 0  # Straight before bounce

        # Height (z): Start at 2m (bowler's release), drop to 0 at bounce, rise to 0.5m
        z = np.zeros(num_frames)
        for i in range(num_frames):
            if y[i] > bounce_y:
                # Before bounce: linear descent from 2m to 0
                z[i] = 2 * (y[i] / 20)
            else:
                # After bounce: rise to 0.5m then drop to 0 at stumps
                z[i] = 0.5 * np.sin(np.pi * (bounce_y - y[i]) / bounce_y)

        return [[x[i], y[i], z[i]] for i in range(num_frames)]

def main():
    """Entry point for standalone testing with mock data"""
    try:
        processor = StreamOverlay()

        # Mock data for testing
        num_frames = 100
        # Use realistic ball path
        ball_positions = processor._generate_realistic_ball_path(num_frames)
        decision_data = {"decision": "OUT", "pitching_zone": "SHORT"}  # Adjusted to reflect later bounce

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