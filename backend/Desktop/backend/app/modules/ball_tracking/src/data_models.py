#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Models Module

This module defines the data structures and models used throughout the Ball Tracking Module,
ensuring consistent data representation and validation.

Team Member Responsibilities:
----------------------------
Member 1: Data model design, validation, and documentation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Optional
import json

@dataclass
class TrackingData:
    """
    Represents metadata about tracking information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 1: Implementation and documentation of this data model
    """
    frame_id: int
    timestamp: str
    processing_timestamp: str
    delivery_id: Optional[str] = None
    match_id: Optional[str] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "processing_timestamp": self.processing_timestamp,
            "delivery_id": self.delivery_id,
            "match_id": self.match_id,
            "confidence_score": self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackingData':
        """Create from dictionary representation."""
        return cls(
            frame_id=data.get("frame_id", 0),
            timestamp=data.get("timestamp", ""),
            processing_timestamp=data.get("processing_timestamp", ""),
            delivery_id=data.get("delivery_id"),
            match_id=data.get("match_id"),
            confidence_score=data.get("confidence_score", 0.0)
        )

@dataclass
class Vector3D:
    """
    Represents a 3D vector with x, y, z components.
    
    Team Member Responsibilities:
    ----------------------------
    Member 1: Implementation and documentation of this data model
    """
    x: float
    y: float
    z: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vector3D':
        """Create from dictionary representation."""
        return cls(
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            z=float(data.get("z", 0.0))
        )

@dataclass
class HistoricalPosition:
    """
    Represents a historical position of the ball.
    
    Team Member Responsibilities:
    ----------------------------
    Member 1: Implementation and documentation of this data model
    """
    frame_id: int
    position: Vector3D
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "frame_id": self.frame_id,
            "position": self.position.to_dict(),
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalPosition':
        """Create from dictionary representation."""
        return cls(
            frame_id=data.get("frame_id", 0),
            position=Vector3D.from_dict(data.get("position", {})),
            timestamp=data.get("timestamp", "")
        )

