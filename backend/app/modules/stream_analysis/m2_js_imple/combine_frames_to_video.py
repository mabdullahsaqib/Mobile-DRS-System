import cv2
import numpy as np

def combine_frames_to_video(frames: list, output_path: str, fps: int = 30):
    """Combine a list of image frames into a video."""
    if not frames:
        raise ValueError("No frames provided")

    # Get frame dimensions from the first frame
    height, width, _ = frames[0].shape

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec for mp4 format
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Write each frame to the video
    for frame in frames:
        video_writer.write(frame)

    # Release the video writer
    video_writer.release()

    print(f"Video saved to {output_path}")
