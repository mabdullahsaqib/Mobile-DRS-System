from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from .models import FrameDetection
from .overlay import process_frame, process_frame_with_decision
from .utils import combine_frames_to_video

router = APIRouter()

# Input model for decision info
class DecisionInput(BaseModel):
    isOut: bool

# Combined input model for both modules
class StreamAnalysisInput(BaseModel):
    frames: List[FrameDetection]
    decision: DecisionInput

# Response model
class StreamAnalysisOutput(BaseModel):
    message: str

@router.post("/analyze_stream", response_model=StreamAnalysisOutput)
async def analyze_stream(input_data: StreamAnalysisInput):
    try:
        processed_frames = []

        # First process all frames normally
        for frame in input_data.frames:
            processed_frame = process_frame(frame)
            processed_frames.append(processed_frame)

        # After processing frames, overlay final decision on last frame
        if processed_frames:
            # Modify the last frame with decision text overlay
            processed_frames[-1] = process_frame_with_decision(
                input_data.frames[-1], input_data.decision.isOut
            )

        # Combine into a single output video
        combine_frames_to_video(processed_frames, "output_video.mp4")

        return StreamAnalysisOutput(
            message="Frames processed and decision overlay added to final frame. Video created."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing stream: {str(e)}")
