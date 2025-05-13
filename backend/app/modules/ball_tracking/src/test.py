import cv2
import base64
import json
import os
import sys

# import the pipeline function
from main import ball_tracking

def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video file: {video_path}")

    frames = []
    frame_id = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Encode to JPEG
        ret2, buf = cv2.imencode('.jpg', frame)
        if not ret2:
            frame_id += 1
            continue
        b64_str = base64.b64encode(buf.tobytes()).decode('utf-8')

        # Dummy metadata (replace with real tracking/camera data if available)
        camera_position = {"x": 0.0, "y": 0.0, "z": 0.0}
        camera_rotation = {"x": 0.0, "y": 0.0, "z": 0.0}

        frames.append({
            "frameId": frame_id,
            "frameData": b64_str,
            "audioData": "",  # no audio per-frame extraction
            "cameraPosition": camera_position,
            "cameraRotation": camera_rotation
        })
        frame_id += 1

    cap.release()
    return frames

if __name__ == '__main__':
    video_path = "../assests/v2.mp4"
    input_json = "../inputs/input.json"
    output_json = "../outputs/output.json"

    # ensure directories exist
    os.makedirs(os.path.dirname(input_json), exist_ok=True)
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    # # extract frames and write input JSON
    # results = extract_frames(video_path)
    # with open(input_json, 'w') as f:
    #     json.dump({"results": results}, f, indent=2)
    # print(f"Wrote {len(results)} frames to {input_json}")

    # run the ball tracking pipeline
    ball_tracking(input_json, output_json)
    print(f"Pipeline completed. Output written to {output_json}")
    