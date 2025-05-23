import json
from pathlib import Path
import sys
from typing import Tuple
import numpy as np

def extract_ball_positions(frames):
    positions = []
    for f in frames:
        bt = f.get("ball_trajectory")
        if not bt:
            continue
        cp = bt.get("current_position")
        if not cp:
            continue
        if all(k in cp for k in ("x", "y", "z")):
            positions.append((f["frame_id"], cp["x"], cp["y"], cp["z"]))
    return positions

def find_lowest_y_before(frames, end_frame_id):
    lowest = None
    lowest_frame = None
    for f in frames:
        frame_id = f.get("frame_id")
        if frame_id is None or frame_id >= end_frame_id:
            continue
        bt = f.get("ball_trajectory")
        if not bt or not bt.get("current_position"):
            continue
        y = bt["current_position"]["y"]
        if lowest is None or y < lowest:
            lowest = y
            lowest_frame = frame_id
    return lowest_frame


from typing import Tuple
import numpy as np


def estimate_spin_rate_between_frames(frames, bounce_frame_id, hit_frame_id):

    try:

        relevant_frames = [
            f
            for f in frames
            if bounce_frame_id <= f.get("frame_id", -1) <= hit_frame_id
        ]
        if not relevant_frames:
            raise ValueError("No frames found in the given ID range.")

        relevant_frames.sort(key=lambda x: x["frame_id"])

        positions = []
        timestamps = []

        for frame in relevant_frames:
            traj = frame.get("ball_trajectory", {})
            current_pos = traj.get("current_position")
            if current_pos:
                x, y, z = (
                    current_pos.get("x"),
                    current_pos.get("y"),
                    current_pos.get("z"),
                )
                if x is not None and y is not None and z is not None:
                    positions.append([x, y, z])
                    timestamps.append(frame.get("timestamp"))
                else:
                    print(
                        f"Incomplete position data in frame {frame['frame_id']}. Skipping."
                    )
            else:
                print(f"No trajectory in frame {frame['frame_id']}. Skipping.")

        if len(positions) < 3:
            raise ValueError("Not enough valid position data to estimate spin.")

        positions = np.array(positions)

        v = np.gradient(positions, axis=0)  # First derivative -> velocity
        a = np.gradient(v, axis=0)  # second derivative -> acceleration
        mid_index = len(positions) // 2

        velocity = v[mid_index]
        acceleration = a[mid_index]

        magnus_force_direction = np.cross(velocity, acceleration)
        norm = np.linalg.norm(magnus_force_direction)
        if norm == 0:
            raise ValueError("Spin axis undefined due to zero magnus force direction.")

        spin_axis = magnus_force_direction / (norm + 1e-8)
        spin_rate = float(norm)

        spin_along_axis = spin_axis * spin_rate

        return {
            "rate": spin_rate,
            "axis_x": spin_along_axis[0],
            "axis_y": spin_along_axis[1],
            "axis_z": spin_along_axis[2],
        }

    except Exception as e:
        print(f"Error estimating spin rate: {e}")
        return {
            "rate": 0,
            "axis_x": 0.0,
            "axis_y": 0.0,
            "axis_z": 0.0,
        }


def find_first_z_drop(frames):
    prev_z = None
    for idx, f in enumerate(frames):
        bt = f.get("ball_trajectory")
        if not bt or not bt.get("current_position"):
            continue
        z = bt["current_position"]["z"]
        if prev_z is not None and z < prev_z:
            return frames[idx]["frame_id"] - 1
        prev_z = z
    return None

def compute_average_spin_and_axis_between(frames, start_frame_id, end_frame_id):
   
    total_rate = 0
    total_axis_x = 0
    total_axis_y = 0
    total_axis_z = 0
    count = 0

    for f in frames:
        frame_id = f.get("frame_id")
        if frame_id is None or not (start_frame_id <= frame_id < end_frame_id):
            continue
        try:
            spin = f["ball_trajectory"]["spin"]
            rate = spin["rate"]
            axis = spin["axis"]
            if not all(isinstance(val, (int, float)) for val in [rate, axis["x"], axis["y"], axis["z"]]):
                continue
            total_rate += rate
            total_axis_x += axis["x"]
            total_axis_y += axis["y"]
            total_axis_z += axis["z"]
            count += 1
        except (KeyError, TypeError):
            continue

    if count == 0:
        return None

    return {
        "rate": total_rate / count,
        "axis_x": total_axis_x / count,
        "axis_y": total_axis_y / count,
        "axis_z": total_axis_z / count,
    }


