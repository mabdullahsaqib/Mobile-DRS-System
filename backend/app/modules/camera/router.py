from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def camera_status():
    return {"message": "Camera module is active"}
