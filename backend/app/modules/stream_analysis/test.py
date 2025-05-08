import cv2
import os
from pathlib import Path

def compile_video():
    frame_dir = Path("output/augmented_frames")
    output_dir = Path("output/output_videos")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    frames = sorted(frame_dir.glob("frame_*.png"))
    if not frames:
        raise FileNotFoundError(f"No frames found in {frame_dir}")
    
    # Get frame size from first image
    sample = cv2.imread(str(frames[0]))
    height, width, _ = sample.shape
    
    # Create video writer (MP4 with H.264 codec)
    output_path = output_dir / "output.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'avc1' for H.264 on some systems
    video = cv2.VideoWriter(str(output_path), fourcc, 30.0, (width, height))
    
    if not video.isOpened():
        raise RuntimeError("Failed to create video writer")
    
    # Add frames with progress tracking
    for i, frame_file in enumerate(frames):
        frame = cv2.imread(str(frame_file))
        if frame is not None:
            video.write(frame)
        print(f"Added frame {i+1}/{len(frames)}", end='\r')
    
    video.release()
    print(f"\nVideo saved to {output_path} (Duration: {len(frames)/30:.1f} sec)")

if __name__ == "__main__":
    compile_video()
