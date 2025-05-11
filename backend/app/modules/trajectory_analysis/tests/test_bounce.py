import json, os
from typing import List, Optional

from matplotlib import pyplot as plt
import numpy as np
from pydantic import ValidationError

from trajectory_analysis.Input_model import FrameInput
from trajectory_analysis.frame_controller import get_ball_positions
from physics import detect_bounce

script_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(script_dir, ".."))

data_dir = os.path.join(project_root, "data")

data_file_path = os.path.join(data_dir, "ball_data.json")


def visualize_positions(trajectory: np.ndarray, bounce_idx: Optional[int] = None):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    xs, ys, zs = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
    ax.plot(
        xs, zs, ys, label="Ball Trajectory"
    )  # note: plotted as x–z horizontal, y vertical

    if bounce_idx is not None:
        bx, bz, by = xs[bounce_idx], zs[bounce_idx], ys[bounce_idx]
        ax.scatter([bx], [bz], [by], c="red", s=50, label="Bounce Point")

    ax.set_xlabel("X (left–right)")
    ax.set_ylabel("Z (bowler→batsman)")
    ax.set_zlabel("Y (vertical)")
    ax.set_title("3D Ball Trajectory with Bounce")
    ax.legend()
    plt.show()


with open(data_file_path, "r") as file:
    raw_ball_positions = json.load(file)
    ball_positions:List[List[float]] = []
    
    for obj in raw_ball_positions:
        ball_traj = obj["ball_trajectory"]
        if not ball_traj:
            continue
        ball_pos=ball_traj["current_position"]
        ball_positions.append([ball_pos["x"],ball_pos["y"],ball_pos["z"]]);
                
    for i,frame in enumerate(ball_positions):
        print(f"i={i} x:{frame[0]} y:{frame[1]} z:{frame[1]} ")
    bounce_point = detect_bounce(ball_positions)
    visualize_positions(np.array(ball_positions))
