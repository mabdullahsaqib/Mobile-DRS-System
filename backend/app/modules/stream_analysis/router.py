from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def stream_analysis_status():
    return {"message": "Stream Analysis module is active"}
