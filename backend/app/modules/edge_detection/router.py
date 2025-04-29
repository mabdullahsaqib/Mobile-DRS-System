from fastapi import APIRouter
from modules.edge_detection.controllers.frame_controller import detect_edge
from modules.edge_detection.models.frame_model import EdgeDetectionInput
from modules.edge_detection.controllers.audio_detection import drs_system_pipeline
router = APIRouter()

@router.get("/")
def edge_detection_status():
    return {"message": "Edge Detection module is active"}

@router.post("/detect-edge")
def edge_detection_handler(data: EdgeDetectionInput):
    result = detect_edge(data)
    audio_res=drs_system_pipeline("")#will insert filename here
    return {"edge_detected": result}
