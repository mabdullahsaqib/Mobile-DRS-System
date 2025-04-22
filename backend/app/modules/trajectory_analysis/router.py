# backend/app/modules/trajectory_analysis/router.py

from fastapi import APIRouter
from backend.app.modules.trajectory_analysis.models.Output_model import (
    TrajectoryData,
    TrajectoryResult,
)
from backend.app.modules.trajectory_analysis.controllers.frame_controller import process_frame

router = APIRouter()

@router.post(
    "/trajectory",
    response_model=TrajectoryResult,
    summary="Run trajectory analysis on an incoming frame"
)
async def analyze_trajectory(
    frame: TrajectoryData   
) -> TrajectoryResult:
    return process_frame(frame)
