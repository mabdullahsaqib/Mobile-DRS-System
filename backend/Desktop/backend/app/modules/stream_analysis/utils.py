"""Enhanced Utility Functions"""
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TrackingData:
    ball_positions: list
    bounce_point: dict
    impact_point: dict
    decision_data: Optional[dict] = None

def load_tracking_data(json_path: Path) -> TrackingData:
    """Load and validate tracking data"""
    with open(json_path) as f:
        data = json.load(f)
    
    validate_data(data)
    return TrackingData(
        ball_positions=data["ball_positions"],
        bounce_point=data["bounce_point"],
        impact_point=data["impact_point"],
        decision_data=data.get("decision_data")
    )

def validate_data(data: Dict[str, Any]):
    """Enhanced validation with type checking"""
    required = {
        "ball_positions": list,
        "bounce_point": dict,
        "impact_point": dict
    }
    
    for field, field_type in required.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], field_type):
            raise TypeError(f"Field {field} must be {field_type.__name__}")
        
        # Additional validation for coordinate points
        if field in ["bounce_point", "impact_point"]:
            if not all(k in data[field] for k in ["x", "y"]):
                raise ValueError(f"{field} must contain x and y coordinates")
