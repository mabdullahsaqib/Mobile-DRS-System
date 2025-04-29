from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import base64
from .overlay import process_frame  # Assuming this function exists in overlay.py
from .utils import combine_frames_to_video  # Assuming this function exists in utils.py

router = APIRouter()

# ===================== INPUT MODELS =====================

class FrameData(BaseModel):
    frame_id: int
    timestamp: str
    data: str  # Base64 image
    resolution: List[int] = [640, 360]  # Optional default
    camera_position: List[float] = [0, 0, 0]
    pitch_yaw_roll: List[float] = [0, 0, 0]
    audio_id: str = ""
    audio_data: str = ""

class PredictedPoint(BaseModel):
    time_offset: float
    position: dict  # Example: {'x': float, 'y': float, 'z': float}
    velocity: dict  # Example: {'vx': float, 'vy': float, 'vz': float}

class StreamAnalysisInput(BaseModel):
    original_frames: List[FrameData]
    predicted_path: List[PredictedPoint]
    will_hit_stumps: bool
    isOut: bool

# ===================== OUTPUT MODEL =====================

class StreamAnalysisOutput(BaseModel):
    augmented_stream: str
    decision_overlay: str

# ===================== ENDPOINT =====================

@router.post("/analyze_stream", response_model=StreamAnalysisOutput)
async def analyze_stream(input_data: StreamAnalysisInput):
    try:
        frames_with_overlay = []

        for i, frame in enumerate(input_data.original_frames):
            img_data = base64.b64decode(frame.data)
            
            # Properly iterate over the predicted_path list and pass it to process_frame
            frame_with_overlay = process_frame(img_data, input_data.predicted_path, input_data.isOut)
            frames_with_overlay.append(frame_with_overlay)

        video_b64 = combine_frames_to_video(frames_with_overlay)
        decision_overlay = "OUT" if input_data.isOut else "NOT OUT"

        return StreamAnalysisOutput(
            augmented_stream=video_b64,
            decision_overlay=decision_overlay
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream processing error: {str(e)}")
