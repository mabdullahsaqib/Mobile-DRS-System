"""Enhanced Utility Functions"""
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
import cv2
import numpy as np
from typing import Dict, Any, Optional


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

@dataclass
class TrackingData:
    ball_positions: list
    bounce_point: dict
    impact_point: dict
    decision_data: Optional[dict] = None

def load_tracking_data(json_path: Path) -> TrackingData:
    """Load and validate tracking data"""
    with open(json_path) as f:
        data = json.load(f)
    
    validate_data(data)
    return TrackingData(
        ball_positions=data["ball_positions"],
        bounce_point=data["bounce_point"],
        impact_point=data["impact_point"],
        decision_data=data.get("decision_data")
    )

def validate_data(data: Dict[str, Any]):
    """Enhanced validation with type checking"""
    required = {
        "ball_positions": list,
        "bounce_point": dict,
        "impact_point": dict
    }
    
    for field, field_type in required.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], field_type):
            raise TypeError(f"Field {field} must be {field_type.__name__}")
        
        # Additional validation for coordinate points
        if field in ["bounce_point", "impact_point"]:
            if not all(k in data[field] for k in ["x", "y"]):
                raise ValueError(f"{field} must contain x and y coordinates")