from modules.trajectory_analysis.models.frame_models import TrajectoryData


def process_frame(frame: TrajectoryData):
    print(f"Processing frame {frame.frame_id}")
    return {"message": "Frame processed"}
