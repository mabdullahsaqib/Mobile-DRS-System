# from fastapi import APIRouter
# from modules.trajectory_analysis.models.frame_models import TrajectoryData
# from modules.trajectory_analysis.controllers.frame_controller import process_frame

# router = APIRouter()

# @router.get("/")
# def hello():
#     return "helloWorld"

# @router.get("/process_frame")
# def trajectory_analysis_status(frameData: TrajectoryData):
#     return process_frame(frameData)


from fastapi import APIRouter, HTTPException, Body
from modules.trajectory_analysis.models.frame_models import TrajectoryData
from modules.trajectory_analysis.models.frame_models import TrajectoryResult
from modules.trajectory_analysis.controllers.frame_controller import process_frame

router = APIRouter()

@router.post(
    "/process_frame",
    response_model=TrajectoryResult,
    summary="Run trajectory analysis on one frame"
)
async def process_frame_endpoint(
    frame: TrajectoryData = Body(..., description="Frame + ball data")
) -> TrajectoryResult:
    try:
        return process_frame(frame)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
