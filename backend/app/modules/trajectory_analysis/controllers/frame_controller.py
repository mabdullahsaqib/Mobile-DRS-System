from datetime import datetime
from modules.trajectory_analysis.models.frame_models import TrajectoryData
from modules.trajectory_analysis.models.frame_models import TrajectoryResult, TrajectoryPoint
from modules.trajectory_analysis.physics import compute_trajectory, check_stumps_hit

def process_frame(frame: TrajectoryData) -> TrajectoryResult:
    raw_path = compute_trajectory(
        current_pos=frame.ball_data.current_position,
        velocity=frame.ball_data.velocity,
        spin=frame.ball_data.spin,
        edge_detected=frame.edge_detected
    )
    
    hit = check_stumps_hit(raw_path)

    points = [TrajectoryPoint(**pt) for pt in raw_path]

    return TrajectoryResult(
        frame_id=frame.frame_id,
        match_id=frame.match_id,
        processing_timestamp=datetime.utcnow(),
        predicted_trajectory=points,
        stumps_hit=hit,
        decision_confidence=0.85,    
        notes=["Computed with drag, spin, bounce"]
    )
