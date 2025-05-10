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
import base64
import io
import tempfile

def project_3d_to_2d(x, y, z, frame_width=1280, frame_height=720):
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

def stream_analysis(frames, ball_positions, decision_data):
    """
    Process frames to add overlays for ball trajectory, markers, and decision, and return as a video
    Args:
        frames: List of frame dictionaries from Module 1, each containing 'frameData' (base64 JPEG)
        ball_positions: List of dictionaries from Module 2, each containing ball_trajectory
        decision_data: Decision from Module 5 (either string or dict with 'Out' and 'Reason')
    Returns:
        Base64-encoded video string (result.mp4)
    """
    # Decode frames from base64
    processed_frames = []
    for frame_dict in frames:
        # Decode base64 frame data
        frame_data = base64.b64decode(frame_dict["frameData"])
        # Convert to numpy array
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode frame data")
        processed_frames.append(frame)

    # Set up output directory structure for temporary storage
    output_dir = Path("output/augmented_frames")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Frame counter for naming
    frame_count = 0
    total_frames = len(processed_frames)
    accumulated_positions = []  # Store positions across frames

    # Estimate the range of y from Module 2 data to map to 0-20m
    y_values = [pos["ball_trajectory"]["current_position"]["y"] for pos in ball_positions]
    y_min, y_max = min(y_values), max(y_values)
    if y_max == y_min:  # Avoid division by zero
        y_max = y_min + 1

    # Process each frame
    for frame_idx, (frame, position_data) in enumerate(zip(processed_frames, ball_positions)):
        # Extract current position from Module 2 output
        current_pos = position_data["ball_trajectory"]["current_position"]
        x, y, z = current_pos["x"], current_pos["y"], current_pos["z"]

        # Map y from Module 2's range to 0-20m (stumps to bowler)
        y_mapped = 20 * (y_max - y) / (y_max - y_min)  # Inverse mapping since y decreases

        # Add mapped position to accumulated positions
        accumulated_positions.append([x, y_mapped, z])

        # Use all positions up to this frame for trajectory
        positions = accumulated_positions

        # Standardize frame to HD resolution (1280x720) for broadcast compatibility
        frame = cv2.resize(frame, (1280, 720))

        # Project 3D ball positions to 2D screen coordinates
        projected_positions = []
        for pos in positions:
            x_2d, y_2d = project_3d_to_2d(pos[0], pos[1], pos[2])
            projected_positions.append([x_2d, y_2d])

        # Detect bounce point (where z, the height, is closest to 0)
        bounce_idx = np.argmin([pos[2] for pos in positions])
        bounce_x, bounce_y = project_3d_to_2d(positions[bounce_idx][0], 
                                              positions[bounce_idx][1], 
                                              positions[bounce_idx][2])
        bounce_point = {"x": bounce_x, "y": bounce_y}

        # Detect post-bounce peak height (maximum z after bounce)
        post_bounce_positions = [pos for pos in positions[bounce_idx:] if pos[2] > 0]
        if post_bounce_positions:
            peak_idx = np.argmax([pos[2] for pos in post_bounce_positions])
            peak_x, peak_y = project_3d_to_2d(post_bounce_positions[peak_idx][0], 
                                             post_bounce_positions[peak_idx][1], 
                                             post_bounce_positions[peak_idx][2])
            peak_point = {"x": peak_x, "y": peak_y}
        else:
            peak_point = None

        # Impact point is the last position (near stumps)
        impact_x, impact_y = project_3d_to_2d(positions[-1][0], 
                                             positions[-1][1], 
                                             positions[-1][2])
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
        if frame_count > 0.8 * total_frames:
            # Black background box for decision
            cv2.rectangle(frame, 
                         (1000, 20),  # Top-left
                         (1200, 100),  # Bottom-right (extended for reason)
                         (0, 0, 0),  # Black
                         -1)  # Filled
            
            # Handle decision_data format
            if isinstance(decision_data, dict) and "Out" in decision_data and "Reason" in decision_data:
                # Expected Module 5 format
                out = decision_data["Out"]
                reason = decision_data["Reason"]
            else:
                # Current dummy format in main.py
                out = decision_data == "dummy_decision"  # Treat as "Out" for testing
                reason = "Out" if out else "Not Out"

            # Decision text (red=OUT, green=NOT OUT)
            color = (0, 0, 255) if out else (0, 255, 0)
            cv2.putText(frame, 
                       "OUT" if out else "NOT OUT", 
                       (1010, 50),  # Position
                       cv2.FONT_HERSHEY_DUPLEX,  # Professional font
                       1.0,  # Font scale
                       color, 
                       2)  # Thickness
            
            # Reason text (below decision)
            cv2.putText(frame, 
                       reason, 
                       (1010, 80),  # Position
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5,  # Font scale
                       (255, 255, 255),  # White
                       1)  # Thickness
        
        # Save frame temporarily (optional, for debugging)
        output_path = output_dir / f"frame_{frame_count:04d}.png"
        cv2.imwrite(str(output_path), frame)
        processed_frames[frame_idx] = frame  # Update the frame in the list
        frame_count += 1

    # Create a temporary video file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_video_path = temp_file.name
        # Initialize video writer (30 fps, 1280x720 resolution)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_video_path, fourcc, 30.0, (1280, 720))
        
        # Write processed frames to video
        for frame in processed_frames:
            out.write(frame)
        out.release()

        # Read the video file and encode as base64
        with open(temp_video_path, "rb") as vf:
            encoded_video = base64.b64encode(vf.read()).decode("utf-8")

    # Clean up temporary video file
    import os
    os.unlink(temp_video_path)

    return encoded_video

def main(frames, ball_positions, decision_data):
    """
    Main function for Module 6: Stream Analysis and Overlay
    Args:
        frames: List of frame dictionaries from Module 1, each containing 'frameData'
        ball_positions: List of dictionaries from Module 2, each containing ball_trajectory
        decision_data: Decision from Module 5 (either string or dict with 'Out' and 'Reason')
    Returns:
        Base64-encoded video string
    """
    try:
        result_video = stream_analysis(frames, ball_positions, decision_data)
        return result_video
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Troubleshooting:")
        print("1. Verify input frames and ball positions are valid")
        print("2. Check output directory permissions")
        raise