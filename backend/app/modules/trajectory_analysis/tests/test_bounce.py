import json, os
from typing import List

script_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(script_dir, ".."))

data_dir = os.path.join(project_root, "data")

data_file_path = os.path.join(data_dir, "ball_data.json")


def process_ball_data(frames):
    ball_positions = []
    timestamps = []

    for frame in frames:
        detections = frame.get("detections", {})
        ball_detections = detections.get("ball", [])

        if ball_detections:
            ball = ball_detections[0]
            center = ball.get("center")
            timestamp = frame.get("timestamp")

            if center and timestamp is not None:
                ball_positions.append(center)
                timestamps.append(timestamp)

    return ball_positions, timestamps


def visualize_positions(ball_positions, timestamps):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    x_coords = [pos[0] for pos in ball_positions]
    y_coords = [pos[1] for pos in ball_positions]



    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(y_coords, x_coords, label="Ball Trajectory", color="blue")
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.set_zlabel("Z Position")  # type: ignore

    ax.invert_xaxis()

    ax.set_title("2D Ball Trajectory in 3D Space")
    ax.legend()
    plt.show()


with open(data_file_path, "r") as file:
    frames = json.load(file)
    ball_positions, time_stamps = process_ball_data(frames)
    visualize_positions(ball_positions, time_stamps)