def extrapolate_trajectory(
    initial_position,
    velocity,
    acceleration,
    spin_axis,
    spin_rate,
    steps=30,
    dt=1/30
):
    pos = initial_position.copy()
    vel = velocity.copy()
    acc = acceleration.copy()
    result = []

    magnus_coefficient = 0.0005  # tweak for realism

    for _ in range(steps):
        # Magnus force (simplified cross product spin x velocity)
        magnus_force = {
            'x': magnus_coefficient * spin_rate * (spin_axis['y'] * vel['z'] - spin_axis['z'] * vel['y']),
            'y': magnus_coefficient * spin_rate * (spin_axis['z'] * vel['x'] - spin_axis['x'] * vel['z']),
            'z': magnus_coefficient * spin_rate * (spin_axis['x'] * vel['y'] - spin_axis['y'] * vel['x']),
        }

        # Update velocity
        vel['x'] += (acc['x'] + magnus_force['x']) * dt
        vel['y'] += (acc['y'] + magnus_force['y']) * dt
        vel['z'] += (acc['z'] + magnus_force['z']) * dt

        # Update position
        pos['x'] += vel['x'] * dt + 0.5 * acc['x'] * dt**2
        pos['y'] += vel['y'] * dt + 0.5 * acc['y'] * dt**2
        pos['z'] += vel['z'] * dt + 0.5 * acc['z'] * dt**2

        result.append({'x': pos['x'], 'y': pos['y'], 'z': pos['z']})

    return result

def did_hit_stumps(trajectory, stumps_bbox, ball_radius=0.07):

    st_x, st_y, st_w, st_h = stumps_bbox
    st_right = st_x + st_w
    st_bottom = st_y + st_h

    for pos in trajectory:
        x, y = pos['x'], pos['y']

        # Check if center of ball (plus radius) intersects with stumps area
        if (st_x - ball_radius) <= x <= (st_right + ball_radius) and \
           (st_y - ball_radius) <= y <= (st_bottom + ball_radius):
            return True, pos

    return False, None



# def main():
#     path = Path(__file__).parent / "module2_output.json"
#     if not path.exists():
#         print(f"Error: file not found at {path}", file=sys.stderr)
#         sys.exit(1)
#     text = path.read_text()
#     if not text.strip():
#         print(f"Error: {path} is empty", file=sys.stderr)
#         sys.exit(1)
#     try:
#         data = json.loads(text)
#     except json.JSONDecodeError as e:
#         print(f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}", file=sys.stderr)
#         sys.exit(1)
#     coords = extract_ball_positions(data)
#     for frame_id, x, y, z in coords:
#         print(frame_id, x, y, z)
#     drop_frame = find_first_z_drop(data)
#     if drop_frame is not None:
#         print(f"First Z drop before frame: {drop_frame}")

#     bounce_frame = find_lowest_y_before(data, drop_frame)
#     if bounce_frame is not None:
#         print(f"Bounce point frame: {bounce_frame}")
#     else:
#         print("No valid frames before z-drop to compute bounce point.")

#     if bounce_frame is not None and drop_frame is not None:
#         spin_stats = compute_average_spin_and_axis_between(data, 35, 60)

#         # Testing by rei
#         spin_stats_t = estimate_spin_rate_between_frames(data, 35, 60);
#         print(spin_stats)
#         print(spin_stats_t)
#         # if spin_stats:
#         #     # print(f"Average spin rate between bounce and z-drop: {spin_stats['rate']:.2f} rpm")
#         #     print(f"Average spin axis: x = {spin_stats['axis_x']:.4f}, y = {spin_stats['axis_y']:.4f}, z = {spin_stats['axis_z']:.4f}")
#         # else:
#         #     print(f"No valid spin data between frames {bounce_frame} and {drop_frame}.")

#     # Set constant average velocity and acceleration (approximation for realism)
#     # avg_velocity = {'x': 0.0, 'y': -17.0, 'z': 1.5}  # meters/second
#     # avg_acceleration = {'x': 0.0, 'y': -9.8, 'z': 0.0}  # only gravity

#     # Get last known position from z-drop frame
#     z_frame = next((f for f in data if f["frame_id"] == drop_frame), None)
#     if z_frame:
#         start_pos = z_frame["ball_trajectory"]["current_position"]
#         vel = z_frame["ball_trajectory"]["velocity"]
#         acc = z_frame["ball_trajectory"]["acceleration"]

#         # Use previously computed average spin axis/rate
#         spin_axis = {
#             'x': spin_stats['axis_x'],
#             'y': spin_stats['axis_y'],
#             'z': spin_stats['axis_z']
#         }
#         spin_rate = spin_stats['rate']

#         # Simulate
#         future_positions = extrapolate_trajectory(
#             initial_position=start_pos,
#             velocity=vel,
#             acceleration=acc,
#             spin_axis=spin_axis,
#             spin_rate=spin_rate,
#             steps=30
#         )

#         for i, pos in enumerate(future_positions):
#             print(f"Step {i+1}: x={pos['x']:.2f}, y={pos['y']:.2f}, z={pos['z']:.2f}")
#     # Assume this is your stumps bbox (in meters or same units as ball trajectory)
#     # You may need to convert pixel bbox to meters if your trajectory is in meters
#     stumps_bbox = [0.75, -0.25, 0.3, 0.8]  # x, y, width, height

#     hit, position = did_hit_stumps(future_positions, stumps_bbox)