@dataclass
class Spin:
    """
    Represents ball spin information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    axis: Vector3D
    rate: float  # revolutions per minute
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "axis": self.axis.to_dict(),
            "rate": self.rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Spin':
        """Create from dictionary representation."""
        return cls(
            axis=Vector3D.from_dict(data.get("axis", {})),
            rate=float(data.get("rate", 0.0))
        )

@dataclass
class BallTrajectory:
    """
    Represents ball trajectory information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    current_position: Vector3D
    velocity: Vector3D
    acceleration: Vector3D
    spin: Spin
    detection_confidence: float
    historical_positions: List[HistoricalPosition] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "current_position": self.current_position.to_dict(),
            "velocity": self.velocity.to_dict(),
            "acceleration": self.acceleration.to_dict(),
            "spin": self.spin.to_dict(),
            "detection_confidence": self.detection_confidence,
            "historical_positions": [pos.to_dict() for pos in self.historical_positions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BallTrajectory':
        """Create from dictionary representation."""
        return cls(
            current_position=Vector3D.from_dict(data.get("current_position", {})),
            velocity=Vector3D.from_dict(data.get("velocity", {})),
            acceleration=Vector3D.from_dict(data.get("acceleration", {})),
            spin=Spin.from_dict(data.get("spin", {})),
            detection_confidence=float(data.get("detection_confidence", 0.0)),
            historical_positions=[
                HistoricalPosition.from_dict(pos) for pos in data.get("historical_positions", [])
            ]
        )

@dataclass
class LegPosition:
    """
    Represents batsman's leg positions.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    left_foot: Vector3D
    right_foot: Vector3D
    left_knee: Vector3D
    right_knee: Vector3D
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "left_foot": self.left_foot.to_dict(),
            "right_foot": self.right_foot.to_dict(),
            "left_knee": self.left_knee.to_dict(),
            "right_knee": self.right_knee.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LegPosition':
        """Create from dictionary representation."""
        return cls(
            left_foot=Vector3D.from_dict(data.get("left_foot", {})),
            right_foot=Vector3D.from_dict(data.get("right_foot", {})),
            left_knee=Vector3D.from_dict(data.get("left_knee", {})),
            right_knee=Vector3D.from_dict(data.get("right_knee", {}))
        )

@dataclass
class Orientation:
    """
    Represents orientation in 3D space using Euler angles.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    pitch: float  # degrees
    yaw: float    # degrees
    roll: float   # degrees
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation."""
        return {
            "pitch": self.pitch,
            "yaw": self.yaw,
            "roll": self.roll
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Orientation':
        """Create from dictionary representation."""
        return cls(
            pitch=float(data.get("pitch", 0.0)),
            yaw=float(data.get("yaw", 0.0)),
            roll=float(data.get("roll", 0.0))
        )

@dataclass
class BatsmanData:
    """
    Represents batsman position and pose information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    position: Vector3D
    leg_position: LegPosition
    stance: str  # "right-handed" or "left-handed"
    body_orientation: Orientation
    detection_confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "position": self.position.to_dict(),
            "leg_position": self.leg_position.to_dict(),
            "stance": self.stance,
            "body_orientation": self.body_orientation.to_dict(),
            "detection_confidence": self.detection_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatsmanData':
        """Create from dictionary representation."""
        return cls(
            position=Vector3D.from_dict(data.get("position", {})),
            leg_position=LegPosition.from_dict(data.get("leg_position", {})),
            stance=data.get("stance", "right-handed"),
            body_orientation=Orientation.from_dict(data.get("body_orientation", {})),
            detection_confidence=float(data.get("detection_confidence", 0.0))
        )

@dataclass
class BatPosition:
    """
    Represents bat position information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    handle: Vector3D
    middle: Vector3D
    edge: Vector3D
    tip: Vector3D
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "handle": self.handle.to_dict(),
            "middle": self.middle.to_dict(),
            "edge": self.edge.to_dict(),
            "tip": self.tip.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatPosition':
        """Create from dictionary representation."""
        return cls(
            handle=Vector3D.from_dict(data.get("handle", {})),
            middle=Vector3D.from_dict(data.get("middle", {})),
            edge=Vector3D.from_dict(data.get("edge", {})),
            tip=Vector3D.from_dict(data.get("tip", {}))
        )

@dataclass
class BatData:
    """
    Represents bat position, orientation, and movement information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    position: BatPosition
    orientation: Orientation
    velocity: Vector3D
    detection_confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "position": self.position.to_dict(),
            "orientation": self.orientation.to_dict(),
            "velocity": self.velocity.to_dict(),
            "detection_confidence": self.detection_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatData':
        """Create from dictionary representation."""
        return cls(
            position=BatPosition.from_dict(data.get("position", {})),
            orientation=Orientation.from_dict(data.get("orientation", {})),
            velocity=Vector3D.from_dict(data.get("velocity", {})),
            detection_confidence=float(data.get("detection_confidence", 0.0))
        )

@dataclass
class StumpPosition:
    """
    Represents the position of a single stump.
    
    Team Member Responsibilities:
    ----------------------------
    Member 5: Implementation and documentation of this data model
    """
    id: str  # "leg", "middle", or "off"
    top_position: Vector3D
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "top_position": self.top_position.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StumpPosition':
        """Create from dictionary representation."""
        return cls(
            id=data.get("id", ""),
            top_position=Vector3D.from_dict(data.get("top_position", {}))
        )

@dataclass
class BailPosition:
    """
    Represents the position and status of a bail.
    
    Team Member Responsibilities:
    ----------------------------
    Member 5: Implementation and documentation of this data model
    """
    id: str  # "leg_bail" or "off_bail"
    position: Vector3D
    is_dislodged: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "position": self.position.to_dict(),
            "is_dislodged": self.is_dislodged
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BailPosition':
        """Create from dictionary representation."""
        return cls(
            id=data.get("id", ""),
            position=Vector3D.from_dict(data.get("position", {})),
            is_dislodged=bool(data.get("is_dislodged", False))
        )

@dataclass
class StumpsData:
    """
    Represents stumps position, orientation, and status information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 5: Implementation and documentation of this data model
    """
    position: Dict[str, Vector3D]  # Contains "base_center"
    orientation: Orientation
    individual_stumps: List[StumpPosition]
    bails: List[BailPosition]
    detection_confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "position": {k: v.to_dict() for k, v in self.position.items()},
            "orientation": self.orientation.to_dict(),
            "individual_stumps": [stump.to_dict() for stump in self.individual_stumps],
            "bails": [bail.to_dict() for bail in self.bails],
            "detection_confidence": self.detection_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StumpsData':
        """Create from dictionary representation."""
        position_dict = {}
        for k, v in data.get("position", {}).items():
            position_dict[k] = Vector3D.from_dict(v)
        
        return cls(
            position=position_dict,
            orientation=Orientation.from_dict(data.get("orientation", {})),
            individual_stumps=[
                StumpPosition.from_dict(stump) for stump in data.get("individual_stumps", [])
            ],
            bails=[
                BailPosition.from_dict(bail) for bail in data.get("bails", [])
            ],
            detection_confidence=float(data.get("detection_confidence", 0.0))
        )

@dataclass
class PitchMap:
    """
    Represents cricket pitch dimensions and position.
    
    Team Member Responsibilities:
    ----------------------------
    Member 5: Implementation and documentation of this data model
    """
    length: float  # meters
    width: float   # meters
    center: Vector3D
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "length": self.length,
            "width": self.width,
            "center": self.center.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PitchMap':
        """Create from dictionary representation."""
        return cls(
            length=float(data.get("length", 0.0)),
            width=float(data.get("width", 0.0)),
            center=Vector3D.from_dict(data.get("center", {}))
        )

@dataclass
class BouncePoint:
    """
    Represents ball bounce point information.
    
    Team Member Responsibilities:
    ----------------------------
    Member 4: Implementation and documentation of this data model
    """
    position: Vector3D
    frame_id: int
    timestamp: str
    detection_confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "position": self.position.to_dict(),
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "detection_confidence": self.detection_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BouncePoint':
        """Create from dictionary representation."""
        return cls(
            position=Vector3D.from_dict(data.get("position", {})),
            frame_id=int(data.get("frame_id", 0)),
            timestamp=data.get("timestamp", ""),
            detection_confidence=float(data.get("detection_confidence", 0.0))
        )

@dataclass
class PitchData:
    """
    Represents cricket pitch data including bounce points.
    
    Team Member Responsibilities:
    ----------------------------
    Member 5: Implementation and documentation of this data model
    """
    pitch_map: PitchMap
    bounce_point: Optional[BouncePoint] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "pitch_map": self.pitch_map.to_dict()
        }
        
        if self.bounce_point:
            result["bounce_point"] = self.bounce_point.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PitchData':
        """Create from dictionary representation."""
        bounce_point = None
        if "bounce_point" in data and data["bounce_point"]:
            bounce_point = BouncePoint.from_dict(data["bounce_point"])
        
        return cls(
            pitch_map=PitchMap.from_dict(data.get("pitch_map", {})),
            bounce_point=bounce_point
        )

