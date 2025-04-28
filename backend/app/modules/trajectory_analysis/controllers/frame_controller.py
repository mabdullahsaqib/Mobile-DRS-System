
from datetime import datetime
from modules.trajectory_analysis.models.Input_model import (
    FrameInput, Position3D, Velocity3D, Spin
)
from modules.trajectory_analysis.models.Output_model import (
    TrajectoryAnalysisResult,
    PredictedPoint,
    SwingCharacteristics
)

#static controller 

def compute_trajectory(position: Position3D, velocity: Velocity3D, spin: Spin) -> list[PredictedPoint]:
    """
    Simulates a basic projectile trajectory
    """
    points = []
    time_step = 0.05
    for i in range(20):
        t = i * time_step
        new_position = Position3D(
            x=position.x + velocity.x * t,
            y=position.y + velocity.y * t,
            z=position.z + velocity.z * t - 0.5 * 9.8 * t * t  # gravity
        )
        new_velocity = Velocity3D(
            x=velocity.x,
            y=velocity.y,
            z=velocity.z - 9.8 * t
        )
        points.append(PredictedPoint(time_offset=t, position=new_position, velocity=new_velocity))
    return points

def estimate_position_and_velocity(frame: FrameInput) -> tuple[Position3D, Velocity3D]:
    return (
        Position3D(x=0.0, y=0.0, z=1.0),   # 1 meter above ground
        Velocity3D(x=20.0, y=0.0, z=2.0)   # Towards batsman
    )

def estimate_spin() -> Spin:
    return Spin(rate=30.0, axis=Position3D(x=0.0, y=0.0, z=1.0))

def process_frame(frame: FrameInput) -> TrajectoryAnalysisResult:
    position, velocity = estimate_position_and_velocity(frame)
    spin = estimate_spin()

    predicted_trajectory = compute_trajectory(position, velocity, spin)

    stumps_hit = any(p.position.x < 0.5 for p in predicted_trajectory)

    return TrajectoryAnalysisResult(
        frame_id=frame.frame_id,
        match_id="match123",  
        processing_timestamp=datetime.utcnow(),
        predicted_trajectory=predicted_trajectory,
        impact_location=predicted_trajectory[-1].position,
        bounce_point=predicted_trajectory[len(predicted_trajectory) // 2].position,
        swing_characteristics=SwingCharacteristics(
            spin_rate=spin.rate,
            spin_axis=spin.axis,
            drag_coefficient=0.45,
            bounce_coefficient=0.6
        ),
        stumps_hit=stumps_hit,
        decision_confidence=0.88,
        notes=["Trajectory and spin are estimated based on dummy logic."]
    )
