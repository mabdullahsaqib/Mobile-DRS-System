from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Position(BaseModel):
    x: float
    y: float
    z: float

class Velocity(BaseModel):
    x: float
    y: float
    z: float

class Spin(BaseModel):
    axis: Position
    rate: float

class HistoricalPosition(Position):
    timestamp: datetime

class BallData(BaseModel):
    current_position: Position
    velocity: Velocity
    spin: Spin
    historical_positions: List[HistoricalPosition]
    confidence: float

class BatPosition(BaseModel):
    handle: Position
    edge: Position
    tip: Position

class Orientation(BaseModel):
    pitch: float
    yaw: float
    roll: float

class BatData(BaseModel):
    position: BatPosition
    orientation: Orientation
    velocity: Velocity
    confidence: float

class AudioData(BaseModel):
    audio_id: str
    data: str  # Base64-encoded audio string

class Metadata(BaseModel):
    frame_id: int
    timestamp: datetime
    delivery_id: str
    match_id: str

class EdgeDetectionInput(BaseModel):
    metadata: Metadata
    ball_data: BallData
    bat_data: BatData
    audio_data: Optional[AudioData]
