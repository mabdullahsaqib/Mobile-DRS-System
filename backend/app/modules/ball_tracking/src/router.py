from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def ball_tracking_status():
    return {"message": "Tracking module is active"}
