import cv2
import numpy as np
from pathlib import Path
import base64
import io
import json
import tempfile
import os

def project_3d_to_2d(x, y, z, frame_width=1280, frame_height=720):
    y_2d = int((y / 20) * frame_height)
    x_2d = int(frame_width / 2 + x * 50)
    return x_2d, y_2d

def stream_analysis(frames, ball_positions, decision_data):
    
    print(f"[INFO] Type of ball posiitons:", type(ball_positions))
    
    frames = frames["results"]
    processed_frames = []
    for frame in frames:
        frame_data = frame["frameData"]
        if frame_data is None:
            continue
        
        frame_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        decoded = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if decoded is None:
            raise ValueError("Failed to decode frame data")

        processed_frames.append(decoded)

    output_dir = Path(__file__).parent / "output/augmented_frames"
    output_dir.mkdir(exist_ok=True, parents=True)

    frame_count = 0
    total_frames = len(processed_frames)
    accumulated_positions = []

    y_values = []
    last_position = {"x": 0, "y": 0, "z": 0}  # Default to (0, 0, 0) for the first frame

    for pos in ball_positions:
        try:
            if "ball_trajectory" in pos and pos["ball_trajectory"] and "current_position" in pos["ball_trajectory"]:
                current_position = pos["ball_trajectory"]["current_position"]
            else:
                current_position = last_position  # Use the last saved position if trajectory is empty

            y_value = current_position["y"]
            y_values.append(y_value)
            last_position = current_position  # Update the last saved position
        except (KeyError, TypeError):
            continue

    if not y_values:
        raise ValueError("No valid y-coordinates found in ball position data")
    
    y_min, y_max = min(y_values), max(y_values)
    
    if y_max == y_min:
        y_max = y_min + 1

    last_position = {"x": 0, "y": 0, "z": 0}
    for frame_idx, (frame, position_data) in enumerate(zip(processed_frames, ball_positions)):
        try:
            if "ball_trajectory" in position_data and position_data["ball_trajectory"] and "current_position" in position_data["ball_trajectory"]:
                current_pos = position_data["ball_trajectory"]["current_position"]
            else:
                current_pos = last_position  # Use the last saved position if trajectory is empty

            x, y, z = current_pos["x"], current_pos["y"], current_pos["z"]
            y_mapped = 20 * (y_max - y) / (y_max - y_min)
            accumulated_positions.append([x, y_mapped, z])
            last_position = current_pos  # Update the last saved position
        except (KeyError, TypeError):
            continue
        y_mapped = 20 * (y_max - y) / (y_max - y_min)
        accumulated_positions.append([x, y_mapped, z])
        positions = accumulated_positions

        frame = cv2.resize(frame, (1280, 720))

        projected_positions = []
        for pos in positions:
            x_2d, y_2d = project_3d_to_2d(pos[0], pos[1], pos[2])
            projected_positions.append([x_2d, y_2d])

        bounce_idx = np.argmin([pos[2] for pos in positions])
        bounce_x, bounce_y = project_3d_to_2d(*positions[bounce_idx])
        bounce_point = {"x": bounce_x, "y": bounce_y}

        post_bounce_positions = [pos for pos in positions[bounce_idx:] if pos[2] > 0]
        if post_bounce_positions:
            peak_idx = np.argmax([pos[2] for pos in post_bounce_positions])
            peak_x, peak_y = project_3d_to_2d(*post_bounce_positions[peak_idx])
            peak_point = {"x": peak_x, "y": peak_y}
        else:
            peak_point = None

        impact_x, impact_y = project_3d_to_2d(*positions[-1])
        impact_point = {"x": impact_x, "y": impact_y}

        if len(projected_positions) > 1:
            for i in range(1, len(projected_positions)):
                cv2.line(frame,
                         tuple(projected_positions[i - 1]),
                         tuple(projected_positions[i]),
                         (0, 255, 0), 2, cv2.LINE_AA)

        cv2.circle(frame, (bounce_point["x"], bounce_point["y"]), 8, (0, 255, 255), -1)
        if peak_point:
            cv2.circle(frame, (peak_point["x"], peak_point["y"]), 6, (255, 0, 0), -1)
        cv2.circle(frame, (impact_point["x"], impact_point["y"]), 10, (0, 0, 255), 2)

        if frame_count > 0.8 * total_frames:
            cv2.rectangle(frame, (1000, 20), (1200, 100), (0, 0, 0), -1)
            if isinstance(decision_data, dict) and "Out" in decision_data and "Reason" in decision_data:
                out = decision_data["Out"]
                reason = decision_data["Reason"]
            else:
                out = decision_data == "dummy_decision"
                reason = "Out" if out else "Not Out"

            color = (0, 0, 255) if out else (0, 255, 0)
            cv2.putText(frame, "OUT" if out else "NOT OUT", (1010, 50),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2)
            cv2.putText(frame, reason, (1010, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        output_path = output_dir / f"frame_{frame_count:04d}.png"
        if not cv2.imwrite(str(output_path), frame):
            print(f"Failed to write frame to {output_path}")
        processed_frames[frame_idx] = frame
        frame_count += 1

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_video_path = temp_file.name
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(temp_video_path, fourcc, 30.0, (1280, 720))

        # Log the number of frames being written
        print(f"[DEBUG] Total frames to write: {len(processed_frames)}")

        for idx, frame in enumerate(processed_frames):
            # Log the dimensions of each frame
            print(f"[DEBUG] Writing frame {idx + 1}/{len(processed_frames)} with dimensions: {frame.shape}")
            out.write(frame)
        out.release()

        # Log the size of the video file before encoding
        print(f"[DEBUG] Temporary video file size: {os.path.getsize(temp_video_path)} bytes")

        with open(temp_video_path, "rb") as vf:
            encoded_video = base64.b64encode(vf.read()).decode("utf-8")

        # Log the length of the base64 string
        print(f"[DEBUG] Encoded video base64 length: {len(encoded_video)} characters")

    os.unlink(temp_video_path)

    return encoded_video

def augmented_stream(frames_path, ball_positions, decision_data):
    try:
        with open(frames_path, "r") as f:
            frames = json.load(f)

        print(f"[INFO] Loaded {len(frames)} frames from {frames_path}")

        if not frames:
            raise ValueError("No frames found in the input data")

        # Call the stream_analysis function
        return stream_analysis(frames, ball_positions, decision_data)

    except Exception as e:
        print(f"[ERROR] stream_analysis failed: {e}")
        print("Hints:")
        print("- Check for missing fields in frames")
        print("- Make sure ball_positions has 'ball_trajectory'")
        raise
