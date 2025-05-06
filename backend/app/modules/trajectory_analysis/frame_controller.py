from datetime import datetime, timezone
import json
import os
from typing import Any, List, Tuple
from frame_stumps import StumpTracker
from Input_model import (
    FrameInput,
    Position3D,
    StumpDetection,
    Velocity3D,
    Spin,
)
from Output_model import (
    TrajectoryAnalysisResult,
    PredictedPoint,
    SwingCharacteristics,
)
from physics import detect_bounce, detect_bounce_kinematic


def compute_trajectory(
    position: Position3D, velocity: Velocity3D, spin: Spin
) -> list[PredictedPoint]:
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
            z=position.z + velocity.z * t - 0.5 * 9.8 * t * t,
        )
        new_velocity = Velocity3D(x=velocity.x, y=velocity.y, z=velocity.z - 9.8 * t)
        points.append(
            PredictedPoint(time_offset=t, position=new_position, velocity=new_velocity)
        )
    return points


def get_ball_positions(raw_ball: Any) -> List[List[float]]:
    ball_positions: List[List[float]] = []

    for obj in raw_ball:
        ball_traj = obj["ball_trajectory"]
        if not ball_traj:
            continue
        ball_pos = ball_traj["current_position"]
        ball_positions.append([ball_pos["x"], ball_pos["y"], ball_pos["z"]])

    return ball_positions


def get_stump_positions(frames: List[FrameInput]) -> List[List[StumpDetection]]:
    all_stump_positions: List[List[StumpDetection]] = []
    for frame in frames:
        stumps = frame.detections.stumps
        if len(stumps) == 3:
            all_stump_positions.append(stumps)

    return all_stump_positions


def get_ball_vel_acc(
    raw_ball: Any,
) -> Tuple[List[List[float]], List[List[float]]]:
    vel: List[List[float]] = []
    accel: List[List[float]] = []

    for obj in raw_ball:
        ball_traj = obj["ball_trajectory"]
        if not ball_traj:
            continue
        ball_vel=ball_traj["velocity"]
        ball_accel=ball_traj["acceleration"]
        if not ball_vel or not ball_accel:
            continue
        vel.append([ball_vel["x"], ball_vel["y"], ball_vel["z"]])
        accel.append([ball_accel["x"], ball_accel["y"], ball_accel["z"]])
        
    return (vel, accel)


def estimate_spin() -> Spin:
    return Spin(rate=30.0, axis=Position3D(x=0.0, y=0.0, z=1.0))


stump_tracker = StumpTracker(jitter_threshold=3)


def process_frame(frame: List[FrameInput]) -> TrajectoryAnalysisResult:
    # position, velocity = estimate_position_and_velocity(frame)
    spin = estimate_spin()
    ball_positions = get_ball_positions(frame)
    vel, accel = get_ball_vel_acc(frame)
    # After getting bounce point, now we will predict the trajectory up till the stump positions
    bounce_pos = detect_bounce(ball_positions)
    if bounce_pos == None:
        # No bounce point found, probably a full toss
        pass
    bounce_vel_idx = detect_bounce_kinematic(vel, accel, min_acc_spike=15.0)
    if bounce_vel_idx == None:
        pass

    # TODO : predict trajectory from bounce point up till stump positions or player (idk)
    predicted_trajectory = compute_trajectory(position, velocity, spin)  # type:ignore
    stump_pos: List[List[StumpDetection]] = get_stump_positions(frames=frame)
    stump_tracker.update(stump_pos)

    # the output model needs to be updated
    return TrajectoryAnalysisResult(
        frame_id=1212,  # Just some dummp value
        match_id="match123",
        processing_timestamp=datetime.now(timezone.utc),
        predicted_trajectory=predicted_trajectory,
        impact_location=predicted_trajectory[-1].position,
        bounce_point=ball_positions[bounce_pos],  # type: ignore
        swing_characteristics=SwingCharacteristics(
            spin_rate=spin.rate,
            spin_axis=spin.axis,
            drag_coefficient=0.45,
            bounce_coefficient=0.6,
        ),
        stumps_hit=stumps_hit,  # type: ignore
        decision_confidence=0.88,
        notes=["Trajectory and spin are estimated based on dummy logic."],
    )
