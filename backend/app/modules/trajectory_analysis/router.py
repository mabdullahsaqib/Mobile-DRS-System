from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def trajectory_analysis_status():
    return {"message": "Trajectory Analysis module is active"}
