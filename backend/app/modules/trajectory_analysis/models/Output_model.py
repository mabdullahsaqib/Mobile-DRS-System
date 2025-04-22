
from pydantic import BaseModel
from typing import List
from datetime import datetime
from .Input_model import Position3D, Velocity3D

class PredictedPoint(BaseModel):
    time_offset: float
    position: Position3D
    velocity: Velocity3D

class SwingCharacteristics(BaseModel):
    spin_rate: float
    spin_axis: Position3D
    drag_coefficient: float
    bounce_coefficient: float

class TrajectoryAnalysisResult(BaseModel):
    frame_id: int
    match_id: str
    processing_timestamp: datetime
    predicted_trajectory: List[PredictedPoint]
    impact_location: Position3D
    bounce_point: Position3D
    swing_characteristics: SwingCharacteristics
    stumps_hit: bool
    decision_confidence: float
    notes: List[str]
