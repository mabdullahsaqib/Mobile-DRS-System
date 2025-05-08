from typing import List
from Input_model import FrameInput
from Output_model import TrajectoryAnalysisResult
from modules.trajectory_analysis.frame_controller import process_frame


def analyze_trajectory(
    frame: List[FrameInput]
) -> TrajectoryAnalysisResult:
    return process_frame(frame)
