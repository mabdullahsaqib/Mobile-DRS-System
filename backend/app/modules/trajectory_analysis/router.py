from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def trajectory_analysis_status():
    return {"message": "Trajectory module is active"}