#     if hit:
#         print(f"Ball hit the stumps at position: x={position['x']:.2f}, y={position['y']:.2f}, z={position['z']:.2f}")
#     else:
#         print("Ball did not hit the stumps.")


# if __name__ == "__main__":
#     main()
def run_analysis(json_path: str) -> Tuple[list[dict[str, float]], bool]:
    frames = json.loads(Path(json_path).read_text())

    coords = extract_ball_positions(frames)
    #for frame_id, x, y, z in coords:
        #print(frame_id, x, y, z)

    drop_frame = find_first_z_drop(frames)
    #print(f"First Z drop before frame: {drop_frame}") if drop_frame is not None else None

    bounce_frame = find_lowest_y_before(frames, drop_frame) if drop_frame is not None else None
    #print(f"Bounce point frame: {bounce_frame}") if bounce_frame is not None else None

    # Estimate spin (optional parameters hardcoded or could be dynamic)
    spin_stats = compute_average_spin_and_axis_between(frames, bounce_frame, drop_frame) if bounce_frame and drop_frame else None

    z_frame = next((f for f in frames if f.get("frame_id") == drop_frame), None)
    if not z_frame:
        raise ValueError("Z-drop frame data missing.")

    init_pos = z_frame["ball_trajectory"]["current_position"]
    vel = z_frame["ball_trajectory"]["velocity"]
    acc = z_frame["ball_trajectory"]["acceleration"]
    if spin_stats:
        axis = {'x': spin_stats['axis_x'], 'y': spin_stats['axis_y'], 'z': spin_stats['axis_z']}
        rate = spin_stats['rate']
    else:
        spin = z_frame["ball_trajectory"]["spin"]
        axis = spin["axis"]
        rate = spin["rate"]

    trajectory = extrapolate_trajectory(init_pos, vel, acc, axis, rate)
    stumps_bbox = [0.75, -0.25, 0.3, 0.8]
    hit, _ = did_hit_stumps(trajectory, stumps_bbox)

    return trajectory, hit

def almost_equal(a, b, tol=1e-6):
    return abs(a - b) <= tol

def test_extrapolate_straight_line():
    print("=== test_extrapolate_straight_line ===")
    init_pos = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    vel      = {'x': 1.0, 'y': 0.0, 'z': 0.0}
    acc      = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    spin_ax  = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    spin_rt  = 0.0

    traj = extrapolate_trajectory(init_pos, vel, acc, spin_ax, spin_rt, steps=5, dt=0.1)
    print("Trajectory:", traj)

    success = True
    for i, pos in enumerate(traj, start=1):
        expected_x = i * 0.1
        if not almost_equal(pos['x'], expected_x) or not almost_equal(pos['y'],0) or not almost_equal(pos['z'],0):
            success = False
            print(f"  ✗ step {i}: got {pos}, expected x≈{expected_x}, y=0, z=0")
    print("PASS\n" if success else "FAIL\n")

def test_extrapolate_constant_acceleration():
    """
    With zero initial velocity and constant acceleration along z of 2 m/s²,
    semi-implicit Euler integration with dt=0.5 yields z ≈ [0.75, 2.0, 3.75, 6.0].
    """
    init_pos = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    vel      = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    acc      = {'x': 0.0, 'y': 0.0, 'z': 2.0}
    spin_ax  = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    spin_rt  = 0.0

    steps = 4
    dt = 0.5
    traj = extrapolate_trajectory(init_pos, vel, acc, spin_ax, spin_rt, steps, dt)
    print("Trajectory:", traj)

    expected_zs = [0.75, 2.0, 3.75, 6.0]
    success = True

    for i, (pos, expected_z) in enumerate(zip(traj, expected_zs), start=1):
        if not almost_equal(pos['z'], expected_z):
            success = False
            print(f"  ✗ step {i}: got z={pos['z']}, expected {expected_z}")
    print("PASS\n" if success else "FAIL\n")


def test_extrapolate_with_spin_magnus_effect():
    print("=== test_extrapolate_with_spin_magnus_effect ===")
    init_pos = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    vel      = {'x': 10.0, 'y': 0.0, 'z': 0.0}
    acc      = {'x': 0.0, 'y': 0.0, 'z': 0.0}
    spin_ax  = {'x': 0.0, 'y': 0.0, 'z': 1.0}
    spin_rt  = 50.0

    traj = extrapolate_trajectory(init_pos, vel, acc, spin_ax, spin_rt, steps=20, dt=1/60.0)
    print("Trajectory (last 5 steps):", traj[-5:])

    final_y = traj[-1]['y']
    if final_y > 0:
        print(f"PASS (final y = {final_y:.6f} > 0)\n")
    else:
        print(f"FAIL (final y = {final_y:.6f} ≤ 0)\n")

if __name__ == "__main__":
    test_extrapolate_straight_line()
    test_extrapolate_constant_acceleration()
    test_extrapolate_with_spin_magnus_effect()
