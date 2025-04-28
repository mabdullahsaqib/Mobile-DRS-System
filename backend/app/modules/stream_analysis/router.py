
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from .overlay import process_frame
from .utils import combine_frames_to_video
import base64

router = APIRouter()

class FrameData(BaseModel):
    frame_id: int
    timestamp: str
    data: str
    resolution: List[int]
    camera_position: List[float]
    pitch_yaw_roll: List[float]
    audio_id: str
    audio_data: str

class TrajectoryData(BaseModel):
    predicted_path: List[List[float]]  
    decision_text: str  # OUT/NOT OUT decision text

class StreamAnalysisInput(BaseModel):
    original_frames: List[FrameData]
    predicted_path: TrajectoryData
    will_hit_stumps: bool
    is_out: bool

class StreamAnalysisOutput(BaseModel):
    augmented_stream: str  # Base64 encoded video stream with overlays
    decision_overlay: str

@router.post("/analyze_stream", response_model=StreamAnalysisOutput)
async def analyze_stream(input_data: StreamAnalysisInput):
    try:
        # Process each frame (camera 1, camera 2)
        frames_with_overlay = []
        for frame in input_data.original_frames:
            # Process each frame and overlay trajectory and decision text
            frame_with_overlay = process_frame(frame, input_data.predicted_path.predicted_path, input_data.is_out)
            frames_with_overlay.append(frame_with_overlay)
        
        # Combine frames into a video and return the final base64-encoded video
        final_video_b64 = combine_frames_to_video(frames_with_overlay)
        decision_overlay = "OUT" if input_data.is_out else "NOT OUT"
        
        return StreamAnalysisOutput(
            augmented_stream=final_video_b64,
            decision_overlay=decision_overlay
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing stream: {str(e)}")