from pydantic import BaseModel
from typing import List

class Position3D(BaseModel):
    x: float
    y: float
    z: float

class Velocity3D(BaseModel):
    x: float
    y: float
    z: float

class Spin(BaseModel):
    axis: Position3D
    rate: float


class HistoricalPosition(Position3D):
    timestamp: str


class BallData(BaseModel):
    current_position: Position3D
    velocity: Velocity3D
    spin: Spin
    historical_positions: List[HistoricalPosition]


class TrajectoryData(BaseModel):
    frame_id: int
    timestamp: str
    delivery_id: str
    match_id: str
    edge_detected: bool
    ball_data: BallData
