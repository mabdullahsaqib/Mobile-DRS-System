from .models import FrameDetection
from .overlay import process_frame
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from .utils import combine_frames_to_video

router = APIRouter()

# Define bounding box structure
class DetectionBox(BaseModel):
    bbox: List[int]
    confidence: float
    top: List[int]
    bottom: List[int]

# Structure for detections in each frame
class Detections(BaseModel):
    ball: List[DetectionBox]
    stumps: List[DetectionBox]

# Structure for a single frame with detections
class FrameDetection(BaseModel):
    frame_id: int
    timestamp: float
    detections: Detections

# Response model
class StreamAnalysisOutput(BaseModel):
    message: str  # Just a placeholder response for now

@router.post("/analyze_stream", response_model=StreamAnalysisOutput)
async def analyze_stream(frames: List[FrameDetection]):
    try:
        processed_frames = []  # To store processed frames

        for frame in frames:
            # Process each frame (perform overlay or detection)
            processed_frame = process_frame(frame)
            processed_frames.append(processed_frame)  # Add the processed frame to the list

        # After processing all frames, combine them into a video
        combine_frames_to_video(processed_frames, "output_video.mp4")

        return StreamAnalysisOutput(message="Frames processed and video created successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing frames: {str(e)}")
