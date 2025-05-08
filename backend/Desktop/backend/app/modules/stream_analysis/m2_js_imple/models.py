# In overlay.py and router.py



from pydantic import BaseModel
from typing import List

class DetectionBox(BaseModel):
    bbox: List[int]
    confidence: float
    top: List[int]
    bottom: List[int]

class Detections(BaseModel):
    ball: List[DetectionBox]
    stumps: List[DetectionBox]

class FrameDetection(BaseModel):
    frame_id: int
    timestamp: float
    detections: Detections