@dataclass
class TrackingResult:
    """
    Represents the complete tracking result for a frame.
    
    Team Member Responsibilities:
    ----------------------------
    Member 1: Implementation and documentation of this data model
    """
    tracking_data: TrackingData
    ball_trajectory: Optional[BallTrajectory] = None
    batsman_data: Optional[BatsmanData] = None
    bat_data: Optional[BatData] = None
    stumps_data: Optional[StumpsData] = None
    pitch_data: Optional[PitchData] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "tracking_data": self.tracking_data.to_dict()
        }
        
        if self.ball_trajectory:
            result["ball_trajectory"] = self.ball_trajectory.to_dict()
        
        if self.batsman_data:
            result["batsman_data"] = self.batsman_data.to_dict()
        
        if self.bat_data:
            result["bat_data"] = self.bat_data.to_dict()
        
        if self.stumps_data:
            result["stumps_data"] = self.stumps_data.to_dict()
        
        if self.pitch_data:
            result["pitch_data"] = self.pitch_data.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackingResult':
        """Create from dictionary representation."""
        tracking_data = TrackingData.from_dict(data.get("tracking_data", {}))
        
        ball_trajectory = None
        if "ball_trajectory" in data and data["ball_trajectory"]:
            ball_trajectory = BallTrajectory.from_dict(data["ball_trajectory"])
        
        batsman_data = None
        if "batsman_data" in data and data["batsman_data"]:
            batsman_data = BatsmanData.from_dict(data["batsman_data"])
        
        bat_data = None
        if "bat_data" in data and data["bat_data"]:
            bat_data = BatData.from_dict(data["bat_data"])
        
        stumps_data = None
        if "stumps_data" in data and data["stumps_data"]:
            stumps_data = StumpsData.from_dict(data["stumps_data"])
        
        pitch_data = None
        if "pitch_data" in data and data["pitch_data"]:
            pitch_data = PitchData.from_dict(data["pitch_data"])
        
        return cls(
            tracking_data=tracking_data,
            ball_trajectory=ball_trajectory,
            batsman_data=batsman_data,
            bat_data=bat_data,
            stumps_data=stumps_data,
            pitch_data=pitch_data
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TrackingResult':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
