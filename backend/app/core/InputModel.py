from pydantic import BaseModel
from typing import List

class CameraPosition(BaseModel):
    x: float
    y: float
    z: float

class CameraRotation(BaseModel):
    x: float
    y: float
    z: float

class FrameData(BaseModel):
    frameId: int
    frameData: str  # base64-encoded JPEG
    audioData: str  # base64-encoded PCM audio (can be an empty string but must be present)
    cameraPosition: CameraPosition
    cameraRotation: CameraRotation

class VideoAnalysisInput(BaseModel):
    results: List[FrameData]
