from pydantic import BaseModel
from typing import List


class Config:
    extra = "ignore"
    
class Position3D(BaseModel):
    x: float
    y: float
    z: float

class Velocity3D(BaseModel):
    x: float
    y: float
    z: float

class Spin(BaseModel):
    rate: float
    axis: Position3D

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
    centre:Position3D
    radius:float


class Detections(BaseModel):
    ball: List[BallDetection]
    stumps: List[StumpDetection]

class FrameInput(BaseModel):
    frame_id: int
    timestamp: float
    detections: Detections
