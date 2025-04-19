from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def edge_detection_status():
    return {"message": "Edge Detection module is active"}
