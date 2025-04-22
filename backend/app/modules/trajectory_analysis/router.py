from fastapi import APIRouter
from backend.app.modules.trajectory_analysis.models.Input_model import FrameInput
from backend.app.modules.trajectory_analysis.models.Output_model import TrajectoryAnalysisResult
from backend.app.modules.trajectory_analysis.controllers.frame_controller import process_frame

router = APIRouter()

@router.post(
    "/trajectory",
    response_model=TrajectoryAnalysisResult,
    summary="Run trajectory analysis on an incoming frame"
)
async def analyze_trajectory(
    frame: FrameInput
) -> TrajectoryAnalysisResult:
    return process_frame(frame)
