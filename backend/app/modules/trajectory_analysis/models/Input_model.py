from pydantic import BaseModel
from typing import List

class Point2D(BaseModel):
    x: int
    y: int

class StumpDetection(BaseModel):
    bbox: List[int]          
    confidence: float
    top: List[int]           
    bottom: List[int]        

class BallDetection(BaseModel):
    bbox: List[int]
    confidence: float
    
class Detections(BaseModel):
    ball: List[BallDetection]
    stumps: List[StumpDetection]
    
class FrameInput(BaseModel):
    frame_id: int
    timestamp: float
    detections: Detections
