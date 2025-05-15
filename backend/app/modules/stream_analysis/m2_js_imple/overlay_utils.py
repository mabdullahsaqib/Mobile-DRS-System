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
    processed_frames = []
    for frame_dict in frames:
        frame_data = base64.b64decode(frame_dict["frameData"])
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode frame data")
        processed_frames.append(frame)

    output_dir = Path("output/augmented_frames")
    output_dir.mkdir(exist_ok=True, parents=True)

    frame_count = 0
    total_frames = len(processed_frames)
    accumulated_positions = []

    y_values = [pos["ball_trajectory"]["current_position"]["y"] for pos in ball_positions]
    y_min, y_max = min(y_values), max(y_values)
    if y_max == y_min:
        y_max = y_min + 1

    for frame_idx, (frame, position_data) in enumerate(zip(processed_frames, ball_positions)):
        current_pos = position_data["ball_trajectory"]["current_position"]
        x, y, z = current_pos["x"], current_pos["y"], current_pos["z"]
        y_mapped = 20 * (y_max - y) / (y_max - y_min)
        accumulated_positions.append([x, y_mapped, z])

        positions = accumulated_positions
        frame = cv2.resize(frame, (1280, 720))
        projected_positions = []
        for pos in positions:
            x_2d, y_2d = project_3d_to_2d(pos[0], pos[1], pos[2])
            projected_positions.append([x_2d, y_2d])

        bounce_idx = np.argmin([pos[2] for pos in positions])
        bounce_x, bounce_y = project_3d_to_2d(positions[bounce_idx][0], positions[bounce_idx][1], positions[bounce_idx][2])
        bounce_point = {"x": bounce_x, "y": bounce_y}

        post_bounce_positions = [pos for pos in positions[bounce_idx:] if pos[2] > 0]
        if post_bounce_positions:
            peak_idx = np.argmax([pos[2] for pos in post_bounce_positions])
            peak_x, peak_y = project_3d_to_2d(post_bounce_positions[peak_idx][0], post_bounce_positions[peak_idx][1], post_bounce_positions[peak_idx][2])
            peak_point = {"x": peak_x, "y": peak_y}
        else:
            peak_point = None

        impact_x, impact_y = project_3d_to_2d(positions[-1][0], positions[-1][1], positions[-1][2])
        impact_point = {"x": impact_x, "y": impact_y}

        if len(projected_positions) > 1:
            for i in range(1, len(projected_positions)):
                cv2.line(frame, tuple(projected_positions[i-1]), tuple(projected_positions[i]), (0, 255, 0), 2, cv2.LINE_AA)

        cv2.circle(frame, (bounce_point["x"], bounce_point["y"]), 8, (0, 255, 255), -1)
        if peak_point:
            cv2.circle(frame, (peak_point["x"], peak_point["y"]), 6, (255, 0, 0), -1)
        cv2.circle(frame, (impact_point["x"], impact_point["y"]), 10, (0, 0, 255), 2)

        if frame_count > 0.8 * total_frames:
            cv2.rectangle(frame, (1000, 20), (1200, 100), (0, 0, 0), -1)
            out = decision_data == "dummy_decision"
            reason = "Out" if out else "Not Out"
            color = (0, 0, 255) if out else (0, 255, 0)
            cv2.putText(frame, "OUT" if out else "NOT OUT", (1010, 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2)
            cv2.putText(frame, reason, (1010, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        output_path = output_dir / f"frame_{frame_count:04d}.png"
        cv2.imwrite(str(output_path), frame)
        print(f"Saving frame: {frame_count+1}/{total_frames} to {output_path}")  # Log for debugging
        processed_frames[frame_idx] = frame
        frame_count += 1

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_video_path = temp_file.name
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_video_path, fourcc, 30.0, (1280, 720))
        for frame in processed_frames:
            out.write(frame)
        out.release()

        with open(temp_video_path, "rb") as vf:
            encoded_video = base64.b64encode(vf.read()).decode("utf-8")

    import os
    os.unlink(temp_video_path)

    return encoded_video
