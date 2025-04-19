from fastapi import APIRouter
from modules.trajectory_analysis.models.frame_models import TrajectoryData
from modules.trajectory_analysis.controllers.frame_controller import process_frame

router = APIRouter()

@router.get("/")
def hello():
    return "helloWorld"

@router.get("/process_frame")
def trajectory_analysis_status(frameData: TrajectoryData):
    return process_frame(frameData)
