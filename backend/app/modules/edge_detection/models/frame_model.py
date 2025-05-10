# from pydantic import BaseModel
# from typing import List, Optional
# from datetime import datetime

# class Position(BaseModel):
#     x: float
#     y: float
#     z: float

# class Velocity(BaseModel):
#     x: float
#     y: float
#     z: float

# class Acceleration(BaseModel):
#     x: float
#     y: float
#     z: float

# class Spin(BaseModel):
#     axis: Position
#     rate: float

# class BoundingBox(BaseModel):
#     x: int
#     y: int
#     width: int
#     height: int

# class BallDetection(BaseModel):
#     bbox: BoundingBox
#     confidence: float
#     center: List[int]  # [x, y] coordinates of the center
#     radius: float
#     z: float

# class StumpDetection(BaseModel):
#     bbox: BoundingBox
#     confidence: float

# class BatsmanDetection(BaseModel):
#     bbox: BoundingBox
#     confidence: float

# class BatDetection(BaseModel):
#     bbox: BoundingBox
#     confidence: float
#     z: float

# class PadsDetection(BaseModel):
#     bbox: BoundingBox
#     confidence: Optional[float] = None

# class Detections(BaseModel):
#     ball: List[BallDetection]
#     stumps: List[StumpDetection]
#     batsman: List[BatsmanDetection]
#     bat: List[BatDetection]
#     pads: List[PadsDetection]

# class BallTrajectory(BaseModel):
#     current_position: Position
#     velocity: Velocity
#     acceleration: Acceleration
#     spin: Spin
#     detection_confidence: float
#     historical_positions: List[Position]

# class Metadata(BaseModel):
#     frame_id: int
#     timestamp: float
#     delivery_id: str
#     match_id: str

# class EdgeDetectionInput(BaseModel):
#     metadata: Metadata
#     detections: Detections
#     ball_trajectory: BallTrajectory
