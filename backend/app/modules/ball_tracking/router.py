from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def ball_tracking_status():
    return {"message": "ball tracking module is active"}
