from pydantic import BaseModel, Field
from typing import Tuple

class FramePayload(BaseModel):
    frame_id: int = Field(..., description="Unique sequential ID for the frame")
    timestamp: str = Field(..., description="ISO 8601 formatted time of frame capture")
    image_data: str = Field(..., description="Base64-encoded JPEG/PNG image data")
    resolution: Tuple[int, int] = Field(..., description="Width and height of the resolution")
    camera_position: Tuple[float, float, float] = Field(
        ..., description="X, Y, Z position of the camera after calibration"
    )